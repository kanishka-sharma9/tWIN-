from uuid import UUID


class NullAuthenticator:
    """Authenticates nobody, so vault routes answer 401 until sessions arrive (E02-S03)."""

    def authenticate(self, authorization: str | None) -> UUID | None:
        return None
