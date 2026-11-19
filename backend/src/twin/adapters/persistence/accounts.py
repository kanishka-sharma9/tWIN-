from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from twin.adapters.persistence.models import FolderModel, UserModel, VaultModel
from twin.domain.accounts import EmailTaken, Folder, User, Vault


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                created_at=user.created_at,
            )
        )
        try:
            self._session.flush()
        except IntegrityError as error:
            if "uq_users_email_lower" in str(error.orig):
                raise EmailTaken(
                    "An account with this email already exists."
                ) from error
            raise

    def get(self, user_id: UUID) -> User | None:
        row = self._session.get(UserModel, user_id)
        return _user(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalars(
            select(UserModel).where(func.lower(UserModel.email) == email.lower())
        ).first()
        return _user(row) if row else None


class SqlVaultRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, vault: Vault) -> None:
        self._session.add(
            VaultModel(
                id=vault.id, owner_id=vault.owner_id, created_at=vault.created_at
            )
        )
        self._session.flush()

    def get_by_owner(self, owner_id: UUID) -> Vault | None:
        row = self._session.scalars(
            select(VaultModel).where(VaultModel.owner_id == owner_id)
        ).first()
        if row is None:
            return None
        return Vault(id=row.id, owner_id=row.owner_id, created_at=row.created_at)


class SqlFolderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, folder: Folder) -> None:
        self._session.add(
            FolderModel(
                id=folder.id,
                vault_id=folder.vault_id,
                parent_id=folder.parent_id,
                name=folder.name,
                created_at=folder.created_at,
            )
        )
        self._session.flush()

    def get(self, vault_id: UUID, folder_id: UUID) -> Folder | None:
        row = self._session.scalars(
            select(FolderModel).where(
                FolderModel.vault_id == vault_id, FolderModel.id == folder_id
            )
        ).first()
        return _folder(row) if row else None

    def get_root(self, vault_id: UUID) -> Folder | None:
        row = self._session.scalars(
            select(FolderModel).where(
                FolderModel.vault_id == vault_id, FolderModel.parent_id.is_(None)
            )
        ).first()
        return _folder(row) if row else None


class SqlUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


def _user(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        created_at=row.created_at,
        password_hash=row.password_hash,
    )


def _folder(row: FolderModel) -> Folder:
    return Folder(
        id=row.id,
        vault_id=row.vault_id,
        parent_id=row.parent_id,
        name=row.name,
        created_at=row.created_at,
    )
