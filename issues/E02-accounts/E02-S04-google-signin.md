# E02-S04 Google sign-in

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03
- **Decisions:** D-010, D-029, D-030
- **Flows:** FLOWS.md 2.3

## Goal

A person can sign up and log in with a Google account.

## Scope

- Authorization-code flow with PKCE handled by the backend.
- First sign-in creates the account and vault; later sign-ins find it by its Google subject.
- If the email already belongs to a password account, nothing is linked: the sign-in is refused and the person lands on login with a message that the account already exists.
- Configuration through environment variables, with the button hidden when unset.
- A setup guide for creating the Google OAuth client.

## Acceptance criteria

- First Google sign-in creates a vault; the second lands in the same vault.
- Google sign-in with an email that has a password account creates nothing and lands on login with the message.
- The app works normally when Google is not configured.

## Open questions (answered)

- The owner supplies the OAuth client id and secret; until then the feature is off and email+password works on its own (D-058, Proposed). Tests use a fake `IdentityProvider`; real Google cannot be exercised unattended, and the PR must say so.

## Detail

Env: `TWIN_GOOGLE_CLIENT_ID`, `TWIN_GOOGLE_CLIENT_SECRET`, `TWIN_GOOGLE_REDIRECT_URI` (default `http://localhost:8000/api/auth/google/callback`). Enabled only when all three are set.

- `GET /api/auth/providers` -> `{google: bool}` (the UI hides the button when false).
- `GET /api/auth/google/start` -> 302 to Google with `state` and PKCE `code_challenge` (S256); `state` and the verifier are kept in a short-lived signed httpOnly cookie.
- `GET /api/auth/google/callback?code&state` -> verifies state, exchanges the code (httpx), validates the ID token (issuer, audience, expiry, `email_verified`), then: known `google_subject` -> log in; email belongs to a password account -> 302 `/login?error=account_exists` and nothing created; otherwise create user and vault with `google_subject` and no password hash. Success sets the refresh cookie and redirects to `/`.
- Port `IdentityProvider(authorization_url, exchange)`; adapters: `GoogleIdentityProvider` and a test fake.
- Docs: `docs/google-oauth-setup.md` (create the Cloud project, consent screen, OAuth client, redirect URI, env vars), linked from README.

**Tests:** fake-provider tests for all three branches, state mismatch, disabled provider 404, app unaffected when unconfigured.

## Verification

- `api` proof: `proof.md` plus audit. State plainly that real Google was not exercised. Proof dir `e02-s04`.
