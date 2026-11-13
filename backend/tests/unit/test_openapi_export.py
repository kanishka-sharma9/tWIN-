import json
from pathlib import Path

from twin.adapters.api.openapi import export_openapi
from twin.bootstrap import create_app
from twin.settings import Settings


def test_export_contains_health_and_the_error_schema(tmp_path: Path) -> None:
    target = export_openapi(
        create_app(Settings()), tmp_path / "nested" / "openapi.json"
    )
    spec = json.loads(target.read_text())
    assert "/api/health" in spec["paths"]
    assert "ErrorResponse" in spec["components"]["schemas"]
    responses = spec["paths"]["/api/health"]["get"]["responses"]
    assert responses["404"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ErrorResponse"
    )


def test_export_is_stable(tmp_path: Path) -> None:
    app = create_app(Settings())
    first = export_openapi(app, tmp_path / "a.json").read_text()
    second = export_openapi(create_app(Settings()), tmp_path / "b.json").read_text()
    assert first == second
