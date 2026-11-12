# E02-S08 Developer password reset command

- **Epic:** E02 Accounts and login
- **Status:** Draft
- **Depends on:** E02-S02
- **Decisions:** D-031
- **Flows:** FLOWS.md 2.5

## Goal

A developer can reset a forgotten password while v1 has no email.

## Scope

- A command-line command that sets a new password for a given email.
- Revoke that account's refresh tokens.
- Document the command in README.md.

## Acceptance criteria

- After the command, the new password logs in and the old one does not.
- An unknown email is refused with a clear message.

## Open questions

None yet.
