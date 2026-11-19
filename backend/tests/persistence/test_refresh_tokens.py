"""The refresh-token and password-hash writes of E02-S07, on the real repositories."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from tests.fakes.clock import FixedClock

from twin.adapters.persistence.models import RefreshTokenRow, UserRow
from twin.adapters.persistence.repositories import SqlUnitOfWork
from twin.application.create_user import CreateUser
from twin.domain.session import RefreshToken
from twin.domain.vault import User

NOW = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def factory(db_session: Session) -> sessionmaker[Session]:
    return sessionmaker(
        bind=db_session.connection(), join_transaction_mode="create_savepoint"
    )


def make_user(factory: sessionmaker[Session], email: str) -> User:
    return CreateUser(lambda: SqlUnitOfWork(factory), FixedClock()).execute(
        email, password_hash="old-hash"
    )


def add_token(
    factory: sessionmaker[Session], user_id: UUID, family_id: UUID
) -> RefreshToken:
    token = RefreshToken(
        id=uuid4(),
        user_id=user_id,
        token_hash=uuid4().hex,
        family_id=family_id,
        expires_at=NOW + timedelta(days=30),
        revoked_at=None,
        replaced_by=None,
        created_at=NOW,
    )
    with SqlUnitOfWork(factory) as uow:
        uow.refresh_tokens.add(token)
        uow.commit()
    return token


def revoked(db_session: Session, token: RefreshToken) -> bool:
    row = db_session.scalar(
        select(RefreshTokenRow).where(RefreshTokenRow.id == token.id)
    )
    assert row is not None
    db_session.refresh(row)
    return row.revoked_at is not None


def test_revoke_user_families_keeps_one_family_and_other_users(
    db_session: Session, factory: sessionmaker[Session]
) -> None:
    ada = make_user(factory, "ada@example.com")
    bob = make_user(factory, "bob@example.com")
    keep, other = uuid4(), uuid4()
    kept = add_token(factory, ada.id, keep)
    kept_rotated = add_token(factory, ada.id, keep)
    gone = add_token(factory, ada.id, other)
    gone_too = add_token(factory, ada.id, uuid4())
    bobs = add_token(factory, bob.id, uuid4())
    with SqlUnitOfWork(factory) as uow:
        uow.refresh_tokens.revoke_user_families(ada.id, keep, NOW)
        uow.commit()
    assert [revoked(db_session, t) for t in (kept, kept_rotated)] == [False, False]
    assert [revoked(db_session, t) for t in (gone, gone_too)] == [True, True]
    assert revoked(db_session, bobs) is False


def test_revoke_user_families_without_an_exception_revokes_everything(
    db_session: Session, factory: sessionmaker[Session]
) -> None:
    ada = make_user(factory, "ada@example.com")
    tokens = [add_token(factory, ada.id, uuid4()) for _ in range(2)]
    with SqlUnitOfWork(factory) as uow:
        uow.refresh_tokens.revoke_user_families(ada.id, None, NOW)
        uow.commit()
    assert all(revoked(db_session, t) for t in tokens)


def test_set_password_hash_replaces_only_that_users_hash(
    db_session: Session, factory: sessionmaker[Session]
) -> None:
    ada = make_user(factory, "ada@example.com")
    bob = make_user(factory, "bob@example.com")
    with SqlUnitOfWork(factory) as uow:
        uow.users.set_password_hash(ada.id, "new-hash")
        uow.commit()
    hashes = {
        row.id: row.password_hash
        for row in db_session.scalars(
            select(UserRow).where(UserRow.id.in_([ada.id, bob.id]))
        )
    }
    assert hashes == {ada.id: "new-hash", bob.id: "old-hash"}
