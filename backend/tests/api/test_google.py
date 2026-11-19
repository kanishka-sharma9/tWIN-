"""Google sign-in (E02-S04) with a fake IdentityProvider. Real Google is never contacted."""

from collections.abc import Iterator
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import SecretStr
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from tests.fakes.identity import FakeIdentityProvider

from twin.adapters.persistence.models import FolderRow, UserRow, VaultRow
from twin.bootstrap import create_app
from twin.domain.identity import ExternalIdentity
from twin.settings import Settings

CSRF = {"X-Requested-With": "twin"}
PASSWORD = "S3cret-passphrase-Zq9"


@pytest.fixture
def fake() -> FakeIdentityProvider:
    return FakeIdentityProvider()


@pytest.fixture
def google(settings: Settings, fake: FakeIdentityProvider) -> Iterator[TestClient]:
    """An app with Google switched on, its provider replaced by the fake."""
    enabled = settings.model_copy(
        update={
            "google_client_id": "id",
            "google_client_secret": SecretStr("secret"),
        }
    )
    app = create_app(enabled)
    assert app.state.identity_provider is not None
    app.state.identity_provider = fake
    with TestClient(app) as test_client:
        yield test_client


def start(client: TestClient) -> str:
    """Begin the flow; returns the `state` that was sent to the provider."""
    response = client.get("/api/auth/google/start", follow_redirects=False)
    assert response.status_code == 302
    state: str = parse_qs(urlsplit(response.headers["location"]).query)["state"][0]
    return state


def callback(client: TestClient, code: str, state: str | None) -> Response:
    params = {"code": code}
    if state is not None:
        params["state"] = state
    response: Response = client.get(
        "/api/auth/google/callback", params=params, follow_redirects=False
    )
    return response


def sign_in(client: TestClient, code: str = "good") -> Response:
    return callback(client, code, start(client))


def counts(settings: Settings, address: str) -> tuple[int, int, int]:
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        users = session.scalar(
            select(func.count()).select_from(UserRow).where(UserRow.email == address)
        )
        ids = select(UserRow.id).where(UserRow.email == address)
        vaults = session.scalar(
            select(func.count()).select_from(VaultRow).where(VaultRow.owner_id.in_(ids))
        )
        folders = session.scalar(
            select(func.count())
            .select_from(FolderRow)
            .join(VaultRow, VaultRow.id == FolderRow.vault_id)
            .where(VaultRow.owner_id.in_(ids))
        )
    engine.dispose()
    assert users is not None
    assert vaults is not None
    assert folders is not None
    return users, vaults, folders


def me(client: TestClient) -> dict[str, object]:
    """Trade the refresh cookie for an access token and ask who is logged in."""
    refreshed = client.post("/api/auth/refresh", headers=CSRF)
    assert refreshed.status_code == 200
    token = refreshed.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def test_providers_reports_google_on(google: TestClient) -> None:
    assert google.get("/api/auth/providers").json() == {"google": True}


def test_start_redirects_to_the_provider_with_state_and_pkce(
    google: TestClient, fake: FakeIdentityProvider
) -> None:
    response = google.get("/api/auth/google/start", follow_redirects=False)
    assert response.status_code == 302
    location = urlsplit(response.headers["location"])
    query = parse_qs(location.query)
    assert location.netloc == "idp.test"
    assert len(query["state"][0]) >= 32
    assert query["code_challenge_method"] == ["S256"]
    assert len(query["code_challenge"][0]) == 43
    cookie = response.headers["set-cookie"]
    assert cookie.startswith("oauth_state=")
    assert "HttpOnly" in cookie
    assert "Path=/api/auth/google" in cookie
    assert "SameSite=lax" in cookie
    assert "Max-Age=600" in cookie
    assert "no-store" in response.headers["cache-control"]


def test_first_sign_in_creates_a_vault_and_the_second_lands_in_the_same_one(
    google: TestClient, fake: FakeIdentityProvider, settings: Settings, email: str
) -> None:
    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    first = sign_in(google)
    assert first.status_code == 302
    assert first.headers["location"] == "/"
    assert "refresh_token=" in first.headers["set-cookie"] or any(
        "refresh_token=" in h for h in first.headers.get_list("set-cookie")
    )
    first_user = me(google)
    assert first_user["email"] == email
    assert first_user["has_password"] is False
    assert counts(settings, email) == (1, 1, 1)

    google.cookies.clear()
    second = sign_in(google)
    assert second.headers["location"] == "/"
    assert me(google)["id"] == first_user["id"]
    assert counts(settings, email) == (1, 1, 1)


def test_callback_sends_the_pkce_verifier_that_matches_the_challenge(
    google: TestClient, fake: FakeIdentityProvider, email: str
) -> None:
    from twin.adapters.auth.oauth_state import code_challenge

    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    response = google.get("/api/auth/google/start", follow_redirects=False)
    query = parse_qs(urlsplit(response.headers["location"]).query)
    callback(google, "good", query["state"][0])
    code, verifier = fake.exchanges[0]
    assert code == "good"
    assert code_challenge(verifier) == query["code_challenge"][0]


