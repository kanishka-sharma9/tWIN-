from datetime import timedelta
from uuid import uuid4

import jwt
import pytest
from tests.fakes.clock import FixedClock

from twin.adapters.auth.jwt_tokens import JwtAccessTokens

SECRET = "unit-test-secret-0123456789-abcdefgh"


def make(clock: FixedClock | None = None) -> tuple[JwtAccessTokens, FixedClock]:
    clock = clock or FixedClock()
    return JwtAccessTokens(SECRET, clock, timedelta(minutes=15)), clock


def bearer(token: str) -> str:
    return f"Bearer {token}"


def test_a_fresh_token_names_its_user_and_vault() -> None:
    tokens, clock = make()
    user, vault = uuid4(), uuid4()
    issued = tokens.issue(user, vault)
    assert issued.expires_in == 900
    claims = jwt.decode(
        issued.token, SECRET, algorithms=["HS256"], options={"verify_exp": False}
    )
    assert claims["sub"] == str(user)
    assert claims["vid"] == str(vault)
    assert claims["exp"] - claims["iat"] == 900
    assert claims["iat"] == int(clock.now().timestamp())
    assert tokens.authenticate(bearer(issued.token)) == user


def test_a_token_expires_after_fifteen_minutes_on_the_clock() -> None:
    tokens, clock = make()
    user = uuid4()
    header = bearer(tokens.issue(user, uuid4()).token)
    clock.advance(timedelta(minutes=14, seconds=59))
    assert tokens.authenticate(header) == user
    clock.advance(timedelta(seconds=1))
    assert tokens.authenticate(header) is None


def test_missing_malformed_and_foreign_tokens_authenticate_nobody() -> None:
    tokens, _ = make()
    claims = {"sub": str(uuid4()), "iat": 1, "exp": 4_000_000_000}
    unsigned = jwt.encode(claims, "", algorithm="none")
    wrong_key = jwt.encode(claims, "another-secret-" * 4, algorithm="HS256")
    no_exp = jwt.encode({"sub": str(uuid4())}, SECRET, algorithm="HS256")
    not_a_uuid = jwt.encode({**claims, "sub": "nope"}, SECRET, algorithm="HS256")
    for header in (
        None,
        "",
        "Bearer",
        "Bearer ",
        "Basic abc",
        "Bearer not-a-jwt",
        bearer(unsigned),
        bearer(wrong_key),
        bearer(no_exp),
        bearer(not_a_uuid),
    ):
        assert tokens.authenticate(header) is None, header
    # Control: the same claims signed with the right key and valid are accepted.
    good = jwt.encode(claims, SECRET, algorithm="HS256")
    assert tokens.authenticate(bearer(good)) is not None


def test_a_short_secret_is_refused() -> None:
    with pytest.raises(ValueError, match="at least 32"):
        JwtAccessTokens("short", FixedClock(), timedelta(minutes=15))
