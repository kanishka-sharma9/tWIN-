"""Change password (E02-S07), against the real test database."""

from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import SecretStr
from tests.api.test_sessions import (
    CSRF,
    PASSWORD,
    login,
    refresh,
    refresh_cookie,
    use_cookie,
)
from tests.fakes.identity import FakeIdentityProvider

from twin.bootstrap import create_app
from twin.domain.identity import VerifiedIdentity
from twin.settings import Settings

NEW = "A brand new passphrase 42"
ROUTE = "/api/auth/change-password"


@pytest.fixture
def account(client: TestClient, email: str) -> str:
    """A signed-up account; returns its email. The client's cookie jar is cleared."""
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201
    client.cookies.clear()
    return email


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def change(client: TestClient, token: str | None, current: str, new: str) -> Response:
    response: Response = client.post(
        ROUTE,
        json={"current_password": current, "new_password": new},
        headers=bearer(token) if token else {},
    )
    return response


def access_token(response: Response) -> str:
    token: str = response.json()["access_token"]
    return token


def test_a_wrong_current_password_is_refused_and_nothing_changes(
    client: TestClient,
    account: str,
) -> None:
    token = access_token(login(client, account))
    response = change(client, token, "not the password!", NEW)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "wrong_password"
    assert NEW not in response.text
    assert login(client, account, NEW).status_code == 401
    assert login(client, account).status_code == 200


def test_the_new_password_works_at_the_next_login_and_the_old_one_does_not(
    client: TestClient,
    account: str,
) -> None:
    token = access_token(login(client, account))
    response = change(client, token, PASSWORD, NEW)
    assert response.status_code == 204
    assert response.content == b""
    assert login(client, account, PASSWORD).status_code == 401
    assert login(client, account, NEW).status_code == 200


def test_another_device_is_logged_out_and_this_one_stays_in(
    client: TestClient,
    account: str,
) -> None:
    phone = login(client, account)
    phone_cookie = refresh_cookie(phone)
    laptop = login(client, account)
    laptop_cookie = refresh_cookie(laptop)
    use_cookie(client, laptop_cookie)
    assert change(client, access_token(laptop), PASSWORD, NEW).status_code == 204
    use_cookie(client, phone_cookie)
    stale = refresh(client)
    assert stale.status_code == 401
    assert stale.json()["error"]["code"] == "invalid_refresh_token"
    use_cookie(client, laptop_cookie)
    assert refresh(client).status_code == 200


def test_without_the_refresh_cookie_every_session_ends(
    client: TestClient,
    account: str,
) -> None:
    first = login(client, account)
    cookie = refresh_cookie(first)
    client.cookies.clear()
    assert change(client, access_token(first), PASSWORD, NEW).status_code == 204
    use_cookie(client, cookie)
    assert refresh(client).status_code == 401


@pytest.mark.parametrize("new", ["short", "123456789", "x" * 129])
def test_a_new_password_outside_10_to_128_characters_is_refused(
    client: TestClient,
    account: str,
    new: str,
) -> None:
    token = access_token(login(client, account))
    response = change(client, token, PASSWORD, new)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "weak_password"
    assert login(client, account).status_code == 200


@pytest.mark.parametrize("new", ["x" * 10, "x" * 128])
def test_the_limits_themselves_are_accepted(
    client: TestClient,
    account: str,
    new: str,
) -> None:
    token = access_token(login(client, account))
    assert change(client, token, PASSWORD, new).status_code == 204


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"current_password": PASSWORD},
        {"new_password": NEW},
        {"current_password": 1},
    ],
)
def test_a_malformed_body_is_a_validation_error(
    client: TestClient,
    account: str,
    body: dict[str, object],
) -> None:
    token = access_token(login(client, account))
    response = client.post(ROUTE, json=body, headers=bearer(token))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_the_passwords_never_appear_in_an_error(
    client: TestClient,
    account: str,
) -> None:
    token = access_token(login(client, account))
    response = client.post(
        ROUTE,
        json={"current_password": PASSWORD, "new_password": ["x"]},
        headers=bearer(token),
    )
    assert response.status_code == 422
    assert PASSWORD not in response.text


def test_repeated_wrong_current_passwords_end_in_429(
    client: TestClient,
    account: str,
) -> None:
    token = access_token(login(client, account))
    for _ in range(5):
        assert change(client, token, "not the password!", NEW).status_code == 401
    blocked = change(client, token, PASSWORD, NEW)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
    assert int(blocked.headers["retry-after"]) >= 1
    assert login(client, account).status_code == 200  # the password did not change


@pytest.mark.parametrize("token", [None, "garbage", "a.b.c"])
def test_a_request_without_a_valid_bearer_token_is_401(
    client: TestClient, token: str | None
) -> None:
    response = change(client, token, PASSWORD, NEW)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


@pytest.fixture
def fake() -> FakeIdentityProvider:
    return FakeIdentityProvider()


@pytest.fixture
def google(settings: Settings, fake: FakeIdentityProvider) -> Iterator[TestClient]:
    enabled = settings.model_copy(
        update={"google_client_id": "id", "google_client_secret": SecretStr("secret")}
    )
    app = create_app(enabled)
    app.state.identity_provider = fake
    with TestClient(app) as test_client:
        yield test_client


def test_a_google_account_answers_409_no_password(
    google: TestClient, fake: FakeIdentityProvider, email: str
) -> None:
    fake.codes["good"] = VerifiedIdentity("google-sub-chg", email)
    started = google.get("/api/auth/google/start", follow_redirects=False)
    state = parse_qs(urlsplit(started.headers["location"]).query)["state"][0]
    google.get(
        "/api/auth/google/callback",
        params={"code": "good", "state": state},
        follow_redirects=False,
    )
    refreshed = google.post("/api/auth/refresh", headers=CSRF)
    assert refreshed.json()["user"]["has_password"] is False
    response = change(google, access_token(refreshed), "", NEW)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "no_password"


def test_the_openapi_schema_documents_the_route(client: TestClient) -> None:
    op = client.get("/openapi.json").json()["paths"][ROUTE]["post"]
    assert "204" in op["responses"]
