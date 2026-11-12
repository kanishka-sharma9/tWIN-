# E02-S02 Sign up with email and password

- **Epic:** E02 Accounts and login
- **Status:** Draft
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

## Open questions

- What are the password rules (minimum length)?
- Should sign-up reveal that an email is already registered?
