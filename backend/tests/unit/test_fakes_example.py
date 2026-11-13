"""The fake-versus-port pattern later stories copy.

A port is a small `Protocol` in `twin.application.ports`; the fake in `tests/fakes/` implements it
in memory. Assigning the fake to the port type below is what proves it still fits, because
mypy and ty check it.
"""

from datetime import UTC, datetime, timedelta

from tests.fakes.clock import FixedClock

from twin.application.ports.clock import Clock


def is_expired(clock: Clock, deadline: datetime) -> bool:
    """A stand-in for a use case: it depends on the port, never on a concrete clock."""
    return clock.now() >= deadline


def test_fake_satisfies_the_port() -> None:
    clock: Clock = FixedClock(datetime(2026, 6, 1, tzinfo=UTC))
    assert clock.now() == datetime(2026, 6, 1, tzinfo=UTC)


def test_use_case_runs_against_the_fake_without_a_database() -> None:
    fake = FixedClock(datetime(2026, 6, 1, tzinfo=UTC))
    deadline = datetime(2026, 6, 2, tzinfo=UTC)
    assert not is_expired(fake, deadline)
    fake.advance(timedelta(days=1))
    assert is_expired(fake, deadline)
