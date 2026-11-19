from typing import Protocol
from uuid import UUID


class UserAuthenticator(Protocol):
    def authenticate(self, authorization: str | None) -> UUID | None:
        """The user id behind an `Authorization` header value, or None when there is none."""
        ...
