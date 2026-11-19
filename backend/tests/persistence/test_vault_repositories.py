from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from tests.fakes.clock import FixedClock

from twin.adapters.persistence.models import FolderRow, UserRow, VaultRow
from twin.adapters.persistence.repositories import (
    SqlUnitOfWork,
    SqlUserRepository,
    SqlVaultRepository,
)
from twin.application.create_user import CreateUser
from twin.domain.email import Email
from twin.domain.vault import EmailTaken, Folder, User, Vault

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def new_user(email: str) -> User:
    return User(uuid4(), Email(email), "hash", None, NOW)


def count(session: Session, table: type[UserRow | VaultRow | FolderRow]) -> int:
    return session.scalar(select(func.count()).select_from(table)) or 0


@pytest.fixture
def create_user(db_session: Session) -> CreateUser:
    """CreateUser on the real repositories, inside the test's rolled-back transaction."""
    factory = sessionmaker(
        bind=db_session.connection(), join_transaction_mode="create_savepoint"
    )
    return CreateUser(lambda: SqlUnitOfWork(factory), FixedClock())


def test_new_user_has_exactly_one_vault_with_one_root_folder(
    db_session: Session, create_user: CreateUser
) -> None:
    user = create_user.execute("ada@example.com", password_hash="hash")
    vaults = db_session.scalars(
        select(VaultRow).where(VaultRow.owner_id == user.id)
    ).all()
    assert len(vaults) == 1
    folders = db_session.scalars(
        select(FolderRow).where(FolderRow.vault_id == vaults[0].id)
    ).all()
    assert len(folders) == 1
    assert folders[0].parent_id is None


def test_email_is_unique_ignoring_case_and_the_whole_signup_is_undone(
    db_session: Session, create_user: CreateUser
) -> None:
    create_user.execute("Ada@Example.com", password_hash="hash")
    before = (count(db_session, UserRow), count(db_session, VaultRow))
    with pytest.raises(EmailTaken):
        create_user.execute("ADA@example.com", password_hash="other")
    assert (count(db_session, UserRow), count(db_session, VaultRow)) == before


def test_database_refuses_an_email_that_differs_only_in_case(
    db_session: Session,
) -> None:
    users = SqlUserRepository(db_session)
    users.add(new_user("Grace@Example.com"))
    duplicate = new_user("grace@example.com")
    with pytest.raises(EmailTaken) as raised, db_session.begin_nested():
        users.add(duplicate)
    assert raised.value.code == "email_taken"


def test_user_is_found_by_email_ignoring_case(db_session: Session) -> None:
    users = SqlUserRepository(db_session)
    user = new_user("Grace@Example.com")
    users.add(user)
    found = users.get_by_email(Email("GRACE@example.com"))
    assert found is not None
    assert found.id == user.id
    assert users.get_by_email(Email("nobody@example.com")) is None


def _vault_with_root(session: Session, email: str) -> tuple[Vault, Folder]:
    user = new_user(email)
    SqlUserRepository(session).add(user)
    vault = Vault(uuid4(), user.id, NOW)
    root = Folder(uuid4(), vault.id, None, "Home", NOW)
    SqlVaultRepository(session).add(vault, root)
    return vault, root


def _insert(session: Session, row: FolderRow | VaultRow) -> None:
    """Insert in a savepoint, so a refused row leaves the test transaction usable."""
    with session.begin_nested():
        session.add(row)
        session.flush()


def test_a_vault_has_exactly_one_root_folder(db_session: Session) -> None:
    vault, _ = _vault_with_root(db_session, "a@example.com")
    second_root = FolderRow(
        id=uuid4(), vault_id=vault.id, parent_id=None, name="Second", created_at=NOW
    )
    with pytest.raises(IntegrityError):
        _insert(db_session, second_root)


def test_a_user_owns_at_most_one_vault(db_session: Session) -> None:
    vault, _ = _vault_with_root(db_session, "a@example.com")
    second_vault = VaultRow(id=uuid4(), owner_id=vault.owner_id, created_at=NOW)
    with pytest.raises(IntegrityError):
        _insert(db_session, second_vault)


def test_a_folder_below_the_root_is_allowed(db_session: Session) -> None:
    vault, root = _vault_with_root(db_session, "a@example.com")
    db_session.add(
        FolderRow(
            id=uuid4(),
            vault_id=vault.id,
            parent_id=root.id,
            name="Docs",
            created_at=NOW,
        )
    )
    db_session.flush()


def test_folder_lookup_is_scoped_to_its_vault(db_session: Session) -> None:
    vault_a, root_a = _vault_with_root(db_session, "a@example.com")
    vault_b, _ = _vault_with_root(db_session, "b@example.com")
    vaults = SqlVaultRepository(db_session)
    found = vaults.get_folder(vault_a.id, root_a.id)
    assert found is not None
    assert found.id == root_a.id
    assert vaults.get_folder(vault_b.id, root_a.id) is None


def test_get_current_returns_the_owners_vault_and_root(db_session: Session) -> None:
    vault, root = _vault_with_root(db_session, "a@example.com")
    current = SqlVaultRepository(db_session).get_current(vault.owner_id)
    assert current is not None
    assert (current.id, current.root_folder_id) == (vault.id, root.id)
    unknown: Callable[[], UUID] = uuid4
    assert SqlVaultRepository(db_session).get_current(unknown()) is None
