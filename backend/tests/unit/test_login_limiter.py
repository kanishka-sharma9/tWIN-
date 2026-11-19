from datetime import timedelta

from tests.fakes.clock import FixedClock

from twin.adapters.ratelimit.memory_login_limiter import MemoryLoginLimiter


def test_blocks_after_five_failures_for_that_key_only() -> None:
    limiter = MemoryLoginLimiter(FixedClock())
    for _ in range(4):
        limiter.record_failure("a|1")
        assert limiter.blocked_for("a|1") is None
    limiter.record_failure("a|1")
    assert limiter.blocked_for("a|1") == 15 * 60
    assert limiter.blocked_for("a|2") is None
    assert limiter.blocked_for("b|1") is None


def test_the_wait_shrinks_and_the_block_lifts_after_the_window() -> None:
    clock = FixedClock()
    limiter = MemoryLoginLimiter(clock)
    for _ in range(5):
        limiter.record_failure("k")
    clock.advance(timedelta(minutes=10))
    assert limiter.blocked_for("k") == 5 * 60
    clock.advance(timedelta(minutes=5))
    assert limiter.blocked_for("k") is None


def test_reset_clears_the_count() -> None:
    limiter = MemoryLoginLimiter(FixedClock())
    for _ in range(5):
        limiter.record_failure("k")
    limiter.reset("k")
    assert limiter.blocked_for("k") is None
