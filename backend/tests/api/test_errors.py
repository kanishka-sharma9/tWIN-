from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from twin.adapters.api.errors import STATUS_BY_ERROR
from twin.bootstrap import create_app
from twin.domain.errors import DomainError
from twin.settings import Settings


class PairTaken(DomainError):
    code = "pair_taken"


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)

    @app.get("/api/_test/items/{item_id}")
    def item(item_id: int) -> dict[str, int]:
        return {"id": item_id}

    @app.get("/api/_test/taken")
    def taken() -> None:
        raise PairTaken(
            "A file with this name and alter already exists.",
            details={"field": "alter"},
        )

    @app.get("/api/_test/boom")
    def boom() -> None:
        raise RuntimeError("secret internal detail")

    # The unhandled-exception handler must answer instead of the test client re-raising.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def assert_error_shape(body: dict[str, object], code: str) -> dict[str, object]:
    assert set(body) == {"error"}
    error = body["error"]
    assert isinstance(error, dict)
    assert set(error) == {"code", "message", "details"}
    assert error["code"] == code
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], dict)
    return error


def test_domain_error_uses_the_shape_and_mapped_status(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(STATUS_BY_ERROR, PairTaken, 409)
    response = client.get("/api/_test/taken")
    assert response.status_code == 409
    error = assert_error_shape(response.json(), "pair_taken")
    assert error["message"] == "A file with this name and alter already exists."
    assert error["details"] == {"field": "alter"}


def test_unmapped_domain_error_is_a_400(client: TestClient) -> None:
    assert client.get("/api/_test/taken").status_code == 400


def test_validation_failure_lists_the_fields(client: TestClient) -> None:
    response = client.get("/api/_test/items/not-a-number")
    assert response.status_code == 422
    error = assert_error_shape(response.json(), "validation_error")
    details = error["details"]
    assert isinstance(details, dict)
    fields = details["fields"]
    assert isinstance(fields, list)
    assert fields[0]["field"] == "item_id"
    assert fields[0]["reason"]


def test_unknown_route_uses_the_shape(client: TestClient) -> None:
    response = client.get("/api/nope")
    assert response.status_code == 404
    assert_error_shape(response.json(), "not_found")


def test_wrong_method_uses_the_shape(client: TestClient) -> None:
    response = client.post("/api/health")
    assert response.status_code == 405
    assert_error_shape(response.json(), "method_not_allowed")


def test_unhandled_exception_never_leaks_a_traceback(client: TestClient) -> None:
    response = client.get("/api/_test/boom")
    assert response.status_code == 500
    assert_error_shape(response.json(), "internal_error")
    assert "secret internal detail" not in response.text
    assert "Traceback" not in response.text
