from datetime import datetime
from typing import Protocol
from uuid import UUID

from twin.domain.session import RefreshToken


class RefreshTokenRepository(Protocol):
    def add(self, token: RefreshToken) -> None: ...

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """The record for a token hash. Locks the row until the transaction ends, so two
        requests cannot both swap the same token."""
        ...

    def mark_replaced(self, token_id: UUID, replaced_by: UUID) -> None: ...

    def revoke_family(self, family_id: UUID, at: datetime) -> None:
        """Revoke every token of the family that is not revoked yet."""
        ...
