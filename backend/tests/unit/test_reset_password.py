"""ResetPassword against in-memory fakes."""

from datetime import timedelta

import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.hasher import ReversingHasher
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.adapters.auth.jwt_tokens import JwtAccessTokens
from twin.adapters.ratelimit.memory_login_limiter import MemoryLoginLimiter
from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.application.reset_password import ResetPassword
from twin.application.sessions import Sessions
from twin.domain.password import NoPassword, NoSuchAccount, WeakPassword
from twin.domain.session import InvalidCredentials, InvalidRefreshToken

OLD = "an old long password"
NEW = "a brand new passphrase"


class Rig:
    def __init__(self) -> None:
        self.store = MemoryStore()
        self.clock = FixedClock()
        self.hasher = ReversingHasher()
        jwt = JwtAccessTokens(
            "unit-test-secret-0123456789-abcdefgh", self.clock, timedelta(minutes=15)
        )
        self.sessions = Sessions(
            self.uow, self.clock, self.hasher, jwt, MemoryLoginLimiter(self.clock)
        )
        self.reset = ResetPassword(self.uow, self.clock, self.hasher)
        CreateUser(self.uow, self.clock).execute(
            "Ada@Example.com", password_hash=self.hasher.hash(OLD)
        )

    def uow(self) -> UnitOfWork:
        return MemoryUnitOfWork(self.store)


@pytest.fixture
def rig() -> Rig:
    return Rig()


def test_the_new_password_logs_in_and_the_old_one_does_not(rig: Rig) -> None:
    rig.reset.execute("ada@example.com", NEW)
    rig.sessions.login("ada@example.com", NEW, "10.0.0.1")
    with pytest.raises(InvalidCredentials):
        rig.sessions.login("ada@example.com", OLD, "10.0.0.1")


def test_it_returns_the_stored_email(rig: Rig) -> None:
    assert rig.reset.execute(" ADA@example.com ", NEW) == "Ada@Example.com"


def test_every_refresh_token_stops_working(rig: Rig) -> None:
    first = rig.sessions.login("ada@example.com", OLD, "10.0.0.1")
    second = rig.sessions.login("ada@example.com", OLD, "10.0.0.2")
    rig.reset.execute("ada@example.com", NEW)
    for tokens in (first, second):
        with pytest.raises(InvalidRefreshToken):
            rig.sessions.refresh(tokens.refresh_token)


def test_an_unknown_email_is_refused(rig: Rig) -> None:
    with pytest.raises(NoSuchAccount, match=r"No account with that email."):
        rig.reset.execute("nobody@example.com", NEW)
    assert len(rig.store.users) == 1


def test_a_google_only_account_is_refused(rig: Rig) -> None:
    CreateUser(rig.uow, rig.clock).execute("g@example.com", google_subject="sub-1")
    with pytest.raises(NoPassword, match="signs in with Google"):
        rig.reset.execute("g@example.com", NEW)


@pytest.mark.parametrize("bad", ["short", "x" * 129, ""])
def test_a_password_that_breaks_the_rules_changes_nothing(rig: Rig, bad: str) -> None:
    with pytest.raises(WeakPassword):
        rig.reset.execute("ada@example.com", bad)
    rig.sessions.login("ada@example.com", OLD, "10.0.0.1")
