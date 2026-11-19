from typing import Protocol


class LoginLimiter(Protocol):
    """Counts failed logins per key (email and client address)."""

    def blocked_for(self, key: str) -> int | None:
        """Seconds until another attempt is allowed, or None when the key is not blocked."""
        ...

    def record_failure(self, key: str) -> None: ...

    def reset(self, key: str) -> None: ...
