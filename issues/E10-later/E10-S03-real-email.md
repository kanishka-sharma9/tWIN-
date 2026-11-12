# E10-S03 Email: sending, password reset and verification

- **Epic:** E10 Later: hosting and apps
- **Status:** Backlog
- **Depends on:** None
- **Decisions:** D-030, D-031
- **Flows:** FLOWS.md 2.5

## Goal

The app can send email, so forgotten passwords can be reset and addresses verified.

## Scope

- An `EmailSender` port with a provider adapter.
- Password reset by emailed link (spec in E02-S05).
- Email verification at sign-up.

## Acceptance criteria

- A reset email reaches a real inbox and its link works once.
- An unverified address is handled as decided.

## Open questions

- Which email provider?
- What can an unverified account do?
