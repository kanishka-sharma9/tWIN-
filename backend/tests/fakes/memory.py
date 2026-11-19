from dataclasses import replace
from datetime import datetime
from types import TracebackType
from typing import Self
from uuid import UUID

from twin.domain.email import Email
from twin.domain.session import RefreshToken
from twin.domain.vault import CurrentVault, EmailTaken, Folder, User, Vault


class MemoryStore:
    """What survives between transactions."""

    def __init__(self) -> None:
        self.users: list[User] = []
        self.vaults: list[Vault] = []
        self.folders: list[Folder] = []
        self.refresh_tokens: dict[UUID, RefreshToken] = {}
        self.password_hashes: dict[UUID, str] = {}  # changes waiting for commit


class MemoryUserRepository:
    def __init__(self, store: MemoryStore, pending: MemoryStore) -> None:
        self._store, self._pending = store, pending

    def add(self, user: User) -> None:
        if self.get_by_email(user.email) is not None:
            raise EmailTaken("taken")
        self._pending.users.append(user)

    def _with_changes(self, user: User) -> User:
        new_hash = self._pending.password_hashes.get(user.id)
        return replace(user, password_hash=new_hash) if new_hash else user

    def get_by_email(self, email: Email) -> User | None:
        for user in [*self._store.users, *self._pending.users]:
            if user.email.key == email.key:
                return self._with_changes(user)
        return None

    def get_by_id(self, user_id: UUID) -> User | None:
        for user in [*self._store.users, *self._pending.users]:
            if user.id == user_id:
                return self._with_changes(user)
        return None

    def set_password_hash(self, user_id: UUID, password_hash: str) -> None:
        self._pending.password_hashes[user_id] = password_hash

    def get_by_google_subject(self, subject: str) -> User | None:
        for user in [*self._store.users, *self._pending.users]:
            if user.google_subject == subject:
                return user
        return None


class MemoryRefreshTokenRepository:
    """Works on a copy of the stored tokens; `MemoryUnitOfWork.commit` publishes it."""

    def __init__(self, tokens: dict[UUID, RefreshToken]) -> None:
        self.tokens = tokens

    def add(self, token: RefreshToken) -> None:
        self.tokens[token.id] = token

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        for token in self.tokens.values():
            if token.token_hash == token_hash:
                return token
        return None

    def mark_replaced(self, token_id: UUID, replaced_by: UUID) -> None:
        self.tokens[token_id] = replace(self.tokens[token_id], replaced_by=replaced_by)

    def revoke_family(self, family_id: UUID, at: datetime) -> None:
        for token_id, token in list(self.tokens.items()):
            if token.family_id == family_id and token.revoked_at is None:
                self.tokens[token_id] = replace(token, revoked_at=at)

    def revoke_user_families(
        self, user_id: UUID, except_family: UUID | None, at: datetime
    ) -> None:
        for token_id, token in list(self.tokens.items()):
            if (
                token.user_id == user_id
                and token.revoked_at is None
                and token.family_id != except_family
            ):
                self.tokens[token_id] = replace(token, revoked_at=at)


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
        self.refresh_tokens = MemoryRefreshTokenRepository(dict(store.refresh_tokens))

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
        self._store.refresh_tokens = dict(self.refresh_tokens.tokens)
        self._store.users = [
            replace(u, password_hash=self._pending.password_hashes[u.id])
            if u.id in self._pending.password_hashes
            else u
            for u in self._store.users
        ]
        self._clear()

    def _clear(self) -> None:
        self._pending.users.clear()
        self._pending.vaults.clear()
        self._pending.folders.clear()
        self._pending.password_hashes.clear()
