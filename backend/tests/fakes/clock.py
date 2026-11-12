from datetime import UTC, datetime, timedelta


class FixedClock:
    """In-memory fake of the `Clock` port. Fakes live here and implement the ports."""

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start or datetime(2026, 1, 1, tzinfo=UTC)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta
