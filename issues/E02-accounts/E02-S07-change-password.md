# E02-S07 Change password

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03
- **Decisions:** D-029, D-042
- **Flows:** FLOWS.md 2.4

## Goal

A logged-in person can change their password.

## Scope

- Endpoint taking the current password and the new one.
- Apply the password rules and save the new hash.
- Revoke the refresh tokens on the person's other devices.
- Not offered to accounts created through Google, which have no password.

## Acceptance criteria

- A wrong current password is refused.
- The new password works at the next login and the old one does not.
- Other devices are logged out.

## Detail

`POST /api/auth/change-password` (bearer) body `{current_password, new_password}` -> 204. Errors: 401 `wrong_password`, 422 `weak_password`, 409 `no_password` for Google-only accounts (`has_password` false in `/me`). Saves a new Argon2id hash and revokes every refresh token of the user except the one on the current request cookie (the current device stays logged in).

**Tests:** wrong current; weak new; success then login with the new password works and the old fails; a second device's refresh fails afterwards while the current one still refreshes; Google account refused.

## Verification

- `api` proof: `proof.md` plus audit. Proof dir `e02-s07`.
