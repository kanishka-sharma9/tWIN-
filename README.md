# tWIN!!

A web-first file explorer in which every file has a Name and an Alter. See `DECISIONS.md` for the design and `issues/` for the backlog.

## Setup

Work inside WSL (Ubuntu) on Windows, or use the [dev container](#dev-container) instead. After the steps below, `scripts/check-env.sh` checks them all at once.

### 1. Docker Desktop

Docker Desktop > Settings > Resources > WSL integration > turn on Ubuntu.

Proof, inside WSL:

```bash
docker compose version
```

### 2. Node

Install [nvm](https://github.com/nvm-sh/nvm#installing-and-updating) in WSL, then read the version from `frontend/.nvmrc` (Node 26):

```bash
cd frontend && nvm install
```

Proof: `node --version` prints `v26.x`. WSL's apt Node 18 is too old for Vite.

### 3. Python

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then in `backend/` (it fetches Python 3.14 from `backend/.python-version`):

```bash
cd backend && uv sync
```

Proof: `uv run python --version` prints `Python 3.14.x`.

### 4. Git

Run `git` inside WSL, not from Windows against the `\\wsl.localhost\...` path. Windows git rejects that checkout with a "dubious ownership" error because the files belong to the WSL user, not your Windows account.

### 5. Check everything

```bash
scripts/check-env.sh
```

It prints each tool's version and exits non-zero naming the first one that is missing or too old.

## Dev container

As an alternative to the steps above, open the folder in VS Code and choose **Reopen in Container**. It gives the same toolchain (uv, Node 26) with Docker-in-Docker (D-041), so `docker compose up` works inside it.

## Ports

| Port | Service |
|---|---|
| 5432 | PostgreSQL |
| 8000 | API |
| 5173 | Web |

## Troubleshooting

- **`docker compose version` fails in WSL:** WSL integration is off. Turn it on for Ubuntu in Docker Desktop (step 1), then restart the WSL terminal.
- **`node --version` prints v18:** you are on WSL's apt Node. Run `nvm install` in `frontend/` and open a new shell.
- **`uv: command not found` from a script or `wsl -e`:** uv is added to PATH by your login profile. Run through a login shell: `wsl -d Ubuntu -e bash -lc 'cd ~/MultiID-folder-mgmt/backend && uv run pytest'`.
