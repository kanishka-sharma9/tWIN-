from fastapi.testclient import TestClient

from twin.bootstrap import create_app
from twin.settings import Settings


def test_health_ok() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
