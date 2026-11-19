"""Login, rotation, reuse detection and logout, against in-memory fakes."""

from datetime import timedelta

import pytest
from tests.fakes.clock import FixedClock
from tests.fakes.hasher import ReversingHasher
from tests.fakes.memory import MemoryStore, MemoryUnitOfWork

from twin.adapters.auth.jwt_tokens import JwtAccessTokens
from twin.adapters.ratelimit.memory_login_limiter import MemoryLoginLimiter
from twin.application.create_user import CreateUser
from twin.application.ports.unit_of_work import UnitOfWork
from twin.application.sessions import Sessions, SessionTokens, hash_token
from twin.domain.session import InvalidCredentials, InvalidRefreshToken, RateLimited
from twin.domain.vault import User

PASSWORD = "a long enough password"


class Rig:
    def __init__(self) -> None:
        self.store = MemoryStore()
        self.clock = FixedClock()
        self.hasher = ReversingHasher()
        self.jwt = JwtAccessTokens(
            "unit-test-secret-0123456789-abcdefgh", self.clock, timedelta(minutes=15)
        )
        self.sessions = Sessions(
            self.uow, self.clock, self.hasher, self.jwt, MemoryLoginLimiter(self.clock)
        )
        self.user: User = CreateUser(self.uow, self.clock).execute(
            "Ada@Example.com", password_hash=self.hasher.hash(PASSWORD)
        )

    def uow(self) -> UnitOfWork:
        return MemoryUnitOfWork(self.store)

    def login(
        self, password: str = PASSWORD, email: str = "ada@example.com"
    ) -> SessionTokens:
        return self.sessions.login(email, password, "10.0.0.1")


@pytest.fixture
def rig() -> Rig:
    return Rig()


def test_login_returns_both_tokens_and_stores_only_the_hash(rig: Rig) -> None:
    tokens = rig.login(email="  ADA@example.com ")
    assert tokens.expires_in == 900
    assert rig.jwt.authenticate(f"Bearer {tokens.access_token}") == rig.user.id
    stored = list(rig.store.refresh_tokens.values())
    assert len(stored) == 1
    assert stored[0].token_hash == hash_token(tokens.refresh_token)
    assert tokens.refresh_token != stored[0].token_hash
    assert stored[0].expires_at - rig.clock.now() == timedelta(days=30)


def test_wrong_password_and_unknown_email_give_the_same_error(rig: Rig) -> None:
    errors = []
    for email, password in (
        ("ada@example.com", "wrong password!"),
        ("nobody@example.com", PASSWORD),
        ("not an email", PASSWORD),
    ):
        with pytest.raises(InvalidCredentials) as caught:
            rig.login(password, email)
        errors.append((caught.value.code, caught.value.message, caught.value.details))
    assert len(set(map(str, errors))) == 1
    assert not rig.store.refresh_tokens


def test_unknown_email_still_runs_a_password_verify(rig: Rig) -> None:
    before = rig.hasher.verified
    with pytest.raises(InvalidCredentials):
        rig.login(PASSWORD, "nobody@example.com")
    assert rig.hasher.verified == before + 1


def test_an_account_without_a_password_cannot_log_in(rig: Rig) -> None:
    CreateUser(rig.uow, rig.clock).execute("g@example.com", google_subject="sub-1")
    with pytest.raises(InvalidCredentials):
        rig.login("", "g@example.com")
    with pytest.raises(InvalidCredentials):
        rig.login("anything at all", "g@example.com")


def test_refresh_swaps_the_token_and_the_old_one_is_spent(rig: Rig) -> None:
    first = rig.login()
    second = rig.sessions.refresh(first.refresh_token)
    assert second.refresh_token != first.refresh_token
    records = {r.token_hash: r for r in rig.store.refresh_tokens.values()}
    spent = records[hash_token(first.refresh_token)]
    live = records[hash_token(second.refresh_token)]
    assert spent.replaced_by == live.id
    assert live.family_id == spent.family_id
    assert rig.sessions.refresh(second.refresh_token).refresh_token


def test_reusing_a_replaced_token_revokes_the_whole_family(rig: Rig) -> None:
    first = rig.login()
    second = rig.sessions.refresh(first.refresh_token)
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(first.refresh_token)
    # The replay also ended the legitimate holder's session.
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(second.refresh_token)
    assert all(r.revoked_at for r in rig.store.refresh_tokens.values())


def test_another_login_is_a_separate_family(rig: Rig) -> None:
    phone = rig.login()
    laptop = rig.login()
    rig.sessions.logout(phone.refresh_token)
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(phone.refresh_token)
    assert rig.sessions.refresh(laptop.refresh_token)


def test_logout_revokes_the_token(rig: Rig) -> None:
    tokens = rig.login()
    rig.sessions.logout(tokens.refresh_token)
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(tokens.refresh_token)


def test_logout_ignores_missing_and_unknown_tokens(rig: Rig) -> None:
    rig.sessions.logout(None)
    rig.sessions.logout("never issued")


def test_refresh_refuses_missing_unknown_and_expired_tokens(rig: Rig) -> None:
    tokens = rig.login()
    for bad in (None, "", "never issued"):
        with pytest.raises(InvalidRefreshToken):
            rig.sessions.refresh(bad)
    rig.clock.advance(timedelta(days=30))
    with pytest.raises(InvalidRefreshToken):
        rig.sessions.refresh(tokens.refresh_token)


def test_a_refresh_token_still_works_just_before_it_expires(rig: Rig) -> None:
    tokens = rig.login()
    rig.clock.advance(timedelta(days=30) - timedelta(seconds=1))
    assert rig.sessions.refresh(tokens.refresh_token)


def test_five_failures_block_even_the_right_password(rig: Rig) -> None:
    for _ in range(5):
        with pytest.raises(InvalidCredentials):
            rig.login("wrong password!")
    with pytest.raises(RateLimited) as caught:
        rig.login()
    assert caught.value.retry_after == 15 * 60
    rig.clock.advance(timedelta(minutes=15))
    assert rig.login().access_token


def test_a_successful_login_resets_the_failure_count(rig: Rig) -> None:
    for _ in range(4):
        with pytest.raises(InvalidCredentials):
            rig.login("wrong password!")
    rig.login()
    for _ in range(4):
        with pytest.raises(InvalidCredentials):
            rig.login("wrong password!")
