from types import TracebackType
from typing import Self
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from twin.adapters.persistence.models import FolderRow, UserRow, VaultRow
from twin.domain.email import Email
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

    @property
    def users(self) -> SqlUserRepository:
        return self._users

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
