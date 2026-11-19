# E02-S02 Sign up with email and password

- **Epic:** E02 Accounts and login
- **Status:** Ready
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

## Open questions (answered)

- Password rules: minimum 10, maximum 128 characters, no composition rules (D-056, Proposed from the owner's choice).
- Revealing a registered email: yes, as D-030 already decides.

## Detail

`POST /api/auth/signup` body `{email, password}`. 201 returns `{user: {id, email}}` (S03 adds the access token and refresh cookie to this response). Errors: 422 `validation_error` with `details.fields`; 409 `email_taken` (message says the account already exists; the UI offers login); 422 `weak_password` with `details.min_length`.

Email check: trimmed, one `@`, domain contains a dot, max 254 chars; compared case-insensitively, stored as typed. Password: `PasswordHasher` port (`hash`, `verify`, `needs_rehash`) with an Argon2id adapter (`argon2-cffi` defaults); the plain password never appears in logs, errors or OpenAPI examples. Use case `SignUp` calls `CreateUser`.

**Tests:** value-object unit tests (boundaries 9/10/128/129 characters); hasher test; API tests (201; duplicate with different case 409; weak password 422; the stored hash is not the password; captured logs searched for the password).

## Verification

- `api` proof: `proof.md` plus audit. Proof dir `e02-s02`.
