from uuid import UUID


class AnonymousAuthenticator:
    """Placeholder until sessions exist (E02-S03): nobody is ever logged in."""

    def authenticate(self, authorization: str | None) -> UUID | None:
        return None
