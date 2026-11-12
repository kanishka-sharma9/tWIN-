# E02-S01 User and vault model

- **Epic:** E02 Accounts and login
- **Status:** Draft
- **Depends on:** E01-S03
- **Decisions:** D-009, D-024
- **Flows:** FLOWS.md 2.1

## Goal

Every account owns exactly one vault, and no request can reach another account's vault.

## Scope

- `users` and `vaults` tables, with their repositories and ports.
- Creating a user also creates the vault and its root folder.
- A current-vault dependency that every later query is scoped by.

## Acceptance criteria

- A new user has exactly one vault with a root folder.
- A test with two users shows neither can read the other's data.

## Open questions

- Keep `vaults` separate from `users` so shared vaults stay possible later? (proposed: yes)
