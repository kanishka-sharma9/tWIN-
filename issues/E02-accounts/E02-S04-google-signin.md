# E02-S04 Google sign-in

- **Epic:** E02 Accounts and login
- **Status:** Draft
- **Depends on:** E02-S03
- **Decisions:** D-010, D-029, D-030
- **Flows:** FLOWS.md 2.3

## Goal

A person can sign up and log in with a Google account.

## Scope

- Authorization-code flow with PKCE handled by the backend.
- First sign-in creates the account and vault; later sign-ins find it by its Google subject.
- If the email already belongs to a password account, nothing is linked: the sign-in is refused and the person lands on login with a message that the account already exists.
- Configuration through environment variables, with the button hidden when unset.
- A setup guide for creating the Google OAuth client.

## Acceptance criteria

- First Google sign-in creates a vault; the second lands in the same vault.
- Google sign-in with an email that has a password account creates nothing and lands on login with the message.
- The app works normally when Google is not configured.

## Open questions

- Who owns the Google Cloud project that holds the OAuth client?
