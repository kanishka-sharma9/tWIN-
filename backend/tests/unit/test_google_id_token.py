import base64
import hashlib
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm
from tests.fakes.clock import FixedClock

from twin.adapters.auth.google_identity import GoogleIdentityProvider
from twin.adapters.auth.oauth_state import (
    OAuthState,
    StateCookie,
    code_challenge,
    new_state,
)
from twin.domain.identity import IdentityRejected, VerifiedIdentity

CLIENT_ID = "client-123.apps.googleusercontent.com"
NOW = datetime(2026, 6, 1, tzinfo=UTC)
GOOGLE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
KID = "google-key-1"


def jwks(kid: str = KID) -> dict[str, object]:
    jwk = RSAAlgorithm.to_jwk(GOOGLE_KEY.public_key(), as_dict=True)
    return {"keys": [{**jwk, "kid": kid, "alg": "RS256", "use": "sig"}]}


def sign(payload: dict[str, object], key: rsa.RSAPrivateKey = GOOGLE_KEY) -> str:
    return jwt.encode(payload, key, algorithm="RS256", headers={"kid": KID})


def google(
    id_token: str, jwks_kid: str = KID, seen: list[httpx.Request] | None = None
) -> httpx.MockTransport:
    """Token endpoint answering with `id_token`; the certs endpoint with Google's key."""

    def respond(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        if request.url.path.endswith("/certs"):
            return httpx.Response(200, json=jwks(jwks_kid))
        return httpx.Response(200, json={"id_token": id_token})

    return httpx.MockTransport(respond)


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
    return google(sign(payload))


def exchange_with(payload: dict[str, object]) -> VerifiedIdentity:
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
    transport = google(sign(claims()), seen=seen)
    identity = provider(transport).exchange("the-code", "the-verifier")
    assert (identity.subject, identity.email) == ("1234567890", "ada@example.com")
    form = parse_qs(next(r for r in seen if r.method == "POST").content.decode())
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


def test_authorization_url_never_contains_the_client_secret() -> None:
    url = provider(returning(claims())).authorization_url("st", "chal")
    assert "shh" not in url
    assert "client_secret" not in url


def test_token_signed_with_another_key_is_rejected() -> None:
    forged = sign(claims(), key=OTHER_KEY)
    with pytest.raises(IdentityRejected):
        provider(google(forged)).exchange("c", "v")


def test_unsigned_token_is_rejected() -> None:
    unsigned = jwt.encode(claims(), "", algorithm="none", headers={"kid": KID})
    with pytest.raises(IdentityRejected):
        provider(google(unsigned)).exchange("c", "v")


def test_token_with_a_key_id_google_does_not_list_is_rejected() -> None:
    with pytest.raises(IdentityRejected):
        provider(google(sign(claims()), jwks_kid="rotated-away")).exchange("c", "v")


def test_signing_keys_are_fetched_once_and_reused() -> None:
    seen: list[httpx.Request] = []
    google_provider = provider(google(sign(claims()), seen=seen))
    google_provider.exchange("c", "v")
    google_provider.exchange("c", "v")
    assert sum(r.url.path.endswith("/certs") for r in seen) == 1
