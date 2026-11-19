"""POST /api/auth/signup (E02-S02), against the real test database."""

import logging
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from twin.adapters.persistence.models import FolderRow, UserRow, VaultRow
from twin.settings import Settings

PASSWORD = "S3cret-passphrase-Zq9"


@pytest.fixture
def email(settings: Settings) -> Iterator[str]:
    """A unique address; the account it creates is removed afterwards."""
    address = f"Ada-{uuid4().hex}@Example.com"
    yield address
    engine = create_engine(settings.database_url)
    with Session(engine) as session, session.begin():
        ids = list(session.scalars(select(UserRow.id).where(UserRow.email == address)))
        vaults = list(
            session.scalars(select(VaultRow.id).where(VaultRow.owner_id.in_(ids)))
        )
        session.execute(delete(FolderRow).where(FolderRow.vault_id.in_(vaults)))
        session.execute(delete(VaultRow).where(VaultRow.owner_id.in_(ids)))
        session.execute(delete(UserRow).where(UserRow.id.in_(ids)))
    engine.dispose()


def signup(client: TestClient, email: str, password: str = PASSWORD) -> Response:
    return client.post("/api/auth/signup", json={"email": email, "password": password})


def test_valid_sign_up_creates_user_and_vault(
    client: TestClient, settings: Settings, email: str
) -> None:
    response = signup(client, f"  {email}  ")
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == email
    assert set(body) == {"user"}
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        user = session.scalars(select(UserRow).where(UserRow.email == email)).one()
        assert str(user.id) == body["user"]["id"]
        vault = session.scalars(
            select(VaultRow).where(VaultRow.owner_id == user.id)
        ).one()
        root = session.scalars(
            select(FolderRow).where(FolderRow.vault_id == vault.id)
        ).all()
        assert len(root) == 1
    engine.dispose()


def test_the_stored_hash_is_argon2id_and_not_the_password(
    client: TestClient, settings: Settings, email: str
) -> None:
    assert signup(client, email).status_code == 201
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        stored = session.scalars(
            select(UserRow.password_hash).where(UserRow.email == email)
        ).one()
    engine.dispose()
    assert stored is not None
    assert stored.startswith("$argon2id$")
    assert PASSWORD not in stored


def test_same_email_in_other_case_is_refused_with_email_taken(
    client: TestClient, email: str
) -> None:
    assert signup(client, email).status_code == 201
    again = signup(client, email.swapcase())
    assert again.status_code == 409
    error = again.json()["error"]
    assert error["code"] == "email_taken"
    assert "already exists" in error["message"]


def test_weak_password_is_refused_and_nothing_is_created(
    client: TestClient, settings: Settings, email: str
) -> None:
    for bad in ("a" * 9, "a" * 129):
        response = signup(client, email, bad)
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "weak_password"
        assert error["details"]["min_length"] == 10
        assert bad not in response.text
    assert signup(client, email, "a" * 10).status_code == 201
    assert signup(client, email.lower(), "a" * 128).status_code == 409


@pytest.mark.parametrize(
    "bad", ["", "nope", "a@@b.com", "a@b", "a b@c.com", "x" * 250 + "@b.com"]
)
def test_invalid_email_is_a_validation_error_naming_the_field(
    client: TestClient, bad: str
) -> None:
    response = signup(client, bad)
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"]["fields"][0]["field"] == "email"
    assert PASSWORD not in response.text


def test_missing_password_does_not_echo_anything_back(client: TestClient) -> None:
    response = client.post("/api/auth/signup", json={"email": "a@b.com"})
    assert response.status_code == 422
    assert response.json()["error"]["details"]["fields"][0]["field"] == "password"


def test_the_password_never_reaches_the_logs(
    client: TestClient, email: str, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.DEBUG):
        signup(client, email)
        signup(client, email)
        signup(client, email, "short")
        signup(client, "bad", PASSWORD)
    assert caplog.records
    assert PASSWORD not in caplog.text
    assert PASSWORD not in "".join(r.getMessage() for r in caplog.records)


def test_openapi_documents_the_route_without_a_password_example(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()
    assert "/api/auth/signup" in schema["paths"]
    assert PASSWORD not in client.get("/openapi.json").text
    props = schema["components"]["schemas"]["SignUpRequest"]["properties"]["password"]
    assert "example" not in props
    assert "examples" not in props
