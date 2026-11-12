# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Planning is done; implementation has not started. The code is still the `uv init --package` scaffold: a FastAPI app (`twin.bootstrap.create_app`) with `GET /api/health`, the layer folders under `backend/src/twin/`, and an architecture test that enforces the import rules (E01-S02). A PostgreSQL 18 service in `docker-compose.yml`, SQLAlchemy and Alembic with an empty baseline migration, and `/api/health` reporting `database` up or down (E01-S03). No frontend yet. The Python checks, CI (`.github/workflows/ci.yml`) and dev container (`.devcontainer/`) are in place (E01-S08, D-041). Update this file as the stories in `issues/E01-foundation/` land.

## What is being built

**tWIN!!** (D-047): a web-first, fully responsive file explorer in which every file has a Name and an **Alter** (a second, user-typed name). The (name, alter) pair must be unique across a user's vault, ignoring case; the folder plays no part. Planned stack: FastAPI + PostgreSQL (Docker Compose), structured as ports and adapters, with file bytes stored in PostgreSQL and JWT login, plus a Vite + React + TypeScript + Tailwind/shadcn frontend.

D-025 puts the Python project in `backend/` and the web app in `frontend/` (story E01-S09, done). `frontend/` holds only `.nvmrc` and a `.gitkeep` until E01-S04. The root keeps `package.json`, `package-lock.json` and `node_modules`, which only install the BMad tooling.

## Project documents

- `DECISIONS.md`: every product and technical decision with the options weighed. Entries marked **Proposed** are not confirmed by the owner, so ask before building on one. Never renumber entries.
- `FLOWS.md`: user and system flows (Mermaid).
- `issues/`: epics and stories, indexed in `issues/README.md`, which also holds the definition of done (D-049) and the rules every UI story follows. Story specs are barebones drafts that get fleshed out before implementation; each story's open questions are answered with the owner at that point.

The owner wants new decisions and flows recorded in those two files as they are made, and wants to be asked, with trade-offs, instead of having choices assumed.

## Commands

The project is managed with [uv](https://docs.astral.sh/uv/) (build backend `uv_build`, Python 3.14 pinned in `backend/.python-version`). Run the commands below from `backend/`.

```bash
uv sync                      # create .venv and install the project
docker compose up -d db      # from the repo root: start PostgreSQL (needs .env, copy .env.example)
uv run alembic upgrade head  # apply migrations
uv run alembic revision -m "message"   # new migration (write by hand; review any autogenerate)
uv run twin                  # start the API on TWIN_HOST:TWIN_PORT (default 127.0.0.1:8000)
uv add <package>             # add a runtime dependency
uv add --dev <package>       # add a dev dependency
uv build                     # build sdist + wheel into dist/
```

Checks (the same ones CI runs; Python and ruff/mypy/ty settings are in `pyproject.toml`):

```bash
uv run ruff format           # format (CI runs `--check`)
uv run ruff check --fix      # lint
uv run ty check              # type check, fast; warnings fail
uv run mypy                  # type check, strict
uv run pytest                # all tests
uv run pytest tests/api/test_health.py::test_health_ok   # one test
```

Frontend (D-038; arrives with E01-S04 in `frontend/`): Biome formats and lints, ESLint holds only the type-aware typescript-eslint and react-hooks rules, and `tsc` type-checks. CI's web job runs `npx biome ci`, `npx eslint .`, `npm run typecheck`, `npm test` and `npm run build` inside `frontend/`, so `package.json` must define the `typecheck`, `test` and `build` scripts. Node is pinned in `frontend/.nvmrc`; the dev container's Node feature version must match it.

The checkout lives in the WSL filesystem (`/home/kanis/MultiID-folder-mgmt`). Run `uv` and `git` inside WSL rather than from Windows against the `\\wsl.localhost\...` path — Windows git rejects the repo with a "dubious ownership" error, and `uv` is installed on the WSL side. From a Windows shell:

```bash
wsl -d Ubuntu -e bash -lc 'cd ~/MultiID-folder-mgmt/backend && uv run twin'
```

## Layout

- `backend/src/` layout: the importable package, the distribution and the console script are all `twin` (D-050).
- Layers (`domain`, `application`, `adapters`, `bootstrap`) and their import rules are described in D-024 and enforced by `tests/architecture/test_layers.py`. Only `bootstrap.py` wires adapters. Configuration comes from `TWIN_`-prefixed environment variables or the root `.env` (see `.env.example`). Tests use the `<database>_test` database on the same server (created and migrated by a session fixture in `tests/conftest.py`); they never touch the development database, so the `db` container must be running for `uv run pytest`.
- The console script is wired in `pyproject.toml` under `[project.scripts]` as `twin:main`, so `main()` must stay importable from the package root if the implementation moves into submodules.
