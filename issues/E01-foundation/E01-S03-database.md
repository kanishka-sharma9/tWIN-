# E01-S03 PostgreSQL and migrations

- **Epic:** E01 Foundation
- **Status:** Done
- **Depends on:** E01-S02
- **Decisions:** D-019, D-020, D-026, D-028
- **Flows:** None

## Goal

The database runs with one command and its schema changes only through migrations.

## Scope

1. `docker-compose.yml` at the root with one service, `db`:
   - Image pinned to a full tag, `postgres:<major>.<minor>`, using the newest stable major at implementation time (record the version in the story's notes).
   - Named volume `twin_pgdata`.
   - Port `127.0.0.1:5432:5432`, so it is not reachable from other machines.
   - Credentials from `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB=twin`), with local-only defaults in `.env.example`.
   - A `pg_isready` healthcheck.
2. Dependencies: `sqlalchemy>=2`, `psycopg[binary]` (psycopg 3), `alembic`.
3. `adapters/persistence/`:
   - `engine.py`: builds the engine from `settings.database_url` (`postgresql+psycopg://...`), synchronous (D-026).
   - `session.py`: a session factory. One session per request, through a FastAPI dependency declared in the API adapter and wired in `bootstrap`.
   - `models.py`: the declarative base, empty for now. D-026's rules apply: 2.0 `select()` style, no lazy loading, no ORM object leaves a repository.
4. Alembic in `backend/alembic/`, with `alembic.ini` reading the URL from `Settings` and an empty baseline revision `0001_baseline`. A constraint naming convention (`pk`, `fk`, `uq`, `ix`, `ck`) is set on the base's `MetaData` now, because later stories add unique indexes and renaming them later is painful.
5. Commands, documented in README and CLAUDE.md:
   - `docker compose up -d db`
   - `uv run alembic upgrade head`
   - `uv run alembic revision -m "message"` (migrations are written by hand; autogenerate is allowed but reviewed).
6. Health: `GET /api/health` becomes `{"status": "ok", "database": "up"}`. When the database is unreachable it still answers `200` with `"database": "down"`. (Story-level choice: the endpoint reports readiness without turning into a failing liveness probe. Revisit with E10-S01.)
7. **Test database:** the suite uses `twin_test` on the same server. A session-scoped fixture creates it if missing and runs `alembic upgrade head` against it once. Each test runs inside a transaction that is rolled back, or truncates tables if a test needs real commits. The development database is never touched by tests.
8. CI: the Python job gets a `postgres` service container with a health check, and `TWIN_DATABASE_URL` pointing at it. This closes E01-S08's follow-up.

## Acceptance criteria

1. On a clean machine, `docker compose up -d db` then `uv run alembic upgrade head` succeeds. (Checked by hand once; the test fixture runs the same upgrade on `twin_test` every run, which is the automated check.)
2. `GET /api/health` reports `"database": "up"` with the container running. (API test against the real database.)
3. With the database stopped or the URL wrong, it reports `"database": "down"` and still returns `200`. (API test with a bad URL in the settings.)
4. `alembic upgrade head`, then `downgrade base`, then `upgrade head` again all work. (Test.)
5. Tests never write to the `twin` database. (Test asserts the active database name ends in `_test`.)
6. CI's Python job passes with the service container. (CI.)

## Tests

- `tests/api/test_health_db.py`, `tests/persistence/test_migrations.py`, shared fixtures in `tests/conftest.py`.

## Out of scope

Real tables (E02-S01 onward), blob storage (E05-S01), backups, production configuration.

## Open questions

None.

## Notes

- PostgreSQL image pinned to `postgres:18.6` (18 is the newest major; 19 has no image yet). Compose mounts the volume at `/var/lib/postgresql`, the path PostgreSQL 18 images expect.
- Criterion 1: `docker compose up -d db` then `uv run alembic upgrade head` succeeded by hand; the `test_database_url` fixture repeats the upgrade on `twin_test` every run.
- Criteria 2 to 5 are tests: `tests/api/test_health.py`, `tests/api/test_health_db.py`, `tests/persistence/test_migrations.py`. The "down" case points at a closed port and still gets `200`.
- Criterion 6: CI's Python job now has a `postgres:18.6` service container and runs `alembic upgrade head` before pytest.
- The engine uses `pool_pre_ping` and a 2-second connect timeout, so an unreachable database reports "down" quickly instead of hanging.
- Ruff is told `src = ["src"]` so the `backend/alembic/` folder is not mistaken for the first-party package. `alembic/` is outside mypy and ty (their settings list `src` and `tests` only).
- Tests use a rolled-back transaction fixture (`db_session`); a test that needs real commits should truncate its tables instead.
