# E02-S07 Change password

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03
- **Decisions:** D-029, D-042, D-056
- **Flows:** FLOWS.md 2.4

## Goal

A logged-in person can change their password, and their other devices are logged out.

## Scope

1. `POST /api/auth/change-password` (bearer), body `{"current_password": "...", "new_password": "..."}`, answers `204`.
   - `401 wrong_password` when the current password does not match. (Distinct from `invalid_credentials` because the caller is already authenticated.)
   - `422 weak_password` when the new password breaks the S02 rules (10 to 128 characters, no composition rules).
   - `409 no_password` for an account created through Google, which has no password to change (D-042). `GET /api/auth/me` already reports `has_password` so the UI can hide the form.
   - `422 validation_error` for a malformed body.
2. Use case `ChangePassword(user_id, current, new, keep_family)`: verifies the current password with `PasswordHasher.verify`, builds the new `Password` value object, hashes it, saves the hash, then revokes every refresh-token family of that user except the one on the current request's cookie, so the current device stays logged in. It does all of this in one unit of work.
3. A new `RefreshTokenRepository.revoke_user_families(user_id, except_family)` method; the existing S03 table is reused, no migration.
4. The new password is never logged or echoed, as in S02. New error rows: `WrongPassword` 401, `NoPassword` 409.
5. Rate limiting: wrong current passwords count against the S03 `LoginLimiter` keyed on the user id, so the endpoint cannot be used to guess the current password.

## Acceptance criteria

1. A wrong current password is refused and nothing changes. (API test.)
2. The new password works at the next login and the old one does not. (API test.)
3. A refresh token held by another device stops working after the change, while the current device's refresh still works. (API test with two logins.)
4. A new password shorter than 10 or longer than 128 characters is refused. (API test.)
5. A Google-created account answers `409 no_password`. (API test.)
6. Repeated wrong current passwords end in `429 rate_limited`. (API test with the fake clock.)
7. A request without a bearer token answers 401. (API test.)

## Tests

- `tests/unit/test_change_password.py`, `tests/api/test_change_password.py`, `tests/persistence/test_refresh_tokens.py` (extended for `revoke_user_families`).

## Verification (proof type `api`)

- Audit passes on the final commit.
- A Playwright spec drives the flow through Swagger UI: log in, authorize with the bearer token, change password (204), a wrong current password (401), then log in with the new password. Screenshots and a video go to `.verification/e02-s07/`.
- `proof.md` maps each criterion to its test or screenshot.

## Out of scope

The account settings screen (S06), changing the email, deleting the account, connecting Google (E10-S08), password reset by email (E10-S03).

## Open questions

None.
