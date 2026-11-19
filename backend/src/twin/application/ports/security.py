from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str:
        """A salted hash safe to store; the password cannot be recovered from it."""
        ...

    def verify(self, password: str, password_hash: str) -> bool: ...
