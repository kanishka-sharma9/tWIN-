from typing import Protocol


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str:
        """A salted, self-describing hash of the password."""
        ...

    def verify(self, password_hash: str, password: str) -> bool:
        """True when the password matches; never raises for a wrong password."""
        ...

    def needs_rehash(self, password_hash: str) -> bool:
        """True when the hash was made with weaker parameters than the current ones."""
        ...
