"""ChangePassword against in-memory fakes."""

from datetime import timedelta

import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.hasher import ReversingHasher
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.adapters.auth.jwt_tokens import JwtAccessTokens
from twin.adapters.ratelimit.memory_login_limiter import MemoryLoginLimiter
from twin.application.change_password import ChangePassword
from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.application.sessions import Sessions, SessionTokens
from twin.domain.password import NoPassword, WeakPassword, WrongPassword
from twin.domain.session import InvalidRefreshToken, RateLimited
from twin.domain.vault import User

PASSWORD = "a long enough password"
NEW = "another long password"


class Rig:
    def __init__(self) -> None:
        self.store = MemoryStore()
        self.clock = FixedClock()
        self.hasher = ReversingHasher()
        limiter = MemoryLoginLimiter(self.clock)
        jwt = JwtAccessTokens(
            "unit-test-secret-0123456789-abcdefgh", self.clock, timedelta(minutes=15)
        )
        self.sessions = Sessions(self.uow, self.clock, self.hasher, jwt, limiter)
        self.change = ChangePassword(self.uow, self.clock, self.hasher, limiter)
        self.user: User = CreateUser(self.uow, self.clock).execute(
            "Ada@Example.com", password_hash=self.hasher.hash(PASSWORD)
        )

    def uow(self) -> UnitOfWork:
        return MemoryUnitOfWork(self.store)

    def login(self) -> SessionTokens:
        return self.sessions.login("ada@example.com", PASSWORD, "10.0.0.1")

    def stored_hash(self) -> str | None:
        with self.uow() as uow:
            user = uow.users.get_by_id(self.user.id)
            return user.password_hash if user else None


@pytest.fixture
def rig() -> Rig:
    return Rig()


def test_the_new_password_is_stored_hashed(rig: Rig) -> None:
    rig.change.execute(rig.user.id, PASSWORD, NEW, None)
    assert rig.stored_hash() == rig.hasher.hash(NEW)


def test_a_wrong_current_password_changes_nothing(rig: Rig) -> None:
    other = rig.login()
    with pytest.raises(WrongPassword):
        rig.change.execute(rig.user.id, "not the password", NEW, None)
    assert rig.stored_hash() == rig.hasher.hash(PASSWORD)
    assert rig.sessions.refresh(other.refresh_token)


def test_a_weak_new_password_changes_nothing(rig: Rig) -> None:
    other = rig.login()
    for bad in ("short", "x" * 129):
        with pytest.raises(WeakPassword):
            rig.change.execute(rig.user.id, PASSWORD, bad, None)
    assert rig.stored_hash() == rig.hasher.hash(PASSWORD)
    assert rig.sessions.refresh(other.refresh_token)


def test_other_sessions_are_revoked_and_the_kept_one_survives(rig: Rig) -> None:
    phone = rig.login()
    laptop = rig.login()
    keep = rig.change.family_of(rig.user.id, laptop.refresh_token)
    assert keep is not None
    rig.change.execute(rig.user.id, PASSWORD, NEW, keep)
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(phone.refresh_token)
    assert rig.sessions.refresh(laptop.refresh_token)


def test_without_a_kept_session_every_session_is_revoked(rig: Rig) -> None:
    tokens = rig.login()
    rig.change.execute(rig.user.id, PASSWORD, NEW, None)
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(tokens.refresh_token)


def test_other_peoples_sessions_are_left_alone(rig: Rig) -> None:
    CreateUser(rig.uow, rig.clock).execute(
        "bob@example.com", password_hash=rig.hasher.hash(PASSWORD)
    )
    bob = rig.sessions.login("bob@example.com", PASSWORD, "10.0.0.2")
    rig.change.execute(rig.user.id, PASSWORD, NEW, None)
    assert rig.sessions.refresh(bob.refresh_token)


def test_family_of_ignores_missing_unknown_and_foreign_tokens(rig: Rig) -> None:
    CreateUser(rig.uow, rig.clock).execute(
        "bob@example.com", password_hash=rig.hasher.hash(PASSWORD)
    )
    bob = rig.sessions.login("bob@example.com", PASSWORD, "10.0.0.2")
    assert rig.change.family_of(rig.user.id, None) is None
    assert rig.change.family_of(rig.user.id, "never issued") is None
    assert rig.change.family_of(rig.user.id, bob.refresh_token) is None


def test_an_account_without_a_password_has_nothing_to_change(rig: Rig) -> None:
    google = CreateUser(rig.uow, rig.clock).execute(
        "g@example.com", google_subject="sub-1"
    )
    with pytest.raises(NoPassword):
        rig.change.execute(google.id, "", NEW, None)
    with pytest.raises(NoPassword):
        rig.change.execute(google.id, "anything at all", NEW, None)


def test_repeated_wrong_current_passwords_are_rate_limited(rig: Rig) -> None:
    for _ in range(5):
        with pytest.raises(WrongPassword):
            rig.change.execute(rig.user.id, "not the password", NEW, None)
    with pytest.raises(RateLimited) as caught:
        rig.change.execute(rig.user.id, PASSWORD, NEW, None)
    assert caught.value.retry_after > 0
    assert rig.stored_hash() == rig.hasher.hash(PASSWORD)
    rig.clock.advance(timedelta(minutes=16))
    rig.change.execute(rig.user.id, PASSWORD, NEW, None)


def test_a_correct_password_resets_the_failure_count(rig: Rig) -> None:
    for _ in range(4):
        with pytest.raises(WrongPassword):
            rig.change.execute(rig.user.id, "not the password", NEW, None)
    rig.change.execute(rig.user.id, PASSWORD, NEW, None)
    for _ in range(4):
        with pytest.raises(WrongPassword):
            rig.change.execute(rig.user.id, PASSWORD, "yet another one", None)
