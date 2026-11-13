from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from twin.bootstrap import create_app
from twin.settings import Settings

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def alembic_config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


@pytest.fixture
def alembic_cfg(test_database_url: str) -> Config:
    return alembic_config(test_database_url)


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """URL of `<database>_test` on the configured server; created and migrated once per run.

    The development database is never touched by tests.
    """
    url = make_url(Settings().database_url)
    assert url.database is not None
    test_url = url.set(database=f"{url.database}_test")
    assert test_url.database is not None

    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": test_url.database},
        ).scalar()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    admin.dispose()

    rendered = test_url.render_as_string(hide_password=False)
    command.upgrade(alembic_config(rendered), "head")
    return rendered


@pytest.fixture
def settings(test_database_url: str) -> Settings:
    return Settings(database_url=test_database_url)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture
def db_session(test_database_url: str) -> Iterator[Session]:
    """A session whose work is rolled back when the test ends."""
    engine = create_engine(test_database_url)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()
