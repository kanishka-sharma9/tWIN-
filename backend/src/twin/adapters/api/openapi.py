import json
from pathlib import Path

from fastapi import FastAPI

# backend/src/twin/adapters/api/openapi.py -> the repository root.
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_OPENAPI_PATH = REPO_ROOT / "frontend" / "src" / "api" / "openapi.json"


def export_openapi(app: FastAPI, path: Path = DEFAULT_OPENAPI_PATH) -> Path:
    """Write the OpenAPI schema without starting a server."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")
    return path
