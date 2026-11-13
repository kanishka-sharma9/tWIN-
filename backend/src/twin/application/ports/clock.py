from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """The current time, as an outside dependency so use cases can be tested with a fixed one."""

    def now(self) -> datetime: ...
