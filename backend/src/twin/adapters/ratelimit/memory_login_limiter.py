import threading
from datetime import timedelta
from math import ceil

from twin.application.ports.clock import Clock

MAX_FAILURES = 5
WINDOW = timedelta(minutes=15)
_PRUNE_AT = 10_000


class MemoryLoginLimiter:
    """Allows `MAX_FAILURES` failed logins per key in a sliding window.

    Held in this process's memory: fine for one process (v1). Several workers would each
    count separately and a restart forgets everything; a shared store replaces it then.
    """

    def __init__(
        self, clock: Clock, max_failures: int = MAX_FAILURES, window: timedelta = WINDOW
    ) -> None:
        self._clock = clock
        self._max = max_failures
        self._window = window
        self._failures: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def blocked_for(self, key: str) -> int | None:
        with self._lock:
            recent = self._recent(key)
            if len(recent) < self._max:
                return None
            wait = (
                recent[0] + self._window.total_seconds() - self._clock.now().timestamp()
            )
            return max(1, ceil(wait))

    def record_failure(self, key: str) -> None:
        with self._lock:
            if len(self._failures) >= _PRUNE_AT:
                for other in list(self._failures):
                    self._recent(other)
            self._recent(key)
            self._failures.setdefault(key, []).append(self._clock.now().timestamp())

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def _recent(self, key: str) -> list[float]:
        """The failures still inside the window; forgets the older ones."""
        cutoff = self._clock.now().timestamp() - self._window.total_seconds()
        kept = [t for t in self._failures.get(key, []) if t > cutoff]
        if kept:
            self._failures[key] = kept
        else:
            self._failures.pop(key, None)
        return kept
