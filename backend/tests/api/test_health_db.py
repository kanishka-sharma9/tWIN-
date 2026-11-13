from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from twin.bootstrap import create_app
from twin.settings import Settings


def test_health_reports_database_down_but_still_200() -> None:
    unreachable = Settings(
        database_url="postgresql+psycopg://twin:twin@127.0.0.1:1/twin"
    )
    with TestClient(create_app(unreachable)) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "down"}


def test_tests_run_against_the_test_database(db_session: Session) -> None:
    name = db_session.execute(text("SELECT current_database()")).scalar()
    assert isinstance(name, str)
    assert name.endswith("_test")
