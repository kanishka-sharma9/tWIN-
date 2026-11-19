from types import TracebackType
from typing import Self
from uuid import UUID

from twin.domain.email import Email
from twin.domain.vault import CurrentVault, EmailTaken, Folder, User, Vault


class MemoryStore:
    """What survives between transactions."""

    def __init__(self) -> None:
        self.users: list[User] = []
        self.vaults: list[Vault] = []
        self.folders: list[Folder] = []


class MemoryUserRepository:
    def __init__(self, store: MemoryStore, pending: MemoryStore) -> None:
        self._store, self._pending = store, pending

    def add(self, user: User) -> None:
        if self.get_by_email(user.email) is not None:
            raise EmailTaken("taken")
        self._pending.users.append(user)

    def get_by_email(self, email: Email) -> User | None:
        for user in [*self._store.users, *self._pending.users]:
            if user.email.key == email.key:
                return user
        return None


class MemoryVaultRepository:
    def __init__(self, store: MemoryStore, pending: MemoryStore) -> None:
        self._store, self._pending = store, pending

    def add(self, vault: Vault, root: Folder) -> None:
        self._pending.vaults.append(vault)
        self._pending.folders.append(root)

    def get_current(self, owner_id: UUID) -> CurrentVault | None:
        for vault in self._store.vaults:
            if vault.owner_id == owner_id:
                root = next(
                    f
                    for f in self._store.folders
                    if f.vault_id == vault.id and f.parent_id is None
                )
                return CurrentVault(vault.id, owner_id, root.id)
        return None

    def get_folder(self, vault_id: UUID, folder_id: UUID) -> Folder | None:
        for folder in self._store.folders:
            if folder.id == folder_id and folder.vault_id == vault_id:
                return folder
        return None


class MemoryUnitOfWork:
    """In-memory fake of the `UnitOfWork` port: nothing is stored until `commit()`."""

    def __init__(self, store: MemoryStore) -> None:
        self._store = store
        self._pending = MemoryStore()
        self.users = MemoryUserRepository(store, self._pending)
        self.vaults = MemoryVaultRepository(store, self._pending)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._clear()

    def commit(self) -> None:
        self._store.users.extend(self._pending.users)
        self._store.vaults.extend(self._pending.vaults)
        self._store.folders.extend(self._pending.folders)
        self._clear()

    def _clear(self) -> None:
        self._pending.users.clear()
        self._pending.vaults.clear()
        self._pending.folders.clear()
