"""Login, refresh, logout and who-am-I (E02-S03), against the real test database."""

import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from twin.adapters.persistence.models import RefreshTokenRow
from twin.application.sessions import hash_token
from twin.bootstrap import create_app
from twin.settings import Settings

PASSWORD = "S3cret-passphrase-Zq9"
CSRF = {"X-Requested-With": "twin"}


@pytest.fixture
def account(client: TestClient, email: str) -> str:
    """A signed-up account; returns its email. The client's cookie jar is cleared."""
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201
    client.cookies.clear()
    return email


def login(client: TestClient, email: str, password: str = PASSWORD) -> Response:
    response: Response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    return response


def refresh_cookie(response: Response) -> str:
    match = re.search(r"refresh_token=([^;]+)", response.headers["set-cookie"])
    assert match
    return match.group(1)


def use_cookie(client: TestClient, value: str) -> None:
    """Present exactly this refresh token (the jar would otherwise send two)."""
    client.cookies.clear()
    client.cookies.set(
        "refresh_token", value, domain="testserver.local", path="/api/auth"
    )


def me(client: TestClient, token: str | None) -> Response:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response: Response = client.get("/api/auth/me", headers=headers)
    return response


def refresh(client: TestClient, **headers: str) -> Response:
    response: Response = client.post("/api/auth/refresh", headers={**CSRF, **headers})
    return response


def test_login_returns_an_access_token_and_sets_the_refresh_cookie(
    client: TestClient, account: str
) -> None:
    response = login(client, account.upper())
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 900
    assert body["user"]["email"] == account
    assert body["user"]["has_password"] is True
    assert "refresh_token" not in body
    assert me(client, body["access_token"]).json() == body["user"]


def test_the_refresh_cookie_has_the_right_flags(
    client: TestClient, account: str
) -> None:
    cookie = login(client, account).headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/api/auth" in cookie
    assert f"max-age={30 * 24 * 3600}" in cookie
    assert "secure" not in cookie.replace("samesite", "")


def test_the_cookie_is_secure_when_configured(settings: Settings, account: str) -> None:
    secure = settings.model_copy(update={"cookie_secure": True})
    with TestClient(create_app(secure), base_url="https://testserver") as client:
        assert "secure" in login(client, account).headers["set-cookie"].lower().split(
            "; "
        )


def test_signup_also_logs_the_new_account_in(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201
    body = response.json()
    assert me(client, body["access_token"]).json()["email"] == email
    assert refresh(client).status_code == 200


def test_wrong_password_and_unknown_email_get_the_same_generic_error(
    client: TestClient, account: str
) -> None:
    wrong = login(client, account, "not the password!")
    unknown = login(client, f"nobody-{uuid4().hex}@example.com")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert wrong.json()["error"]["code"] == "invalid_credentials"
    assert "set-cookie" not in wrong.headers


def test_a_malformed_email_is_also_just_a_wrong_login(client: TestClient) -> None:
    response = login(client, "not an email")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_the_login_password_never_reaches_the_response(
    client: TestClient, account: str
) -> None:
    assert PASSWORD not in login(client, account).text
    assert (
        "wrong-password-value"
        not in login(client, account, "wrong-password-value").text
    )


def test_missing_malformed_and_expired_access_tokens_get_401(
    client: TestClient, settings: Settings, account: str
) -> None:
    token = login(client, account).json()["access_token"]
    assert me(client, token).status_code == 200
    claims = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value() if settings.jwt_secret else "",
        algorithms=["HS256"],
    )
    past = int((datetime.now(UTC) - timedelta(minutes=1)).timestamp())
    expired = jwt.encode(
        {**claims, "iat": past - 900, "exp": past},
        settings.jwt_secret.get_secret_value() if settings.jwt_secret else "",
        algorithm="HS256",
    )
    for bad in (None, "garbage", expired, token[:-3] + "abc"):
        response = me(client, bad)
        assert response.status_code == 401, bad
        assert response.json()["error"]["code"] == "unauthorized"


def test_refresh_gives_a_new_pair_and_the_old_token_stops_working(
    client: TestClient, account: str
) -> None:
    first = login(client, account)
    old_cookie = refresh_cookie(first)
    second = refresh(client)
    assert second.status_code == 200
    new_cookie = refresh_cookie(second)
    assert new_cookie != old_cookie
    assert me(client, second.json()["access_token"]).status_code == 200
    use_cookie(client, old_cookie)
    replay = refresh(client)
    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "invalid_refresh_token"


def test_replaying_a_used_token_also_ends_the_newer_one(
    client: TestClient, account: str
) -> None:
    old_cookie = refresh_cookie(login(client, account))
    newer = refresh_cookie(refresh(client))
    use_cookie(client, old_cookie)
    assert refresh(client).status_code == 401
    use_cookie(client, newer)
    assert refresh(client).status_code == 401


def test_after_logout_the_refresh_token_no_longer_works(
    client: TestClient, account: str
) -> None:
    cookie = refresh_cookie(login(client, account))
    out = client.post("/api/auth/logout", headers=CSRF)
    assert out.status_code == 204
    assert (
        'refresh_token=""' in out.headers["set-cookie"]
        or "Max-Age=0" in out.headers["set-cookie"]
    )
    use_cookie(client, cookie)
    response = refresh(client)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"


def test_logout_without_a_session_is_still_204(client: TestClient) -> None:
    assert client.post("/api/auth/logout", headers=CSRF).status_code == 204


def test_refresh_without_a_cookie_is_401(client: TestClient) -> None:
    response = refresh(client)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"


def test_only_the_hash_of_the_refresh_token_is_stored(
    client: TestClient, settings: Settings, account: str
) -> None:
    raw = refresh_cookie(login(client, account))
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        stored = list(session.scalars(select(RefreshTokenRow.token_hash)))
    engine.dispose()
    assert hash_token(raw) in stored
    assert raw not in stored
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in stored)


@pytest.mark.parametrize("route", ["/api/auth/refresh", "/api/auth/logout"])
def test_csrf_needs_the_custom_header(
    client: TestClient, account: str, route: str
) -> None:
    login(client, account)
    response = client.post(route)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"
    wrong = client.post(route, headers={"X-Requested-With": "XMLHttpRequest"})
    assert wrong.status_code == 403
    # The refused request did not use up the token.
    assert refresh(client).status_code == 200


@pytest.mark.parametrize(
    "origin", ["https://evil.example", "null", "http://testserver.evil.com"]
)
def test_csrf_refuses_a_foreign_origin(
    client: TestClient, account: str, origin: str
) -> None:
    login(client, account)
    response = refresh(client, Origin=origin)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_csrf_accepts_a_same_host_origin(client: TestClient, account: str) -> None:
    login(client, account)
    assert refresh(client, Origin="http://testserver").status_code == 200


@pytest.fixture
def limited_client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def test_five_failed_logins_then_429_with_retry_after(
    limited_client: TestClient, account: str
) -> None:
    for _ in range(5):
        assert login(limited_client, account, "wrong password!").status_code == 401
    blocked = login(limited_client, account)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
    assert 1 <= int(blocked.headers["retry-after"]) <= 15 * 60
    # Another email from the same address is not affected.
    assert login(limited_client, f"other-{uuid4().hex}@example.com").status_code == 401


def test_the_openapi_schema_documents_the_session_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    for route in ("login", "refresh", "logout", "me"):
        assert f"/api/auth/{route}" in paths
