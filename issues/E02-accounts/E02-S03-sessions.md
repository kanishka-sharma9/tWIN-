# E02-S03 Log in, log out and tokens

- **Epic:** E02 Accounts and login
- **Status:** Draft
- **Depends on:** E02-S02
- **Decisions:** D-029, D-030
- **Flows:** FLOWS.md 2.2

## Goal

A logged-in person stays logged in across requests and reloads, and can log out.

## Scope

- Login endpoint that returns a short-lived access token (JWT) and sets a refresh token in an httpOnly cookie.
- Refresh endpoint that swaps the refresh token for a new pair. Refresh tokens are recorded in the database and replaced on each use.
- Logout that revokes the refresh token, and a who-am-I endpoint.
- Protection against cross-site request forgery on the refresh endpoint.
- A rate limit on login attempts.

## Acceptance criteria

- A wrong password gives the same generic error as an unknown email.
- After logout the refresh token no longer works.
- A request with a missing or expired access token gets 401.
- A refresh token that was already used or revoked is refused.

## Open questions

- How long do the access token and the refresh token last?
- Is a 'remember me' option wanted?
