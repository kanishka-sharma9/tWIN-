from typing import Protocol

from twin.domain.identity import ExternalIdentity


class IdentityProvider(Protocol):
    """An OpenID Connect provider that runs the authorization-code flow with PKCE."""

    def authorization_url(self, state: str, code_challenge: str) -> str:
        """Where to send the browser. `code_challenge` is the S256 challenge."""
        ...

    def exchange(self, code: str, code_verifier: str) -> ExternalIdentity:
        """Swap the code for the person's identity.

        Raises `IdentityRejected` when the code is refused or any ID token check fails,
        including an email the provider has not verified.
        """
        ...
