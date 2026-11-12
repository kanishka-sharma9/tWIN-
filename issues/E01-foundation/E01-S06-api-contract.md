# E01-S06 API contract and typed client

- **Epic:** E01 Foundation
- **Status:** Draft (spec complete; waits for D-053's library choice to be confirmed)
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
