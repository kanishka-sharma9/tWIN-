# E01-S08 CI and dev container

- **Epic:** E01 Foundation
- **Status:** Done
- **Depends on:** None
- **Decisions:** D-038, D-041
- **Flows:** None

## Goal

Every push and pull request runs the checks, and a dev container gives anyone the same toolchain as WSL.

## Scope

- GitHub Actions workflow with a Python job (Ruff format and lint, ty, mypy, pytest) and a web job (Biome, ESLint, type check, Vitest, build) that skips itself until `web/package.json` exists.
- Ruff, ty, mypy and pytest added as dev dependencies, configured in `pyproject.toml`, and locked in `uv.lock`.
- A smoke test so pytest has something to collect until E01-S07 lays out the suites.
- `.devcontainer/` with uv, Node 26 and Docker-in-Docker, plus editor extensions for every tool.
- Node pinned in `.nvmrc`.

## Acceptance criteria

- Every Python check passes locally on the scaffold.
- The workflow passes on GitHub. Not checked yet: the repository has no commits and no remote.
- The dev container builds and `uv run pytest` passes inside it. Not checked yet: Docker Desktop's WSL integration is off (D-020).

## Follow-ups

- E01-S04 adds Biome and ESLint configs plus the `typecheck`, `test` and `build` npm scripts that the web job calls.
- E01-S03 and E01-S07 add a PostgreSQL service to the Python job when the API tests arrive.
