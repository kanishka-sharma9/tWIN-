# E02-S01 User and vault model

- **Epic:** E02 Accounts and login
- **Status:** Done
- **Depends on:** E01-S03
- **Decisions:** D-009, D-024, D-026, D-055 (Proposed)
- **Flows:** FLOWS.md 2.1

## Goal

Every account owns exactly one vault, and no request can reach another account's vault.

## Scope

### Database (migration `0002_users_vaults_folders`, written by hand)

1. `users`: `id` uuid primary key, `email` text not null, `password_hash` text null, `google_subject` text null, `created_at` timestamptz default now.
   - Unique index on `lower(email)` (`uq_users_email_lower`), so `Ann@x.com` and `ann@x.com` are the same account. The email is stored as typed after trimming.
   - Unique constraint on `google_subject` (nulls allowed, many).
   - Check constraint: `password_hash is not null or google_subject is not null`, so a user always has a way in and a later account can hold both.
2. `vaults`: `id` uuid primary key, `owner_id` uuid not null references `users`, unique (`uq_vaults_owner_id`, one vault per user for now; dropping it later is how shared vaults arrive), `created_at`.
3. `folders`: `id`, `vault_id` references `vaults`, `parent_id` null references `folders`, `name` text not null, `created_at`.
   - Partial unique index on `vault_id where parent_id is null`: exactly one root per vault.
   - Everything else about folders (sibling name rules, moves, trash) belongs to E04-S01, which extends this table.
4. Downgrade drops the three tables in reverse order. Constraint names follow the naming convention set in E01-S03.

### Domain (`domain/accounts.py`, no framework imports)

5. `Email` value object: trims, requires exactly one `@`, a non-empty local part and a domain containing a dot, at most 254 characters. Equality and hashing use the lower-cased form. Raises `InvalidEmail` (code `invalid_email`).
6. `User`, `Vault`, `Folder` plain dataclasses. `User.__repr__` never prints `password_hash`.
7. `EmailTaken(DomainError)` with code `email_taken`, mapped to HTTP 409 in `STATUS_BY_ERROR`.

### Application

8. Ports in `application/ports/accounts.py`: `UserRepository` (`add`, `by_email`, `by_id`), `VaultRepository` (`add`, `for_user`, `get`), `FolderRepository` (`add_root`, `get`), `UnitOfWork` (context manager that commits or rolls back all repositories together) and `UserAuthenticator` (`authenticate(request) -> UserId | None`).
9. Use case `CreateUser(email, password_hash | None, google_subject | None)`: inside one unit of work it checks the email, inserts the user, its vault and the root folder named `Home` (D-059 later records this name), and returns the user with its vault id. A failure leaves nothing behind.

### Persistence and API adapters

10. SQLAlchemy models and repositories in `adapters/persistence/accounts.py` (2.0 style, no lazy loading, no ORM object leaves the repository, D-026). A unique-violation on `uq_users_email_lower` is translated to `EmailTaken`.
11. `get_current_vault` FastAPI dependency in `adapters/api/dependencies.py`. It asks the `UserAuthenticator` port for the caller, loads that user's vault and returns it. Every later query is scoped by this vault id; no repository method in later stories takes a vault id from the request body or URL.
12. Until E02-S03 the wired authenticator authenticates nobody, so every vault route answers 401 `unauthorized`. A token for a user without a vault is also 401, so ids cannot be probed.

## Acceptance criteria

1. A new user has exactly one vault with exactly one root folder. (Persistence test; unit test with fakes.)
2. Creating a second vault for the same user, or a second root in a vault, is refused by the database. (Persistence tests.)
3. `Ann@X.com` after `ann@x.com` raises `EmailTaken`; the database index agrees even when the use case is bypassed. (Unit and persistence tests.)
4. A failure while inserting the root folder leaves no user and no vault. (Unit test with a failing fake and a persistence rollback test.)
5. A user with neither a password hash nor a Google subject cannot be stored. (Persistence test of the check constraint.)
6. With two users, neither can read the other's folder: the other's folder id answers 404 inside your vault. (API test with two real users and a temporary vault-scoped route registered in test code only.)
7. `alembic upgrade head`, `downgrade base`, `upgrade head` still work. (Existing migration test, extended.)

## Tests

- `tests/unit/test_email.py`, `tests/unit/test_create_user.py` (with `tests/fakes/accounts.py`), `tests/persistence/test_accounts.py`, `tests/api/test_vault_isolation.py`, `tests/persistence/test_migrations.py`.
- Architecture test `tests/architecture/test_layers.py` must still pass: the domain imports nothing from outside.

## Verification (proof type `api`)

- Audit passes on the final commit.
- `proof.md` maps each criterion above to its test.
- No browser proof: this story adds no endpoint, only a dependency.

## Out of scope

Passwords and hashing (S02), tokens (S03), Google (S04), folder naming rules and moves (E04), vault sharing.

## Open questions

None. Resolved: the vault is a separate table from users, one per user, so shared vaults stay possible (D-055, Proposed).
