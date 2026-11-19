# E02-S02 Sign up with email and password

- **Epic:** E02 Accounts and login
- **Status:** Done
- **Depends on:** E02-S01
- **Decisions:** D-010, D-030
- **Flows:** FLOWS.md 2.1

## Goal

A person can create an account with an email address and a password.

## Scope

- Sign-up endpoint.
- Email format check and case-insensitive duplicate detection.
- Password rules and Argon2id hashing.

## Acceptance criteria

- A valid sign-up creates the user and vault and logs the person in.
- An email that already has an account, by password or by Google, is refused with a message that the account exists, and the person is offered the login screen (D-030).
- The password is never stored or logged in readable form.

## Answers to the open questions

- Password rules: 10 to 128 characters, no composition rules (owner decision, D-030; recorded in D-056).
- Sign-up does reveal that an email is registered: it answers 409 `email_taken` so the UI can offer login (D-030).

## Built

- `POST /api/auth/signup` takes `{email, password}` and answers 201 `{user: {id, email}}`. It creates the user, vault and root folder in one transaction. The password hash is never returned.
- Tokens are not issued yet: E02-S03 adds them to this response ("logs the person in" is completed there).
- Errors: `invalid_email` (422), `weak_password` (422, `details` has `min_length` or `max_length`), `email_taken` (409).
- Argon2id sits behind the `PasswordHasher` port (`adapters/auth/argon2_hasher.py`); `users.password_hash` is nullable (migration 0003) so Google accounts (E02-S04) can have none.
