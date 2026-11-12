# E02-S07 Change password

- **Epic:** E02 Accounts and login
- **Status:** Draft
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

## Open questions

None yet.
