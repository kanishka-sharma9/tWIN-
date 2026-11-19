from urllib.parse import urlencode

from twin.domain.identity import ExternalIdentity, IdentityRejected


class FakeIdentityProvider:
    """In-memory fake of the `IdentityProvider` port.

    `codes` maps a code to the identity it stands for. `exchanges` records what it was given.
    """

    def __init__(self) -> None:
        self.codes: dict[str, ExternalIdentity] = {}
        self.exchanges: list[tuple[str, str]] = []

    def authorization_url(self, state: str, code_challenge: str) -> str:
        query = urlencode(
            {
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )
        return f"https://idp.test/authorize?{query}"

    def exchange(self, code: str, code_verifier: str) -> ExternalIdentity:
        self.exchanges.append((code, code_verifier))
        identity = self.codes.get(code)
        if identity is None:
            raise IdentityRejected("bad code")
        return identity
