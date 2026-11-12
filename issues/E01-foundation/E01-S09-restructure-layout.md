# E01-S09 Restructure into backend/ and frontend/

- **Epic:** E01 Foundation
- **Status:** Draft (spec complete; waits for D-050 to be confirmed)
- **Depends on:** None
- **Decisions:** D-025, D-041, D-047, D-050 (Proposed)
- **Flows:** None

## Goal

The repository matches the agreed layout, and the Python package carries the product's name, before any feature code is written. This is the first story to build.

## Answers already given (2026-11-11)

- `.python-version` moves to `backend/` and `.nvmrc` moves to `frontend/`.
- The Python package and console script are renamed to match tWIN!!; the repository keeps its name.
- The new name is `twin` (D-050, Proposed): a valid identifier, short, and free of the `!!`.

## Scope

1. Move with `git mv`, so history follows:
   - `pyproject.toml`, `uv.lock`, `.python-version`, `src/`, `tests/` into `backend/`.
   - `.nvmrc` into `frontend/` (creating the folder with a `.gitkeep` until E01-S04 fills it).
2. Rename inside `backend/`:
   - `src/multiid_folder_mgmt/` becomes `src/twin/`.
   - `[project] name` becomes `twin`; `[project.scripts]` becomes `twin = "twin:main"`.
   - `tests/test_smoke.py` imports `twin`.
   - Regenerate `uv.lock` with `uv lock`.
3. `.github/workflows/ci.yml`:
   - Python job: `defaults.run.working-directory: backend`, and `setup-uv` is told where `pyproject.toml` and `uv.lock` live (`working-directory: backend`, cache key `backend/uv.lock`).
   - Web job: every `web/` becomes `frontend/`; `node-version-file: frontend/.nvmrc`.
4. `.devcontainer/`:
   - `post-create.sh` runs `uv sync` in `backend/` and `npm ci` in `frontend/` when `frontend/package.json` exists.
   - The comment in `devcontainer.json` points at `frontend/.nvmrc`.
   - Forwarded ports are unchanged.
5. Documents: CLAUDE.md (status, commands, layout), D-025's tree and D-041's text (add a dated note rather than rewriting history), `README.md` stub paths.
6. Leave at the root: `package.json`, `package-lock.json` and `node_modules` (they only install the BMad tooling), `.gitignore`, `docker-compose.yml` (arrives in E01-S03), `.github/`, `.devcontainer/`, the documents.
7. Extend `.gitignore` for `backend/.venv`, `backend/.mypy_cache`, `backend/.ruff_cache`, `backend/.pytest_cache`, `frontend/node_modules`, `frontend/dist`.

## Acceptance criteria

1. From `backend/`, `uv sync --locked`, `ruff format --check`, `ruff check`, `ty check`, `mypy` and `pytest` all pass. (Verified by running them.)
2. `uv run twin` prints the placeholder greeting. (Verified by `test_main_runs` calling `twin.main`.)
3. CI's Python job runs from `backend/` and passes, and its web job looks in `frontend/`. (Verified on the first push; the repository has no remote yet, so this stays "not checked" until it has one, as in E01-S08.)
4. `grep -rniE "web/|multiid_folder_mgmt|multiid-folder-mgmt"` over tracked files finds nothing except the history in E01-S08, the repository name, and dated notes in DECISIONS.md. (Verified by running the grep.)
5. No `pyproject.toml`, `.python-version` or `uv.lock` remains at the root. (Verified by listing.)
6. The dev container builds and `uv run pytest` passes inside it. Not checkable until Docker Desktop's WSL integration is on (D-020); written reason recorded as in E01-S08.

## Tests

- The existing smoke test, renamed to import `twin`, is the automated check for criterion 2.
- Criteria 4 and 5 are one-off shell checks run while implementing; they are not worth a permanent test.

## Order of work

Move files, fix `pyproject.toml`, `uv lock`, run the checks, then CI, dev container, documents, then the grep.

## Run from WSL

Run `git` and `uv` inside WSL (CLAUDE.md): `wsl -d Ubuntu -e bash -lc 'cd ~/MultiID-folder-mgmt && ...'`.

## Open questions

- Confirm `twin` as the package and script name (D-050). If another name is chosen, only the spelling in scope item 2 changes.
