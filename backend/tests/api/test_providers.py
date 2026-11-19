"""GET /api/auth/providers and when Google counts as configured (E02-S04)."""

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from twin.adapters.auth.google_identity import GoogleIdentityProvider
from twin.bootstrap import create_app
from twin.settings import Settings


def test_providers_says_false_when_google_is_not_configured(
    client: TestClient,
) -> None:
    response = client.get("/api/auth/providers")
    assert response.status_code == 200
    assert response.json() == {"google": False}


def test_providers_says_true_when_google_is_configured(settings: Settings) -> None:
    enabled = settings.model_copy(
        update={"google_client_id": "id", "google_client_secret": SecretStr("s")}
    )
    with TestClient(create_app(enabled)) as test_client:
        assert test_client.get("/api/auth/providers").json() == {"google": True}


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

    app = create_app(
        settings.model_copy(
            update={
                "google_client_id": "id",
                "google_client_secret": SecretStr("s"),
            }
        )
    )
    assert isinstance(app.state.identity_provider, GoogleIdentityProvider)
