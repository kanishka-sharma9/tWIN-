from typing import Protocol
from uuid import UUID

from twin.domain.vault import CurrentVault, Folder, Vault


class VaultRepository(Protocol):
    def add(self, vault: Vault, root: Folder) -> None:
        """Store a vault together with its root folder."""
        ...

    def get_current(self, owner_id: UUID) -> CurrentVault | None:
        """The vault owned by this user, or None."""
        ...

    def get_folder(self, vault_id: UUID, folder_id: UUID) -> Folder | None:
        """A folder, only when it lives in `vault_id`. The model for every vault-scoped query."""
        ...
