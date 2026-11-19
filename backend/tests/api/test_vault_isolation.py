"""No request can reach another account's vault (E02-S01).

The route below exists only in this test; real vault routes arrive with E04 and declare the
same `get_current_vault` dependency.
"""

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID, uuid4

import pytest
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker
from tests.fakes.clock import FixedClock

from twin.adapters.api.dependencies import get_current_vault, get_uow
from twin.adapters.persistence.models import FolderRow, UserRow, VaultRow
from twin.adapters.persistence.repositories import SqlUnitOfWork
from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.bootstrap import create_app
from twin.domain.vault import CurrentVault, User
from twin.settings import Settings


class BearerIsUserId:
    """Test authenticator: the header `Bearer <user id>` logs that user in."""

    def authenticate(self, authorization: str | None) -> UUID | None:
        if authorization and authorization.startswith("Bearer "):
            return UUID(authorization.removeprefix("Bearer "))
        return None


@pytest.fixture
def app_client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    app.state.authenticator = BearerIsUserId()

    @app.get("/api/_test/folders/{folder_id}")
    def folder(
        folder_id: UUID,
        vault: Annotated[CurrentVault, Depends(get_current_vault)],
        uow: Annotated[UnitOfWork, Depends(get_uow)],
    ) -> dict[str, str]:
        found = uow.vaults.get_folder(vault.id, folder_id)
        if found is None:
            raise HTTPException(status_code=404)
        return {"id": str(found.id), "vault_id": str(found.vault_id)}

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def two_users(settings: Settings) -> Iterator[tuple[User, User]]:
    """Two committed accounts, removed again afterwards."""
    engine = create_engine(settings.database_url)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    create_user = CreateUser(lambda: SqlUnitOfWork(factory), FixedClock())
    tag = uuid4().hex
    ada = create_user.execute(f"ada-{tag}@example.com", password_hash="h")
    bob = create_user.execute(f"bob-{tag}@example.com", password_hash="h")
    try:
        yield ada, bob
    finally:
        with Session(engine) as session, session.begin():
            ids = [ada.id, bob.id]
            vault_id_list = list(
                session.scalars(select(VaultRow.id).where(VaultRow.owner_id.in_(ids)))
            )
            session.execute(
                delete(FolderRow).where(FolderRow.vault_id.in_(vault_id_list))
            )
            session.execute(delete(VaultRow).where(VaultRow.owner_id.in_(ids)))
            session.execute(delete(UserRow).where(UserRow.id.in_(ids)))
        engine.dispose()


def root_of(settings: Settings, user: User) -> UUID:
    engine = create_engine(settings.database_url)
    try:
        factory = sessionmaker(bind=engine)
        with SqlUnitOfWork(factory) as uow:
            current = uow.vaults.get_current(user.id)
            assert current is not None
            return current.root_folder_id
    finally:
        engine.dispose()


def as_user(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {user.id}"}


def test_each_user_reads_their_own_root_folder(
    app_client: TestClient, settings: Settings, two_users: tuple[User, User]
) -> None:
    ada, _ = two_users
    root = root_of(settings, ada)
    response = app_client.get(f"/api/_test/folders/{root}", headers=as_user(ada))
    assert response.status_code == 200
    assert response.json()["id"] == str(root)


def test_neither_user_can_read_the_other_vault(
    app_client: TestClient, settings: Settings, two_users: tuple[User, User]
) -> None:
    ada, bob = two_users
    ada_root, bob_root = root_of(settings, ada), root_of(settings, bob)
    assert ada_root != bob_root
    as_ada = app_client.get(f"/api/_test/folders/{bob_root}", headers=as_user(ada))
    as_bob = app_client.get(f"/api/_test/folders/{ada_root}", headers=as_user(bob))
    assert as_ada.status_code == as_bob.status_code == 404
    assert str(bob_root) not in as_ada.text
    assert str(ada_root) not in as_bob.text


def test_a_vault_route_without_login_answers_401(
    app_client: TestClient, settings: Settings, two_users: tuple[User, User]
) -> None:
    root = root_of(settings, two_users[0])
    response = app_client.get(f"/api/_test/folders/{root}")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_the_default_authenticator_logs_nobody_in(
    settings: Settings, two_users: tuple[User, User]
) -> None:
    """With the app as wired (no sessions yet) even a well-formed header is refused."""
    app = create_app(settings)

    @app.get("/api/_test/whoami")
    def whoami(
        vault: Annotated[CurrentVault, Depends(get_current_vault)],
    ) -> dict[str, str]:
        return {"vault": str(vault.id)}

    with TestClient(app) as client:
        response = client.get("/api/_test/whoami", headers=as_user(two_users[0]))
    assert response.status_code == 401


def test_a_token_for_a_user_without_a_vault_is_refused(
    app_client: TestClient,
) -> None:
    ghost = {"Authorization": f"Bearer {uuid4()}"}
    response = app_client.get(f"/api/_test/folders/{uuid4()}", headers=ghost)
    assert response.status_code == 401
