from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class AccessToken:
    token: str
    expires_in: int  # seconds


class AccessTokenIssuer(Protocol):
    def issue(self, user_id: UUID, vault_id: UUID) -> AccessToken: ...
