# E02 Accounts and login

- **Status:** Draft
- **Depends on:** E01

## Outcome

A person can create an account with email + password or Google, gets a private vault, and stays logged in.

## Stories

| ID | Story | Depends on | Status |
|---|---|---|---|
| [E02-S01](E02-S01-user-vault-model.md) | User and vault model | E01-S03 | Draft |
| [E02-S02](E02-S02-signup-email.md) | Sign up with email and password | E02-S01 | Draft |
| [E02-S03](E02-S03-sessions.md) | Log in, log out and tokens | E02-S02 | Draft |
| [E02-S04](E02-S04-google-signin.md) | Google sign-in | E02-S03 | Draft |
| [E02-S05](E02-S05-password-reset.md) | Password reset (not in v1, D-031) | E02-S03 | Backlog |
| [E02-S06](E02-S06-auth-screens.md) | Sign-up, login and account screens | E02-S03, E02-S04, E02-S07, E01-S05, E01-S06 | Draft |
| [E02-S07](E02-S07-change-password.md) | Change password | E02-S03 | Draft |
| [E02-S08](E02-S08-developer-password-reset.md) | Developer password reset command | E02-S02 | Draft |
