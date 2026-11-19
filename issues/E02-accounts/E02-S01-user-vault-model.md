# E02-S01 User and vault model

- **Epic:** E02 Accounts and login
- **Status:** Ready
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

## Open questions (answered)

- Vault separate from users: yes, 1:1 for now (unique `vaults.owner_id`), so shared vaults stay possible (D-055, Proposed).

## Detail

**Tables** (migration `0002`, by hand): `users(id uuid pk, email text not null, password_hash text null, google_subject text null unique, created_at)` with a unique index on `lower(email)`; `vaults(id uuid pk, owner_id fk users unique, created_at)`; `folders(id uuid pk, vault_id fk, parent_id fk null, name text, created_at)` with a partial unique index so a vault has exactly one root (`parent_id is null`). E04-S01 extends `folders`.

**Code:** domain `User`, `Vault`, `Folder` and an `Email` value object; ports `UserRepository`, `VaultRepository`; use case `CreateUser(email, password_hash | google_subject)` that inserts user, vault and root folder in one transaction and raises `EmailTaken` (409, code `email_taken`); `get_current_vault` FastAPI dependency resolved from a `UserAuthenticator` port (an adapter that authenticates nobody until S03, so vault routes answer 401).

**Tests:** unit tests with in-memory fakes (create user makes one vault with one root); persistence tests (case-insensitive uniqueness, one root per vault); an API-level isolation test with two users and a temporary vault-scoped route in test code only.

## Verification

- `api` proof: `proof.md` maps each criterion to its test; the audit passes. No browser proof (no UI). Proof dir `e02-s01`.