def test_email_of_a_password_account_creates_nothing_and_lands_on_login(
    google: TestClient, fake: FakeIdentityProvider, settings: Settings, email: str
) -> None:
    signup = google.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert signup.status_code == 201
    google.cookies.clear()
    fake.codes["good"] = ExternalIdentity("google-sub-9", email.lower())
    response = sign_in(google)
    assert response.status_code == 302
    assert response.headers["location"] == "/login?error=account_exists"
    assert not any(
        h.startswith("refresh_token=") and "Max-Age=0" not in h
        for h in response.headers.get_list("set-cookie")
    )
    assert counts(settings, email) == (1, 1, 1)
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        user = session.scalars(select(UserRow).where(UserRow.email == email)).one()
        assert user.google_subject is None
    engine.dispose()
    assert google.post("/api/auth/refresh", headers=CSRF).status_code == 401


def test_a_google_account_has_no_password_to_log_in_with(
    google: TestClient, fake: FakeIdentityProvider, email: str
) -> None:
    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    sign_in(google)
    google.cookies.clear()
    login = google.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 401


def test_state_mismatch_is_refused_and_the_provider_is_not_called(
    google: TestClient, fake: FakeIdentityProvider, settings: Settings, email: str
) -> None:
    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    start(google)
    response = callback(google, "good", "not-the-state")
    assert response.headers["location"] == "/login?error=google_failed"
    assert fake.exchanges == []
    assert counts(settings, email) == (0, 0, 0)


def test_callback_without_the_state_cookie_is_refused(
    google: TestClient, fake: FakeIdentityProvider, settings: Settings, email: str
) -> None:
    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    state = start(google)
    google.cookies.clear()
    response = callback(google, "good", state)
    assert response.headers["location"] == "/login?error=google_failed"
    assert fake.exchanges == []
    assert counts(settings, email) == (0, 0, 0)


def test_state_cookie_cannot_be_replayed_after_a_successful_sign_in(
    google: TestClient, fake: FakeIdentityProvider, email: str
) -> None:
    fake.codes["good"] = ExternalIdentity("google-sub-1", email)
    state = start(google)
    assert callback(google, "good", state).headers["location"] == "/"
    # The browser dropped the cookie when the callback answered; a replay has none.
    again = callback(google, "good", state)
    assert again.headers["location"] == "/login?error=google_failed"


@pytest.mark.parametrize("missing", ["code", "state"])
def test_callback_without_code_or_state_is_refused(
    google: TestClient, fake: FakeIdentityProvider, missing: str
) -> None:
    state = start(google)
    params = {"code": "good", "state": state}
    del params[missing]
    response = google.get(
        "/api/auth/google/callback", params=params, follow_redirects=False
    )
    assert response.headers["location"] == "/login?error=google_failed"
    assert fake.exchanges == []


def test_person_declining_at_google_lands_on_login(
    google: TestClient, fake: FakeIdentityProvider
) -> None:
    state = start(google)
    response = google.get(
        "/api/auth/google/callback",
        params={"error": "access_denied", "state": state},
        follow_redirects=False,
    )
    assert response.headers["location"] == "/login?error=google_failed"


def test_rejected_code_lands_on_login_and_creates_nothing(
    google: TestClient, fake: FakeIdentityProvider, settings: Settings, email: str
) -> None:
    response = sign_in(google, "unknown-code")
    assert response.headers["location"] == "/login?error=google_failed"
    assert counts(settings, email) == (0, 0, 0)


def test_disabled_provider_answers_404_and_the_app_works(
    client: TestClient, email: str
) -> None:
    assert client.get("/api/auth/providers").json() == {"google": False}
    for path in ("/api/auth/google/start", "/api/auth/google/callback"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "provider_disabled"
    signup = client.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert signup.status_code == 201
    client.cookies.clear()
    login = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200


@pytest.mark.parametrize(
    "update",
    [
        {"google_client_id": "id"},
        {"google_client_secret": SecretStr("s")},
        {"google_client_id": "id", "google_client_secret": SecretStr("")},
        {
            "google_client_id": "id",
            "google_client_secret": SecretStr("s"),
            "google_redirect_uri": "",
        },
    ],
)
def test_google_stays_off_unless_all_three_settings_are_set(
    settings: Settings, update: dict[str, object]
) -> None:
    app = create_app(settings.model_copy(update=update))
    assert app.state.identity_provider is None


def test_all_three_settings_switch_the_real_provider_on(settings: Settings) -> None:
    from twin.adapters.auth.google_identity import GoogleIdentityProvider

    app = create_app(
        settings.model_copy(
            update={
                "google_client_id": "id",
                "google_client_secret": SecretStr("s"),
            }
        )
    )
    assert isinstance(app.state.identity_provider, GoogleIdentityProvider)
