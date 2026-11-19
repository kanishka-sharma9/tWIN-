# E02-S04 Google sign-in

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03
- **Decisions:** D-010, D-029, D-030, D-058 (Proposed)
- **Flows:** FLOWS.md 2.3

## Goal

A person can sign up and log in with a Google account, when Google sign-in is configured.

## Scope

### Configuration (D-058)

1. Three environment variables, documented in `.env.example`: `TWIN_GOOGLE_CLIENT_ID`, `TWIN_GOOGLE_CLIENT_SECRET`, `TWIN_GOOGLE_REDIRECT_URI` (default `http://localhost:8000/api/auth/google/callback`). Google sign-in is enabled only when all three are set. The owner creates the OAuth client; email and password never depends on it.
2. `GET /api/auth/providers` returns `{"google": true|false}`, so the UI can hide the button when it is off.

### Flow (FLOWS.md 2.3)

3. `GET /api/auth/google/start`: `404 not_found` when disabled; otherwise `302` to Google's authorization URL with `response_type=code`, `scope=openid email`, a random `state` and a PKCE `code_challenge` (S256). The `state` and the code verifier travel in a short-lived (10 minutes), signed, httpOnly cookie scoped to `/api/auth/google`.
4. `GET /api/auth/google/callback?code=&state=`:
   - Missing or mismatching `state`, or a missing cookie, redirects to `/login?error=google_failed` and creates nothing.
   - Exchanges the code with the verifier over HTTPS (`httpx`), and validates the ID token: issuer, audience (the client id), expiry, signature against Google's keys, and `email_verified`.
   - **Known Google subject:** logs that user in.
   - **Email belongs to a password account:** nothing is created or linked; redirect to `/login?error=account_exists` (D-030).
   - **New person:** creates the user (with `google_subject` and no password hash), the vault and the root folder through `CreateUser`.
   - Success sets the refresh cookie exactly as login does and redirects to `/`; the web app then obtains its access token with the silent refresh (S06).
5. `IdentityProvider` port (`authorization_url(state, challenge)`, `exchange(code, verifier) -> VerifiedIdentity(subject, email)`) with a `GoogleIdentityProvider` adapter and an in-memory fake for tests. Use case `SignInWithGoogle` owns the three branches above, so the router stays thin.
6. `users.google_subject` already exists from S01; a migration is added only if a missing index or constraint is found.

### Documentation

7. `docs/google-oauth-setup.md`: create a Google Cloud project, the consent screen, an OAuth client of type "Web application", the redirect URI, and which values go into `.env`. Linked from README.

## Acceptance criteria

1. The first Google sign-in creates a user, vault and root folder; the second lands in the same vault. (Use-case and API tests with the fake provider.)
2. A Google sign-in whose email already has a password account creates nothing, links nothing and redirects to `/login?error=account_exists`. (Test.)
3. A forged or missing `state` and a replayed callback create nothing. (Tests.)
4. An ID token with the wrong audience, an expired token, or `email_verified: false` is refused. (Unit tests on the validator.)
5. With the three variables unset, `/providers` says `false`, `/start` answers 404 and every other route behaves as before. (Tests.)
6. The authorization URL contains the S256 challenge and `state`, and never the client secret. (Test.)

## Tests

- `tests/unit/test_sign_in_with_google.py`, `tests/unit/test_google_id_token.py`, `tests/api/test_google.py`, `tests/api/test_providers.py`.

## Verification (proof type `api`)

- Audit passes on the final commit.
- A Playwright spec drives `/api/auth/providers` and `/api/auth/google/start` through Swagger UI in both states (configured with fake values, and unconfigured), with screenshots and a video in `.verification/e02-s04/`.
- **Real Google is not exercised.** It needs the owner's OAuth client and an interactive sign-in. `proof.md` and the PR body say so; the fake provider carries the branch tests.

## Out of scope

Connecting Google to an existing password account (D-030, D-042), other providers, the Continue with Google button (S06).

## Open questions

None. Resolved: the owner supplies the OAuth client and secret later (D-058).
