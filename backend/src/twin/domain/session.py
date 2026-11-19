from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from twin.domain.errors import DomainError


class InvalidCredentials(DomainError):
    """Wrong password or unknown email; the two are deliberately indistinguishable."""

    code = "invalid_credentials"


class InvalidRefreshToken(DomainError):
    """The refresh token is missing, unknown, expired, used already or revoked."""

    code = "invalid_refresh_token"


class RateLimited(DomainError):
    code = "rate_limited"

    def __init__(self, message: str, *, retry_after: int) -> None:
        super().__init__(message, details={"retry_after": retry_after})
        self.retry_after = retry_after


class CsrfFailed(DomainError):
    code = "csrf_failed"


@dataclass(frozen=True)
class RefreshToken:
    """The stored record of one refresh token. `token_hash` is the SHA-256 of the token."""

    id: UUID
    user_id: UUID
    token_hash: str = field(repr=False)
    family_id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    replaced_by: UUID | None
    created_at: datetime

    @property
    def is_spent(self) -> bool:
        """Already swapped for a newer token, or revoked: presenting it again is a theft sign."""
        return self.replaced_by is not None or self.revoked_at is not None
