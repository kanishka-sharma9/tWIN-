# E02-S03 Log in, log out and tokens

- **Epic:** E02 Accounts and login
- **Status:** Done
- **Depends on:** E02-S02
- **Decisions:** D-029, D-030, D-057 (Proposed)
- **Flows:** FLOWS.md 2.2

## Goal

A logged-in person stays logged in across requests and reloads, and can log out.

## Scope

### Tokens (D-029, D-057)

1. **Access token:** a JWT (HS256) valid for 15 minutes, claims `sub` (user id), `vid` (vault id), `iat`, `exp`. Signed with `TWIN_JWT_SECRET`, which must be at least 32 characters; the API refuses to start without it, and `.env.example` leaves it empty on purpose. Only `HS256` is accepted on verification and `sub`, `exp` and `iat` are required. The vault is still looked up on every request, so `vid` is informational.
2. **Refresh token:** a random 256-bit string valid for 30 days, no remember-me. Only its SHA-256 hash is stored.
3. Table `refresh_tokens` (migration `0003`, by hand): `id`, `user_id` references `users`, `token_hash` unique, `family_id` uuid (one family per login), `expires_at`, `revoked_at` null, `replaced_by` null references `refresh_tokens`, `created_at`.
4. `TokenIssuer` port (issue and verify access tokens) with a PyJWT adapter; `pyjwt` goes through the dependency vetting and is approved. The clock is the existing `Clock` port, so expiry is testable.

### Endpoints (all under `/api/auth`)

5. `POST /login` `{email, password}` returns `200 {access_token, token_type: "bearer", expires_in: 900, user: {id, email, has_password}}` and sets the cookie `refresh_token`: httpOnly, `SameSite=Lax`, `Path=/api/auth`, `Secure` when `TWIN_COOKIE_SECURE` is set.
   - Unknown email, wrong password, malformed email and an account with no password all answer the same `401 invalid_credentials`. An unknown email still runs one hash verification so timing does not reveal it.
6. `POST /refresh` (cookie) returns a new pair and replaces the token. Each use inserts a new token in the same family and marks the old one replaced, under a row lock so two simultaneous refreshes cannot both succeed.
   - A replaced or revoked token revokes the whole family and answers `401 invalid_refresh_token`; an expired or unknown one answers the same 401 without revoking.
7. `POST /logout` returns `204`, revokes the whole family of the presented token, clears the cookie, and answers 204 even when the cookie is missing or unknown.
8. `GET /me` (bearer) returns `{id, email, has_password}`. A missing, malformed, wrongly signed or expired token answers `401 unauthorized`.
9. Signup (S02) now also issues the pair, with the same response as login.
10. The `UserAuthenticator` port from S01 now resolves the bearer token, so `get_current_vault` works for real.

### Protection

11. **CSRF** on `/refresh` and `/logout`: the request must carry `X-Requested-With: twin`, and an `Origin` header, when present, must have the same host name as `Host`; otherwise `403 csrf_failed`. Together with `SameSite=Lax` this keeps another site from refreshing or logging a person out.
12. **Login rate limit:** 5 failed attempts per email and client address in 15 minutes (sliding window) answer `429 rate_limited` with `Retry-After`, even for the right password; a successful login resets the count. `LoginLimiter` is a port with an in-memory adapter (single process in v1). Deployment behind a proxy must pass the real client address through before this limit means anything.
13. New error rows: `InvalidCredentials` 401, `InvalidRefreshToken` 401, `CsrfFailed` 403, `RateLimited` 429.

## Acceptance criteria

1. A wrong password and an unknown email give identical responses (status, code, message). (API test.)
2. After logout the refresh token no longer works. (API test.)
3. A request with no token, a garbage token, a token signed with another key and an expired token (fake clock) all get 401. (API tests.)
4. A refresh token that was already used is refused, and the whole family is revoked, including the newest token. (API test.)
5. A refresh returns a working new access token and a new cookie; the old cookie stops working. (API test.)
6. Refresh and logout without the CSRF header, or with a foreign `Origin`, answer 403. (API tests.)
7. The sixth failed login inside the window answers 429 with `Retry-After`; a success resets the counter. (API test with the fake clock.)
8. The cookie is httpOnly, `SameSite=Lax`, `Path=/api/auth`, and `Secure` when configured; the stored token is a hash. (API test on headers; persistence assertion.)
9. The API will not start with a missing or short `TWIN_JWT_SECRET`. (Settings test.)

## Tests

- `tests/unit/test_token_issuer.py`, `tests/unit/test_login_limiter.py`, `tests/api/test_login.py`, `tests/api/test_refresh.py`, `tests/api/test_logout.py`, `tests/api/test_me.py`, `tests/persistence/test_refresh_tokens.py`, `tests/unit/test_settings.py`.

## Verification (proof type `api`)

- Audit passes on the final commit.
- A Playwright spec drives the endpoints through Swagger UI: sign up, log in (200), `/me` with the bearer token (200), a wrong password (401), refresh, logout. A screenshot of each response and a video go to `.verification/e02-s03/`.
- `proof.md` includes a curl transcript against a live server and maps each criterion to its test.
- Not verifiable here: the `Secure` flag over real HTTPS, behaviour behind a reverse proxy.

## Out of scope

Google (S04), change password (S07, which also revokes token families), the screens and the silent refresh on page load (S06), cleaning up expired token rows, a database-backed limiter.

## Open questions

None. Resolved: access 15 minutes, refresh 30 days, no remember-me (D-057, Proposed from the owner's choice).
