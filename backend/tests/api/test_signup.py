from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, text

from twin.settings import Settings

PASSWORD = "correct horse battery"
EMAILS = ("ada@signup.test", "ADA@signup.test", "bad@signup.test")


@pytest.fixture(autouse=True)
def clean_users(settings: Settings) -> Iterator[None]:
    def wipe() -> None:
        engine = create_engine(settings.database_url)
        with engine.begin() as connection:
            params = {"emails": [e.lower() for e in EMAILS]}
            where = (
                "owner_id IN (SELECT id FROM users WHERE lower(email) = ANY(:emails))"
            )
            connection.execute(
                text(
                    "DELETE FROM folders WHERE vault_id IN (SELECT id FROM vaults WHERE "
                    + where
                    + ")"
                ),
                params,
            )
            connection.execute(text("DELETE FROM vaults WHERE " + where), params)
            connection.execute(
                text("DELETE FROM users WHERE lower(email) = ANY(:emails)"), params
            )
        engine.dispose()

    wipe()
    yield
    wipe()


def signup(client: TestClient, email: str, password: str = PASSWORD) -> Response:
    response: Response = client.post(
        "/api/auth/signup", json={"email": email, "password": password}
    )
    return response


def test_signup_creates_user_vault_and_root(
    client: TestClient, settings: Settings
) -> None:
    response = signup(client, "ada@signup.test")
    assert response.status_code == 201
    user = response.json()["user"]
    assert user["email"] == "ada@signup.test"
    assert set(user) == {"id", "email"}
    assert PASSWORD not in response.text
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT u.password_hash, count(DISTINCT v.id), count(f.id) FROM users u "
                "JOIN vaults v ON v.owner_id = u.id JOIN folders f ON f.vault_id = v.id "
                "WHERE u.id = :id GROUP BY u.password_hash"
            ),
            {"id": user["id"]},
        ).one()
    engine.dispose()
    assert row[0].startswith("$argon2id$")
    assert PASSWORD not in row[0]
    assert (row[1], row[2]) == (1, 1)


def test_duplicate_email_in_any_case_is_refused_with_account_exists(
    client: TestClient,
) -> None:
    assert signup(client, "ada@signup.test").status_code == 201
    response = signup(client, "ADA@signup.test")
    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "email_taken"
    assert "already exists" in error["message"]


def test_invalid_email_is_refused(client: TestClient) -> None:
    response = signup(client, "bad@signup")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_email"


@pytest.mark.parametrize("password", ["short", "x" * 129])
def test_password_length_is_refused(client: TestClient, password: str) -> None:
    response = signup(client, "bad@signup.test", password)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "weak_password"


def test_missing_fields_use_the_validation_error_shape(client: TestClient) -> None:
    response = client.post("/api/auth/signup", json={"email": "bad@signup.test"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_the_password_is_not_logged(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level("DEBUG"):
        signup(client, "ada@signup.test")
        signup(client, "ada@signup.test")
    assert PASSWORD not in caplog.text
