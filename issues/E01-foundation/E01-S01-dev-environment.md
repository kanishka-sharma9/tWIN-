# E01-S01 Developer environment

- **Epic:** E01 Foundation
- **Status:** Ready
- **Depends on:** E01-S09 (so the README describes the final layout)
- **Decisions:** D-020, D-038, D-041
- **Flows:** None

## Goal

Anyone on the team can set up the required tools on Windows with WSL, or open the dev container instead, by following one README.

## Scope

1. Documentation and checks only; no application code.
2. `README.md` gets a **Setup** section with these steps, each ending in a command that proves it worked:
   - **Docker Desktop:** Settings > Resources > WSL integration > turn on Ubuntu. Proof: `docker compose version` inside WSL.
   - **Node:** install nvm in WSL, then `nvm install` in `frontend/` (reads `frontend/.nvmrc`, Node 26). Proof: `node --version` prints v26.x. WSL's apt Node 18 is too old for Vite.
   - **Python:** `uv sync` in `backend/` (fetches Python 3.14 from `backend/.python-version`). Proof: `uv run python --version`.
   - **Git:** run git inside WSL; explain the "dubious ownership" error from Windows git.
3. A short **Dev container** alternative: "Reopen in Container" gives the same toolchain, with Docker-in-Docker (D-041).
4. A **Ports** table: 5432 PostgreSQL, 8000 API, 5173 web.
5. A **Troubleshooting** list: Docker integration off, wrong Node version, `uv` missing from PATH in a non-login shell (`bash -lc`).
6. `scripts/check-env.sh`: prints each tool's version and exits non-zero naming the first one that is missing or too old. It checks `docker compose version`, `node` major equals `.nvmrc`, `uv` present, `python` 3.14.

## Acceptance criteria

1. `docker compose version`, `node --version` and `uv run python --version` all work inside WSL. (Verified by `scripts/check-env.sh` exiting 0.)
2. Following the README from a clean WSL user reaches a working toolchain. (Manual: the owner follows it once on a fresh WSL user or the dev container; recorded in the story's notes. This cannot be automated.)
3. `check-env.sh` fails with a clear message when Node is too old. (Automated: a pytest that runs the script with a fake `node` first on PATH.)

## Tests

- One pytest in `backend/tests/` that runs `scripts/check-env.sh` with stubbed tools on PATH: all good, Node too old, Docker missing.

## Out of scope

Installing PostgreSQL (E01-S03), the frontend toolchain beyond Node (E01-S04), hosting setup (E10-S01).

## Open questions

None.
