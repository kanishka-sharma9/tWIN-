# E02 Accounts and login

- **Status:** In progress
- **Depends on:** E01

## Outcome

A person can create an account with email + password or Google, gets a private vault, and stays logged in.

## Stories

| ID | Story | Depends on | Proof | Status |
|---|---|---|---|---|
| [E02-S01](E02-S01-user-vault-model.md) | User and vault model | E01-S03 | api | Done |
| [E02-S02](E02-S02-signup-email.md) | Sign up with email and password | E02-S01 | api | Done |
| [E02-S03](E02-S03-sessions.md) | Log in, log out and tokens | E02-S02 | api | Done |
| [E02-S04](E02-S04-google-signin.md) | Google sign-in | E02-S03 | api | Done |
| [E02-S05](E02-S05-password-reset.md) | Password reset (not in v1, D-031) | E02-S03 | none | Backlog |
| [E02-S06](E02-S06-auth-screens.md) | Sign-up, login and account screens | E02-S03, E02-S04, E02-S07, E01-S05, E01-S06 | ui | Ready |
| [E02-S07](E02-S07-change-password.md) | Change password | E02-S03 | api | Done |
| [E02-S08](E02-S08-developer-password-reset.md) | Developer password reset command | E02-S03, E02-S07 | cli | Ready |

Build order: S01, S02, S03, S04, S07, S08, S06. S06 comes last because it uses everything.

## Proof types

- **api:** a Playwright spec drives the story's endpoints through Swagger UI in Chromium; screenshots and video go to `.verification/e02-sNN/`, together with the audit report.
- **ui:** Playwright at 1280 and 390 width with screenshots and video in the same folder.
- **cli:** a terminal transcript in `proof.md`.

## The API this epic builds (one place to read it)

All routes are under `/api/auth`. Every non-2xx response uses the E01-S06 error shape.

| Route | Auth | Story | Success | Errors |
|---|---|---|---|---|
| `POST /signup` | none | S02 (+S03) | `201` user and, from S03, tokens | `422 validation_error`, `422 weak_password`, `409 email_taken` |
| `POST /login` | none | S03 | `200` access token, user; refresh cookie | `401 invalid_credentials`, `429 rate_limited` |
| `POST /refresh` | cookie + CSRF header | S03 | `200` new access token; new cookie | `401 invalid_refresh_token`, `403 csrf_failed` |
| `POST /logout` | cookie + CSRF header | S03 | `204` | `403 csrf_failed` |
| `GET /me` | bearer | S03 | `200` id, email, `has_password` | `401 unauthorized` |
| `GET /providers` | none | S04 | `200 {google: bool}` | none |
| `GET /google/start` | none | S04 | `302` to Google | `404 not_found` when off |
| `GET /google/callback` | state cookie | S04 | `302` to `/` | redirects to `/login?error=...` |
| `POST /change-password` | bearer | S07 | `204` | `401 wrong_password`, `422 weak_password`, `409 no_password`, `429 rate_limited` |

CLI: `uv run twin set-password <email>` (S08).

## Rules that hold across the stories

- Passwords: 10 to 128 characters, no composition rules, Argon2id (D-030, D-056).
- Access token 15 minutes, refresh token 30 days rotated on every use, no remember-me (D-029, D-057). The access token is kept only in memory in the browser.
- One email, one login method: no automatic linking between password and Google accounts (D-030).
- No email is sent in v1 (D-031).
- Every vault query is scoped by `get_current_vault`; no route takes a vault id from the caller (D-009).

## Settings added by the epic

| Variable | Story | Meaning |
|---|---|---|
| `TWIN_JWT_SECRET` | S03 | Signing key, at least 32 characters, no default; the API refuses to start without it |
| `TWIN_COOKIE_SECURE` | S03 | Sets `Secure` on the refresh cookie; on when served over HTTPS |
| `TWIN_GOOGLE_CLIENT_ID`, `TWIN_GOOGLE_CLIENT_SECRET`, `TWIN_GOOGLE_REDIRECT_URI` | S04 | Google sign-in is on only when all three are set |

## Migrations in order

`0002_users_vaults_folders` (S01), `0003_refresh_tokens` (S03). S04 adds none unless a missing index is found.

## Out of scope for the epic

Password reset by email and email verification (D-031, E10-S03), connecting Google to a password account, deleting the account, changing the email (E10-S08), shared vaults.
