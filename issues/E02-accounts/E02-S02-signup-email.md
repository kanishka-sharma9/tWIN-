# E02-S02 Sign up with email and password

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S01
- **Decisions:** D-010, D-030, D-056 (Proposed)
- **Flows:** FLOWS.md 2.1

## Goal

A person can create an account with an email address and a password.

## Scope

### Backend

1. `POST /api/auth/signup`, body `{"email": "...", "password": "..."}`.
   - `201` with `{"user": {"id": "...", "email": "..."}}`. (E02-S03 extends this response with the access token and the refresh cookie, so signup logs the person in.)
   - `422 validation_error` for a malformed body or email, with `details.fields`.
   - `422 weak_password` with `details.min_length` (10) and `details.max_length` (128).
   - `409 email_taken` when the address already has an account, by password or by Google. The message says the account already exists; the UI turns it into an offer to log in (D-030).
2. **Email rules** are the `Email` value object from S01: trimmed, one `@`, a dot in the domain, at most 254 characters. Duplicates are detected case-insensitively; the email is stored as typed.
3. **Password rules (D-056):** 10 to 128 characters counted as Unicode characters, no composition rules (no required digit, symbol or case), no trimming, so spaces are allowed. `Password` is a domain value object that owns this rule and refuses to print itself.
4. **Hashing:** `PasswordHasher` port (`hash`, `verify`, `needs_rehash`) in `application/ports`, with an Argon2id adapter in `adapters/auth/` using the `argon2-cffi` defaults (D-030). `argon2-cffi` goes through the dependency vetting; the owner has approved it.
5. Use case `SignUp(email, password)` validates, hashes and calls `CreateUser` from S01. The router only translates HTTP.
6. **The password never leaks.** The request model holds it as a `SecretStr`; the validation error handler never echoes submitted input; the OpenAPI schema carries no example password; no log line contains it.
7. New error rows in `STATUS_BY_ERROR`: `EmailTaken` 409, `WeakPassword` 422, `InvalidEmail` 422. The frontend types are regenerated (`npm run api:types`).

## Acceptance criteria

1. A valid sign-up creates the user, a vault and a root folder and answers `201`. (API test, then a database assertion.)
2. The same email with different capitals answers `409 email_taken`; so does an email registered through Google. (API tests; the Google case is built by creating a user with only a Google subject.)
3. Passwords of 9 and 129 characters are refused and 10 and 128 are accepted. (Unit tests on the boundaries.)
4. The stored value is an Argon2id hash, never the password, and `verify` accepts the right password and rejects a wrong one. (Hasher test; database assertion.)
5. The password does not appear in captured logs, in an error response for a bad request, or in the OpenAPI document. (API tests that search all three.)
6. A malformed email answers `422 validation_error` with `details.fields` naming `email`. (API test.)

## Tests

- `tests/unit/test_password.py`, `tests/unit/test_signup.py`, `tests/unit/test_hasher.py`, `tests/api/test_signup.py`.

## Verification (proof type `api`)

- Audit passes on the final commit.
- A Playwright spec in `frontend/e2e/proof/s02-signup.spec.ts` drives `POST /api/auth/signup` through Swagger UI (`/docs`): a successful sign-up, the duplicate email refusal and the weak password refusal, each with a screenshot of the response, plus a video. Evidence lands in `.verification/e02-s02/`.
- `proof.md` maps each criterion to its test or screenshot.

## Out of scope

Tokens and login (S03), Google (S04), email verification (D-031: no email in v1), rate limiting and request size limits on this route (follow-up), the sign-up screen (S06).

## Open questions

None. Resolved: password rules per D-056; revealing that an email is registered is the choice D-030 already made.
