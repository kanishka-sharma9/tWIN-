# E01-S06 API contract and typed client

- **Epic:** E01 Foundation
- **Status:** Done (browser check pending)
- **Depends on:** E01-S02, E01-S04
- **Decisions:** D-024, D-029, D-037, D-053 (Proposed)
- **Flows:** FLOWS.md 1

## Goal

The frontend and backend cannot drift apart silently, and an API error reaches the UI with its code intact.

## Scope

### Backend

1. **One error shape** for every non-2xx response:

```json
{ "error": { "code": "pair_taken", "message": "A file with this name and alter already exists.", "details": {} } }
```

   - `code` is a stable snake_case string the UI switches on; `message` is English text for display; `details` is an object (empty when there is nothing to add, for example `{"field": "alter"}`).
   - `domain/errors.py`: a base `DomainError` carrying a `code`. Each rule failure later subclasses it.
   - `adapters/api/errors.py`: one table mapping error classes to HTTP status and code, and exception handlers registered in `create_app`. Handlers cover `DomainError`, FastAPI's request validation (`code: "validation_error"`, `details.fields` listing each field and reason), 401/403/404/405 from the framework, and a catch-all `internal_error` that never leaks a stack trace.
   - The error response model is declared once and attached to routes, so it appears in the OpenAPI schema and the frontend can type it.
2. **Schema export:** `uv run twin export-openapi` writes the OpenAPI JSON from `create_app()` to `frontend/src/api/openapi.json` without starting a server.

### Frontend

3. **Type generation:** `openapi-typescript` (dev dependency) reads that file and writes `src/api/schema.d.ts`. `npm run api:types` runs export and generation in one step. Both generated files are committed.
4. **Drift check:** CI runs the generation and fails if `git diff --exit-code` shows a change, so a backend schema change cannot merge without regenerated types. Locally, `npm run typecheck` fails when generated types no longer match code that uses them.
5. **Client:** `src/api/client.ts` wraps `openapi-fetch`:
   - Attaches `Authorization: Bearer <access token>` from an in-memory store (never localStorage, D-029).
   - On a `401`, calls an injected `refresh()` once, stores the new token, and retries the original request once. If refresh fails, it clears the token and signals "logged out". Concurrent 401s share one refresh call.
   - `refresh()` is a hook that E02-S03 implements against the refresh cookie; until then it is a stub that fails, which keeps this story testable.
   - Turns every error response into an `ApiError` (`status`, `code`, `message`, `details`). Network failures become `ApiError` with `code: "network_error"`.
6. **TanStack Query:** a `QueryProvider` with one `QueryClient`. Defaults: no retry on 4xx, one retry on network errors, `refetchOnWindowFocus` off for now. A `useHealth()` query replaces E01-S04's placeholder fetch. Mutations surface `ApiError` to the caller.
7. A small `errorMessage(error)` helper returns the English text for a known code and a generic line otherwise, so screens do not each invent wording.

## Acceptance criteria

1. Changing a backend response schema breaks the frontend type check until the types are regenerated. (Verified once by hand; the CI drift check enforces it afterwards.)
2. An API error reaches the UI layer with its code intact. (Vitest with a mocked server: a `pair_taken` response becomes an `ApiError` with `code === "pair_taken"` and the placeholder page shows its message.)
3. Request validation failures, unknown routes and unhandled exceptions all use the same shape. (Backend API tests, one per case; the unhandled case asserts no traceback in the body.)
4. The access token is attached to requests. (Vitest.)
5. A refused request is refreshed and retried exactly once; two simultaneous 401s trigger one refresh; a failed refresh logs out. (Vitest, three tests.)
6. The generated types are current in CI. (CI step.)

## Tests

- Backend: `tests/api/test_errors.py`, `tests/unit/test_openapi_export.py` (the exported file contains `/api/health` and the error schema).
- Frontend: `src/api/client.test.ts`, `src/api/errors.test.ts`.

## Out of scope

Login and the real `refresh()` (E02-S03), the full list of error codes (each feature story adds its own), upload progress handling (E08-S06).

## Open questions

- Confirm D-053's choice of `openapi-typescript` plus `openapi-fetch`. The alternative is hand-wrapping `fetch` around the generated types: fewer dependencies, more code to maintain.

## Notes

- The open question (D-053's `openapi-typescript` + `openapi-fetch`) was not put to the owner (instruction: proceed without questions); it was built as proposed. D-053 stays **Proposed**.
- openapi-typescript 7 needs TypeScript `^5`, while typescript-eslint needs `<6.1`, so TypeScript moves from 6.0 to 5.9 (D-054 updated).
- **Bug found and fixed, present since E01-S04:** `npm run typecheck` ran `tsc --noEmit` against a root `tsconfig.json` that only lists references, so it checked nothing. It now runs `tsc --noEmit -p tsconfig.app.json && tsc --noEmit -p tsconfig.node.json`, and `build` calls it. That exposed real errors in `tokens.test.ts` (Node types missing), fixed by adding `node` to `types`.
- `unwrap()` is typed from the generated schema. A first version inferred `any`, which would have hidden backend schema changes; a probe (`const n: number = useHealth().data`) now errors as it should.
- Criterion 1 was checked by hand: renaming `database` to `db` in the health response, running `npm run api:types` and `npm run typecheck` fails with `Property 'database' does not exist`; the change was then reverted.
- Criteria 3 (backend): `tests/api/test_errors.py` covers a domain error, a validation failure with `details.fields`, an unknown route (404), a wrong method (405) and an unhandled exception (500, no traceback or message leaked).
- Criteria 2, 4 and 5 (frontend): `src/api/client.test.ts` and `src/pages/Health.test.tsx` cover the code reaching the UI (`pair_taken`), the Bearer header, one refresh and one retry, two simultaneous 401s sharing one refresh, and a failed refresh logging out.
- Criterion 6: CI's Python job re-exports the schema and runs `git diff --exit-code` on `openapi.json`; the web job regenerates `schema.d.ts` and diffs it. Both were simulated locally on a clean tree.
- `openapi-fetch` needs an absolute URL outside the browser, so the client's `baseUrl` is `location.origin` (or `http://localhost` when there is no `location`).
- `STATUS_BY_ERROR` is checked in insertion order, so feature stories should list more specific error classes first.
