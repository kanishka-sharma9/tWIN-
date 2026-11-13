# E01-S02 Backend skeleton and layering

- **Epic:** E01 Foundation
- **Status:** Done
- **Depends on:** E01-S01, E01-S09
- **Decisions:** D-018, D-024, D-025, D-026, D-050
- **Flows:** FLOWS.md 1

## Goal

The API starts, and the layer boundaries exist and are enforced before any feature is written.

## Scope

1. Dependencies (`uv add`): `fastapi`, `uvicorn[standard]`, `pydantic-settings`. Dev: `httpx` (for the test client).
2. Folders under `backend/src/twin/`, each with an `__init__.py` and a one-line docstring saying what belongs there:

```
domain/                 entities, value objects, rules, domain errors
application/            use cases
application/ports/      one small interface per outside dependency
adapters/api/           routers, request and response schemas, error mapping
adapters/persistence/   filled by E01-S03
adapters/blobs/         filled by E05-S01
adapters/auth/          filled by E02
settings.py             Settings (pydantic-settings)
bootstrap.py            composition root: builds the app from Settings
```

3. `Settings`: environment variables with prefix `TWIN_`, read once. Fields now: `host` (default `127.0.0.1`) and `port` (default 8000); E01-S03 adds `database_url`. A `.env.example` lists them; `.env` is git-ignored.
4. `bootstrap.create_app(settings: Settings | None = None) -> FastAPI` builds the app, mounts the API router under `/api`, and is the only place adapters are wired. Tests call it with their own settings.
5. `GET /api/health` returns `200 {"status": "ok"}` (E01-S03 adds a `database` field).
6. `twin.main()` starts uvicorn on `settings.host:settings.port` with the app from `create_app` (uvicorn's factory mode, so `--reload` works in development). `uv run twin` runs it. `main()` stays importable from the package root (CLAUDE.md).
7. **Layer rule as a test**, `tests/architecture/test_layers.py`, walking every module's imports with `ast`:
   - `twin.domain` imports nothing from `twin.application`, `twin.adapters`, `twin.bootstrap`, `fastapi`, `starlette`, `pydantic_settings`, `sqlalchemy`, `psycopg`, `alembic` or `uvicorn`.
   - `twin.application` imports nothing from `twin.adapters`, `twin.bootstrap` or those frameworks.
   - `twin.adapters.*` never import `twin.bootstrap`.
   - The domain keeps an explicit allow-list of third-party packages (empty at first), so adding one is a visible diff.

   An AST walk needs no new dependency. `import-linter` is the alternative if the rules grow; it would replace this one file.

## Acceptance criteria

1. `GET /api/health` answers `200` with `{"status": "ok"}`. (API test with `TestClient(create_app(...))`.)
2. `uv run twin` starts the server and the same endpoint answers over real HTTP. (Checked by hand once; the in-process test covers the logic.)
3. A test fails if `domain` imports FastAPI or SQLAlchemy. (The architecture test is itself proven by a second test that feeds it a deliberately bad module source and expects a violation.)
4. Settings read `TWIN_PORT` from the environment. (Unit test with `monkeypatch`.)
5. `ruff`, `ty`, `mypy --strict` and `pytest` pass.

## Tests

- `tests/api/test_health.py`, `tests/unit/test_settings.py`, `tests/architecture/test_layers.py`.

## Out of scope

Database (E01-S03), error response shape and OpenAPI export (E01-S06), authentication (E02).

## Open questions

None.

## Notes

- Criteria 1, 3, 4 and 5 are covered by tests and the local checks (`tests/api/test_health.py`, `tests/architecture/test_layers.py`, `tests/unit/test_settings.py`).
- Criterion 2 was checked by hand: `TWIN_PORT=8765 uv run twin`, then `curl localhost:8765/api/health` returned `{"status":"ok"}`.
- The old `tests/test_smoke.py` was removed: `main()` now starts a server, so the test that called it no longer fits. `tests/unit/test_settings.py` checks `main()` by replacing `uvicorn.run`.
- `pytest` runs with `--import-mode=importlib` so test files in different folders can share a name.
- `httpx` brings a Starlette deprecation warning that points to `httpx2`. The story names `httpx`, so it stays; revisit if the warning becomes an error.
- Settings read the repository-root `.env` (the same file E01-S03's Docker Compose will use) and ignore variables that are not `TWIN_`-prefixed.
- Review change: the layer test reads import statements with regular expressions instead of Python's `ast` module (the owner does not trust `ast`). Only statements that start a line are read, which covers plain, aliased, relative and multi-line parenthesised imports; tests prove it.
