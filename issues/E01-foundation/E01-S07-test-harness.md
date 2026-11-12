# E01-S07 Test and lint harness

- **Epic:** E01 Foundation
- **Status:** Ready
- **Depends on:** E01-S03, E01-S04
- **Decisions:** D-022, D-038, D-043, D-044, D-049
- **Flows:** None

## Goal

Every kind of check runs with one documented command, including running a single test.

## Scope

### Backend (pytest)

1. Layout under `backend/tests/`:
   - `unit/`: rule tests using in-memory fakes, no database, no network. Fakes live in `tests/fakes/` and implement the ports, so they double as proof that the ports are small (D-024).
   - `api/`: tests through `TestClient` against the real PostgreSQL test database (E01-S03's fixtures).
   - `architecture/` and `persistence/`: already created by E01-S02 and E01-S03.
2. Markers declared in `pyproject.toml` (`--strict-markers` is already on): `unit`, `api`, applied automatically by folder through `conftest.py`, so `pytest -m unit` runs the fast set.
3. A fixture that builds an authenticated client is deliberately left for E02; this story only provides the unauthenticated client.

### Frontend

4. Vitest conventions on top of E01-S04's setup: `src/test/setup.ts` (Testing Library matchers, `fetch` mocking helper), `renderWithProviders()` that wraps a component in the router and Query providers, and tests next to the code they cover (`Thing.test.tsx`).
5. **Playwright** in `frontend/e2e/`:
   - Browsers: Chromium, Firefox and WebKit (D-044).
   - Projects: each browser at **desktop** (1280×800) and **phone** (a device preset, 390×844), six projects (D-043).
   - `webServer` entries start the Vite dev server; the API and database are expected to be running (documented), with an optional `npm run e2e:full` that also starts them.
   - One smoke test: the home page loads and shows the health result; no console errors; no horizontal scroll at phone width.
   - `npx playwright install --with-deps` documented as the one-time browser install; Playwright is not run in CI yet (E09-S01, per D-041).
6. Biome, ESLint, Ruff, ty and mypy configs already exist from E01-S08 and E01-S04; this story does not change rules, it only makes them reachable from one place and documents them.

### One place for commands

7. The commands below are recorded in CLAUDE.md and README.md, verified by running each:

| What | Where | Command |
|---|---|---|
| All backend tests | `backend/` | `uv run pytest` |
| Fast rule tests only | `backend/` | `uv run pytest -m unit` |
| One backend test | `backend/` | `uv run pytest tests/api/test_health.py::test_health_ok` |
| Backend lint and types | `backend/` | `uv run ruff format --check && uv run ruff check && uv run ty check && uv run mypy` |
| Frontend unit tests | `frontend/` | `npm test` |
| One frontend test | `frontend/` | `npx vitest run src/pages/Health.test.tsx -t "database down"` |
| Frontend lint and types | `frontend/` | `npx biome ci && npx eslint . && npm run typecheck` |
| Browser tests | `frontend/` | `npm run e2e` |
| One browser test, one project | `frontend/` | `npx playwright test e2e/smoke.spec.ts --project=firefox-phone` |

## Acceptance criteria

1. Each suite runs with one command and passes on the skeleton. (Verified by running every row of the table; CI runs the backend and frontend unit rows.)
2. A single test can be run on its own. (Rows "One backend test", "One frontend test" and "One browser test" are executed.)
3. `pytest -m unit` runs without a database. (Test run with the database container stopped.)
4. The Playwright smoke test passes in all six projects. (Run locally with the stack up; WebKit stands in for Safari, D-044.)
5. The smoke test fails when the page overflows horizontally at phone width. (Checked once by temporarily breaking the layout.)
6. CLAUDE.md and README.md list the commands, and the CLAUDE.md "Status" and "Commands" sections no longer describe the scaffold. (Review.)

## Tests

- This story is the harness; its tests are the smoke test above and a backend fake-contract example (`tests/unit/test_fakes_example.py`) showing the fake-versus-port pattern that later stories copy.

## Out of scope

Playwright in CI and the real end-to-end flows (E09-S01), coverage thresholds, test data builders (added by the first feature that needs them).

## Open questions

None.
