"""Two accounts, one app: neither can read the other vault through the current-vault dependency."""

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

import pytest
from fastapi import APIRouter, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from tests.fakes.clock import FixedClock

from twin.adapters.api.dependencies import get_current_vault, get_folder_repository
from twin.adapters.persistence.accounts import (
    SqlFolderRepository,
    SqlUnitOfWork,
    SqlUserRepository,
    SqlVaultRepository,
)
from twin.application.create_user import CreateUser, NewAccount
from twin.bootstrap import create_app
from twin.domain.accounts import Vault
from twin.settings import Settings


class HeaderAuthenticator:
    """Test stand-in for E02-S03: the Authorization header is the user id."""

    def authenticate(self, authorization: str | None) -> UUID | None:
        return UUID(authorization) if authorization else None


probe = APIRouter()


@probe.get("/probe/folders/{folder_id}")
def read_folder(
    folder_id: UUID,
    vault: Annotated[Vault, Depends(get_current_vault)],
    folders: Annotated[SqlFolderRepository, Depends(get_folder_repository)],
) -> dict[str, str]:
    folder = folders.get(vault.id, folder_id)
    if folder is None:
        raise HTTPException(404)
    return {"id": str(folder.id), "vault_id": str(folder.vault_id)}


@pytest.fixture
def probe_client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    app.state.authenticator = HeaderAuthenticator()
    app.include_router(probe)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def accounts(settings: Settings) -> Iterator[tuple[NewAccount, NewAccount]]:
    engine = create_engine(settings.database_url)
    created: list[NewAccount] = []
    with Session(engine) as session:
        create = CreateUser(
            SqlUserRepository(session),
            SqlVaultRepository(session),
            SqlFolderRepository(session),
            SqlUnitOfWork(session),
            FixedClock(),
        )
        created = [create("ada@isolation.test"), create("bob@isolation.test")]
    yield created[0], created[1]
    with engine.begin() as connection:
        ids = [str(a.user.id) for a in created]
        for table, column in (("folders", "vault_id"), ("vaults", "owner_id")):
            owners = [str(a.vault.id) for a in created] if column == "vault_id" else ids
            connection.execute(
                text(f"DELETE FROM {table} WHERE {column} = ANY(CAST(:ids AS uuid[]))"),
                {"ids": owners},
            )
        connection.execute(
            text("DELETE FROM users WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": ids},
        )
    engine.dispose()


def test_user_reads_own_root_folder(
    probe_client: TestClient, accounts: tuple[NewAccount, NewAccount]
) -> None:
    ada, _ = accounts
    response = probe_client.get(
        f"/probe/folders/{ada.root.id}", headers={"Authorization": str(ada.user.id)}
    )
    assert response.status_code == 200
    assert response.json()["vault_id"] == str(ada.vault.id)


def test_neither_user_can_read_the_other_vault(
    probe_client: TestClient, accounts: tuple[NewAccount, NewAccount]
) -> None:
    ada, bob = accounts
    as_ada = probe_client.get(
        f"/probe/folders/{bob.root.id}", headers={"Authorization": str(ada.user.id)}
    )
    as_bob = probe_client.get(
        f"/probe/folders/{ada.root.id}", headers={"Authorization": str(bob.user.id)}
    )
    assert as_ada.status_code == 404
    assert as_bob.status_code == 404


def test_anonymous_request_is_401_in_the_error_shape(
    probe_client: TestClient, accounts: tuple[NewAccount, NewAccount]
) -> None:
    ada, _ = accounts
    response = probe_client.get(f"/probe/folders/{ada.root.id}")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"


def test_account_without_a_vault_is_refused(
    probe_client: TestClient, accounts: tuple[NewAccount, NewAccount]
) -> None:
    ada, _ = accounts
    response = probe_client.get(
        f"/probe/folders/{ada.root.id}",
        headers={"Authorization": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "vault_not_found"


def test_default_app_authenticates_nobody(client: TestClient) -> None:
    app = client.app
    assert app.state.authenticator.authenticate("anything") is None  # type: ignore[attr-defined]
