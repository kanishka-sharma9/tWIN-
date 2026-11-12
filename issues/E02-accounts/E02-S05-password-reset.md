# E02-S05 Password reset

- **Epic:** E02 Accounts and login
- **Status:** Backlog (not in v1, see D-031; returns with real email in E10-S03)
- **Depends on:** E02-S03
- **Decisions:** D-031
- **Flows:** FLOWS.md 2.4

## Goal

A person who forgot their password can set a new one.

## Scope

- Request endpoint that answers the same way whether or not the email exists.
- Single-use, expiring token stored hashed.
- `EmailSender` port with a console adapter that logs the link.
- Set-new-password endpoint that ends all existing sessions.

## Acceptance criteria

- The link from the server log resets the password exactly once.
- An expired or reused link is refused.

## Open questions

- How long is a reset link valid?
