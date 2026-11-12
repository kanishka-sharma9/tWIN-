# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Planning is done; implementation has not started. The code is still the `uv init --package` scaffold: a placeholder `main()` in `src/multiid_folder_mgmt/__init__.py`, an empty README, no runtime dependencies and no frontend. The Python checks, CI (`.github/workflows/ci.yml`) and dev container (`.devcontainer/`) are in place (E01-S08, D-041). Update this file as the stories in `issues/E01-foundation/` land.

## What is being built

**tWIN!!** (D-047): a web-first, fully responsive file explorer in which every file has a Name and an **Alter** (a second, user-typed name). The (name, alter) pair must be unique across a user's vault, ignoring case; the folder plays no part. Planned stack: FastAPI + PostgreSQL (Docker Compose), structured as ports and adapters, with file bytes stored in PostgreSQL and JWT login, plus a Vite + React + TypeScript + Tailwind/shadcn frontend.

D-025 puts the Python project in `backend/` and the web app in `frontend/`. That move is story E01-S09 and has not happened yet, so the commands and paths below describe the current root layout, and CI still looks for `web/`.

## Project documents

- `DECISIONS.md`: every product and technical decision with the options weighed. Entries marked **Proposed** are not confirmed by the owner, so ask before building on one. Never renumber entries.
- `FLOWS.md`: user and system flows (Mermaid).
- `issues/`: epics and stories, indexed in `issues/README.md`, which also holds the definition of done (D-049) and the rules every UI story follows. Story specs are barebones drafts that get fleshed out before implementation; each story's open questions are answered with the owner at that point.

The owner wants new decisions and flows recorded in those two files as they are made, and wants to be asked, with trade-offs, instead of having choices assumed.

## Commands

The project is managed with [uv](https://docs.astral.sh/uv/) (build backend `uv_build`, Python 3.14 pinned in `.python-version`).

```bash
uv sync                      # create .venv and install the project
uv run multiid-folder-mgmt   # run the CLI entry point
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
uv run pytest tests/test_smoke.py::test_main_runs   # one test
```

Frontend (D-038; arrives with E01-S04 in `web/`): Biome formats and lints, ESLint holds only the type-aware typescript-eslint and react-hooks rules, and `tsc` type-checks. CI's web job runs `npx biome ci`, `npx eslint .`, `npm run typecheck`, `npm test` and `npm run build` inside `web/`, so `package.json` must define the `typecheck`, `test` and `build` scripts. Node is pinned in `.nvmrc`; the dev container's Node feature version must match it.

The checkout lives in the WSL filesystem (`/home/kanis/MultiID-folder-mgmt`). Run `uv` and `git` inside WSL rather than from Windows against the `\\wsl.localhost\...` path — Windows git rejects the repo with a "dubious ownership" error, and `uv` is installed on the WSL side. From a Windows shell:

```bash
wsl -d Ubuntu -e bash -lc 'cd ~/MultiID-folder-mgmt && uv run multiid-folder-mgmt'
```

## Layout

- `src/` layout: the importable package is `multiid_folder_mgmt` (underscores); the distribution and console script are `multiid-folder-mgmt` (hyphens).
- The console script is wired in `pyproject.toml` under `[project.scripts]` as `multiid_folder_mgmt:main`, so `main()` must stay importable from the package root if the implementation moves into submodules.
