from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.fakes.clock import FixedClock

from twin.adapters.persistence.accounts import (
    SqlFolderRepository,
    SqlUnitOfWork,
    SqlUserRepository,
    SqlVaultRepository,
)
from twin.application.create_user import CreateUser, NewAccount
from twin.domain.accounts import EmailTaken, Folder, User, Vault


def create_user(session: Session, email: str) -> NewAccount:
    return CreateUser(
        SqlUserRepository(session),
        SqlVaultRepository(session),
        SqlFolderRepository(session),
        SqlUnitOfWork(session),
        FixedClock(),
    )(email)


def test_new_user_has_one_vault_with_a_root_folder(db_session: Session) -> None:
    account = create_user(db_session, "ada@example.com")
    assert SqlUserRepository(db_session).get(account.user.id) == account.user
    assert SqlVaultRepository(db_session).get_by_owner(account.user.id) == account.vault
    assert SqlFolderRepository(db_session).get_root(account.vault.id) == account.root
    assert db_session.scalar(text("SELECT count(*) FROM vaults")) == 1


def test_database_refuses_emails_differing_only_by_case(db_session: Session) -> None:
    create_user(db_session, "ada@example.com")
    with pytest.raises(EmailTaken):
        SqlUserRepository(db_session).add(
            User(id=uuid4(), email="ADA@Example.com", created_at=FixedClock().now())
        )


def test_a_user_cannot_have_two_vaults(db_session: Session) -> None:
    account = create_user(db_session, "ada@example.com")
    with pytest.raises(IntegrityError):
        SqlVaultRepository(db_session).add(
            Vault(id=uuid4(), owner_id=account.user.id, created_at=FixedClock().now())
        )


def test_a_vault_cannot_have_two_roots(db_session: Session) -> None:
    account = create_user(db_session, "ada@example.com")
    with pytest.raises(IntegrityError):
        SqlFolderRepository(db_session).add(
            Folder(
                id=uuid4(),
                vault_id=account.vault.id,
                parent_id=None,
                name="Another",
                created_at=FixedClock().now(),
            )
        )


def test_folder_reads_are_scoped_to_the_vault(db_session: Session) -> None:
    ada = create_user(db_session, "ada@example.com")
    bob = create_user(db_session, "bob@example.com")
    folders = SqlFolderRepository(db_session)
    assert folders.get(ada.vault.id, ada.root.id) == ada.root
    assert folders.get(ada.vault.id, bob.root.id) is None
    assert folders.get(bob.vault.id, ada.root.id) is None
    assert folders.get_root(bob.vault.id) == bob.root


def test_create_user_twice_in_different_case_leaves_one_vault(
    db_session: Session,
) -> None:
    create_user(db_session, "ada@example.com")
    with pytest.raises(EmailTaken):
        create_user(db_session, "ADA@EXAMPLE.COM")
    assert db_session.scalar(text("SELECT count(*) FROM vaults")) == 1
