# E02-S06 Sign-up, login and account screens

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03, E02-S04, E02-S07, E01-S05, E01-S06
- **Decisions:** D-010, D-013, D-017, D-030, D-042, D-043
- **Flows:** FLOWS.md 2

## Goal

Everything in this epic can be done from the web app, on a desktop or a phone.

## Scope

- Sign-up and login screens.
- A Continue with Google button.
- The 'account already exists' message when a sign-up or Google sign-in was refused.
- An account settings screen with change password.
- Redirect to login when not signed in; log out from the app shell.
- Form validation and error messages from API error codes.

## Acceptance criteria

- A new person can go from the first screen to an empty vault using only the UI.
- Reloading the page keeps the person logged in.
- A logged-in person can change their password from account settings.
- Every screen is usable at phone width.

## Detail

Routes: `/signup`, `/login`, `/` (empty vault shell showing the signed-in email and Log out), `/account` (change password). Unauthenticated access to `/` or `/account` redirects to `/login`.

- Auth state: access token only in memory; on load the app calls `POST /api/auth/refresh` (with the CSRF header) before deciding between the app and `/login`; a 401 anywhere returns to `/login`.
- Screens use the oxblood/rose/cyan tokens and shared components; single column at phone width 390, centred card at 1280; every control has a visible label and focus ring, touch targets at least 44px.
- States per form: idle, submitting (button disabled), field errors from `details.fields`, and top-level errors from `errorMessage()`. `email_taken` shows "An account with this email already exists." with a Log in link; `/login?error=account_exists` shows the same message.
- Continue with Google appears only when `GET /api/auth/providers` says `google: true`.
- Account page: change-password form (replaced by an explanation when `has_password` is false).

**Tests:** Vitest per screen state; Playwright spec `frontend/e2e/auth.spec.ts`: sign up, empty vault, reload stays signed in, change password, log out, log in with the new password, at desktop and phone.

## Verification

- `ui` proof: `factory-proof.sh ui` on the final commit; evidence in `.verification/e02-s06/` includes desktop and phone screenshots of signup, login, error states, empty vault and account page, plus a video of the full flow. Proof dir `e02-s06`.
