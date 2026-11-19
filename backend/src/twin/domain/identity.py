from dataclasses import dataclass

from twin.domain.errors import DomainError


class ProviderDisabled(DomainError):
    """The sign-in provider is not configured on this server."""

    code = "not_found"


class IdentityRejected(DomainError):
    """The provider refused the code, or its ID token failed a check."""

    code = "identity_rejected"


class AccountExists(DomainError):
    """The email already belongs to an account that was not made with this provider."""

    code = "account_exists"


@dataclass(frozen=True)
class VerifiedIdentity:
    """A verified person according to the provider: stable subject plus a verified email."""

    subject: str
    email: str
