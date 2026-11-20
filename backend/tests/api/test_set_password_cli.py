"""`twin set-password` as a real process against the test database, checked through the API."""

import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tests.api.test_sessions import PASSWORD, login, refresh_cookie

from twin.adapters.persistence.engine import create_db_engine
from twin.adapters.persistence.models import UserRow
from twin.adapters.persistence.repositories import SqlUnitOfWork
from twin.adapters.persistence.session import create_session_factory
from twin.adapters.system_clock import SystemClock
from twin.application.create_user import CreateUser
from twin.settings import Settings

NEW = "A brand new passphrase 42"
CODE = "from twin import main; main()"


def run_cli(
    settings: Settings, *args: str, stdin: str = f"{NEW}\n"
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "TWIN_DATABASE_URL": settings.database_url,
        "TWIN_JWT_SECRET": "",
    }
    return subprocess.run(
        [sys.executable, "-c", CODE, "set-password", *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )


@pytest.fixture
def account(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/signup", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 201
    client.cookies.clear()
    return email


def test_the_new_password_logs_in_and_the_old_one_does_not(
    client: TestClient, settings: Settings, account: str
) -> None:
    result = run_cli(settings, account.lower())
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        f"Password updated for {account}. All sessions were ended.\n"
    )
    assert login(client, account, NEW).status_code == 200
    assert login(client, account, PASSWORD).status_code == 401


def test_the_password_is_not_in_argv_or_in_any_output(
    settings: Settings, account: str
) -> None:
    result = run_cli(settings, account)
    assert NEW not in result.stdout + result.stderr
    assert NEW not in f"-c {CODE} set-password {account}"


def test_existing_refresh_tokens_stop_working(
    client: TestClient, settings: Settings, account: str
) -> None:
    first = login(client, account, PASSWORD)
    cookie = refresh_cookie(first)
    assert run_cli(settings, account).returncode == 0
    client.cookies.clear()
    response = client.post(
        "/api/auth/refresh",
        headers={"X-Requested-With": "twin"},
        cookies={"refresh_token": cookie},
    )
    assert response.status_code == 401


def test_an_unknown_email_is_refused_and_nothing_is_created(
    settings: Settings,
) -> None:
    result = run_cli(settings, "nobody-at-all@example.com")
    assert result.returncode == 1
    assert result.stderr == "No account with that email.\n"
    assert result.stdout == ""
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        assert (
            session.query(UserRow)
            .filter(UserRow.email == "nobody-at-all@example.com")
            .count()
            == 0
        )
    engine.dispose()


def test_a_short_password_is_refused_and_the_old_one_still_works(
    client: TestClient, settings: Settings, account: str
) -> None:
    result = run_cli(settings, account, stdin="short\n")
    assert result.returncode == 1
    assert result.stderr == "Use 10 to 128 characters for the password.\n"
    assert login(client, account, PASSWORD).status_code == 200


def test_a_google_only_account_is_refused(settings: Settings, email: str) -> None:
    clock = SystemClock()
    CreateUser(
        lambda: SqlUnitOfWork(
            create_session_factory(create_db_engine(settings.database_url))
        ),
        clock,
    ).execute(email, google_subject=f"sub-{email}")
    result = run_cli(settings, email)
    assert result.returncode == 1
    assert result.stderr == "That account signs in with Google and has no password.\n"
    assert result.stdout == ""
