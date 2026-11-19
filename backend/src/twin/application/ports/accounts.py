from typing import Protocol
from uuid import UUID

from twin.domain.accounts import Folder, User, Vault


class UserRepository(Protocol):
    def add(self, user: User) -> None:
        """Raises `EmailTaken` when the email exists in any letter case."""
        ...

    def get(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...


class VaultRepository(Protocol):
    def add(self, vault: Vault) -> None: ...

    def get_by_owner(self, owner_id: UUID) -> Vault | None: ...


class FolderRepository(Protocol):
    """Every read takes the vault id, so a query can never leave the caller vault."""

    def add(self, folder: Folder) -> None: ...

    def get(self, vault_id: UUID, folder_id: UUID) -> Folder | None: ...

    def get_root(self, vault_id: UUID) -> Folder | None: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class UserAuthenticator(Protocol):
    """Who is calling. E02-S03 implements it with tokens; None means not authenticated."""

    def authenticate(self, authorization: str | None) -> UUID | None: ...
