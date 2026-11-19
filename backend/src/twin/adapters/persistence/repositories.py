from datetime import datetime
from types import TracebackType
from typing import Self
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from twin.adapters.persistence.models import (
    FolderRow,
    RefreshTokenRow,
    UserRow,
    VaultRow,
)
from twin.domain.email import Email
from twin.domain.session import RefreshToken
from twin.domain.vault import CurrentVault, EmailTaken, Folder, User, Vault

EMAIL_INDEX = "uq_users_email_lower"


def _constraint(error: IntegrityError) -> str | None:
    diag = getattr(error.orig, "diag", None)
    name = getattr(diag, "constraint_name", None)
    return name if isinstance(name, str) else None


def _user(row: UserRow) -> User:
    return User(
        row.id, Email(row.email), row.password_hash, row.google_subject, row.created_at
    )


def _refresh_token(row: RefreshTokenRow) -> RefreshToken:
    return RefreshToken(
        row.id,
        row.user_id,
        row.token_hash,
        row.family_id,
        row.expires_at,
        row.revoked_at,
        row.replaced_by,
        row.created_at,
    )


def _folder(row: FolderRow) -> Folder:
    return Folder(row.id, row.vault_id, row.parent_id, row.name, row.created_at)


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(
            UserRow(
                id=user.id,
                email=user.email.value,
                password_hash=user.password_hash,
                google_subject=user.google_subject,
                created_at=user.created_at,
            )
        )
        try:
            self._session.flush()
        except IntegrityError as error:
            if _constraint(error) == EMAIL_INDEX:
                raise EmailTaken(
                    "An account with this email already exists.",
                    details={"field": "email"},
                ) from error
            raise

    def get_by_email(self, email: Email) -> User | None:
        row = self._session.scalar(
            select(UserRow).where(func.lower(UserRow.email) == email.key)
        )
        return _user(row) if row else None

    def get_by_id(self, user_id: UUID) -> User | None:
        row = self._session.get(UserRow, user_id)
        return _user(row) if row else None


class SqlRefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: RefreshToken) -> None:
        self._session.add(
            RefreshTokenRow(
                id=token.id,
                user_id=token.user_id,
                token_hash=token.token_hash,
                family_id=token.family_id,
                expires_at=token.expires_at,
                revoked_at=token.revoked_at,
                replaced_by=token.replaced_by,
                created_at=token.created_at,
            )
        )
        self._session.flush()

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        row = self._session.scalar(
            select(RefreshTokenRow)
            .where(RefreshTokenRow.token_hash == token_hash)
            .with_for_update()
        )
        return _refresh_token(row) if row else None

    def mark_replaced(self, token_id: UUID, replaced_by: UUID) -> None:
        self._session.execute(
            update(RefreshTokenRow)
            .where(RefreshTokenRow.id == token_id)
            .values(replaced_by=replaced_by)
        )

    def revoke_family(self, family_id: UUID, at: datetime) -> None:
        self._session.execute(
            update(RefreshTokenRow)
            .where(
                RefreshTokenRow.family_id == family_id,
                RefreshTokenRow.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )


class SqlVaultRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, vault: Vault, root: Folder) -> None:
        self._session.add(
            VaultRow(id=vault.id, owner_id=vault.owner_id, created_at=vault.created_at)
        )
        self._session.flush()
        self._session.add(
            FolderRow(
                id=root.id,
                vault_id=root.vault_id,
                parent_id=root.parent_id,
                name=root.name,
                created_at=root.created_at,
            )
        )
        self._session.flush()

    def get_current(self, owner_id: UUID) -> CurrentVault | None:
        row = self._session.execute(
            select(VaultRow.id, FolderRow.id)
            .join(FolderRow, FolderRow.vault_id == VaultRow.id)
            .where(VaultRow.owner_id == owner_id, FolderRow.parent_id.is_(None))
        ).one_or_none()
        return CurrentVault(row[0], owner_id, row[1]) if row else None

    def get_folder(self, vault_id: UUID, folder_id: UUID) -> Folder | None:
        row = self._session.scalar(
            select(FolderRow).where(
                FolderRow.id == folder_id, FolderRow.vault_id == vault_id
            )
        )
        return _folder(row) if row else None


class SqlUnitOfWork:
    """One database transaction; closing it without `commit()` rolls back."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session = session_factory()
        self._users = SqlUserRepository(self._session)
        self._vaults = SqlVaultRepository(self._session)
        self._refresh_tokens = SqlRefreshTokenRepository(self._session)

    @property
    def users(self) -> SqlUserRepository:
        return self._users

    @property
    def refresh_tokens(self) -> SqlRefreshTokenRepository:
        return self._refresh_tokens

    @property
    def vaults(self) -> SqlVaultRepository:
        return self._vaults

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._session.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()
