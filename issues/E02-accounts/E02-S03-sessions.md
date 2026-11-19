# E02-S03 Log in, log out and tokens

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S02
- **Decisions:** D-029, D-030
- **Flows:** FLOWS.md 2.2

## Goal

A logged-in person stays logged in across requests and reloads, and can log out.

## Scope

- Login endpoint that returns a short-lived access token (JWT) and sets a refresh token in an httpOnly cookie.
- Refresh endpoint that swaps the refresh token for a new pair. Refresh tokens are recorded in the database and replaced on each use.
- Logout that revokes the refresh token, and a who-am-I endpoint.
- Protection against cross-site request forgery on the refresh endpoint.
- A rate limit on login attempts.

## Acceptance criteria

- A wrong password gives the same generic error as an unknown email.
- After logout the refresh token no longer works.
- A request with a missing or expired access token gets 401.
- A refresh token that was already used or revoked is refused.

## Open questions (answered)

- Access token 15 minutes; refresh token 30 days; no remember-me (D-057, Proposed from the owner's choice).

## Detail

Table `refresh_tokens(id uuid pk, user_id fk, token_hash text unique, family_id uuid, expires_at, revoked_at null, replaced_by null, created_at)`; only the SHA-256 hash of the random 256-bit token is stored. Access token: JWT HS256 signed with `TWIN_JWT_SECRET` (required outside tests), claims `sub`, `vid` (vault id), `exp`, `iat`.

Endpoints (all under `/api/auth`):
- `POST /login` `{email, password}` -> 200 `{access_token, token_type: "bearer", expires_in: 900, user}` and `Set-Cookie: refresh_token` (httpOnly, SameSite=Lax, Path=/api/auth, Secure when `TWIN_COOKIE_SECURE`). Wrong password and unknown email both give 401 `invalid_credentials`, with a dummy hash verify so timing matches.
- `POST /refresh` (cookie) -> new pair, old token marked replaced. Reuse of a replaced or revoked token revokes the whole family and answers 401 `invalid_refresh_token`. CSRF: requires header `X-Requested-With: twin` and a same-site `Origin` (when present); otherwise 403 `csrf_failed`.
- `POST /logout` -> 204, revokes the token, clears the cookie.
- `GET /me` (bearer) -> `{id, email, has_password}`; missing, malformed or expired token -> 401 `unauthorized`.
- Signup now also issues the pair (same response as login).
- Login rate limit: 5 failed attempts per email+IP per 15 minutes -> 429 `rate_limited` with `Retry-After` (in-memory adapter behind a port, fine for single-process v1).

The S01 `UserAuthenticator` port now resolves from the bearer token, so `get_current_vault` works.

**Tests:** each acceptance criterion; expiry with the fake clock; rotation and reuse detection; CSRF; rate limit; cookie flags asserted.

## Verification

- `api` proof: `proof.md` plus audit; include a curl transcript in `proof.md` for login, refresh, logout. Proof dir `e02-s03`.
