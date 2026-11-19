import base64
import hashlib
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from tests.fakes.clock import FixedClock

from twin.adapters.auth.google_identity import GoogleIdentityProvider
from twin.adapters.auth.oauth_state import (
    OAuthState,
    StateCookie,
    code_challenge,
    new_state,
)
from twin.domain.identity import ExternalIdentity, IdentityRejected

CLIENT_ID = "client-123.apps.googleusercontent.com"
NOW = datetime(2026, 6, 1, tzinfo=UTC)
KEY = "irrelevant-key-0123456789-abcdefgh"
SECRET = "a-secret-0123456789-abcdefghijklmnop"


def claims(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "sub": "1234567890",
        "email": "ada@example.com",
        "email_verified": True,
        "exp": int((NOW + timedelta(hours=1)).timestamp()),
    }
    return {k: v for k, v in {**base, **overrides}.items() if v is not None}


def provider(
    transport: httpx.MockTransport,
) -> GoogleIdentityProvider:
    return GoogleIdentityProvider(
        CLIENT_ID,
        "shh",
        "http://x/cb",
        FixedClock(NOW),
        httpx.Client(transport=transport),
    )


def returning(payload: dict[str, object]) -> httpx.MockTransport:
    token = jwt.encode(payload, KEY, "HS256")
    return httpx.MockTransport(
        lambda request: httpx.Response(200, json={"id_token": token})
    )


def exchange_with(payload: dict[str, object]) -> ExternalIdentity:
    return provider(returning(payload)).exchange("code", "verifier")


def test_authorization_url_carries_state_and_an_s256_challenge() -> None:
    google = provider(returning(claims()))
    url = urlsplit(google.authorization_url("st", "chal"))
    query = parse_qs(url.query)
    assert url.netloc == "accounts.google.com"
    assert query["state"] == ["st"]
    assert query["code_challenge"] == ["chal"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["response_type"] == ["code"]
    assert query["client_id"] == [CLIENT_ID]
    assert query["scope"] == ["openid email"]


def test_exchange_posts_the_code_and_verifier_and_returns_the_identity() -> None:
    seen: list[httpx.Request] = []
    token = jwt.encode(claims(), KEY, "HS256")

    def respond(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id_token": token})

    identity = provider(httpx.MockTransport(respond)).exchange(
        "the-code", "the-verifier"
    )
    assert (identity.subject, identity.email) == ("1234567890", "ada@example.com")
    form = parse_qs(seen[0].content.decode())
    assert form["code"] == ["the-code"]
    assert form["code_verifier"] == ["the-verifier"]
    assert form["client_secret"] == ["shh"]
    assert form["grant_type"] == ["authorization_code"]


@pytest.mark.parametrize(
    "changes",
    [
        {"iss": "https://evil.example"},
        {"aud": "someone-else"},
        {"exp": int((NOW - timedelta(seconds=1)).timestamp())},
        {"email_verified": False},
        {"email_verified": "true"},
        {"sub": ""},
    ],
)
def test_bad_id_token_claims_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(IdentityRejected):
        exchange_with(claims(**changes))


@pytest.mark.parametrize(
    "missing", ["exp", "email_verified", "sub", "email", "iss", "aud"]
)
def test_missing_claims_are_rejected(missing: str) -> None:
    payload = claims()
    del payload[missing]
    with pytest.raises(IdentityRejected):
        exchange_with(payload)


def test_audience_list_containing_the_client_id_is_accepted() -> None:
    assert exchange_with(claims(aud=["other", CLIENT_ID]))


def test_bare_issuer_is_accepted() -> None:
    assert exchange_with(claims(iss="accounts.google.com"))


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(400, json={"error": "invalid_grant"}),
        httpx.Response(200, json={}),
        httpx.Response(200, json={"id_token": "not-a-jwt"}),
        httpx.Response(200, text="not json"),
    ],
)
def test_token_endpoint_failures_are_rejected(response: httpx.Response) -> None:
    google = provider(httpx.MockTransport(lambda request: response))
    with pytest.raises(IdentityRejected):
        google.exchange("c", "v")


def test_network_failure_is_rejected() -> None:
    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    with pytest.raises(IdentityRejected):
        provider(httpx.MockTransport(boom)).exchange("c", "v")


def test_code_challenge_is_the_rfc7636_s256_value() -> None:
    # The worked example in RFC 7636 appendix B.
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    assert code_challenge(verifier) == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    digest = hashlib.sha256(verifier.encode()).digest()
    assert base64.urlsafe_b64decode(code_challenge(verifier) + "=") == digest


def test_state_cookie_round_trips_and_expires() -> None:
    clock = FixedClock(NOW)
    cookie = StateCookie(SECRET, clock)
    flow = new_state()
    value = cookie.dump(flow)
    assert cookie.load(value) == flow
    clock.advance(timedelta(minutes=11))
    assert cookie.load(value) is None


def test_state_cookie_rejects_tampering_other_keys_and_access_tokens() -> None:
    clock = FixedClock(NOW)
    cookie = StateCookie(SECRET, clock)
    other = StateCookie("another-secret-0123456789-abcdefghijk", clock)
    value = cookie.dump(OAuthState("s", "v"))
    assert other.load(value) is None
    assert cookie.load(value[:-2] + "xx") is None
    assert cookie.load(None) is None
    assert cookie.load("") is None
    access = jwt.encode({"sub": "u", "exp": 4102444800}, SECRET, "HS256")
    assert cookie.load(access) is None
