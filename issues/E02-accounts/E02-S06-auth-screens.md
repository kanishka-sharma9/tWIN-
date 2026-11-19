# E02-S06 Sign-up, login and account screens

- **Epic:** E02 Accounts and login
- **Status:** Ready
- **Depends on:** E02-S03, E02-S04, E02-S07, E01-S05, E01-S06
- **Decisions:** D-010, D-013, D-017, D-029, D-030, D-042, D-043, D-045, D-046
- **Flows:** FLOWS.md 2, 3.3

## Goal

Everything in this epic can be done from the web app, on a desktop or a phone.

## Scope

### Routing and session

1. Routes with React Router: `/signup`, `/login`, `/` (the signed-in shell, an empty vault for now) and `/account`. Signed-out access to `/` or `/account` redirects to `/login`; signed-in access to `/signup` or `/login` redirects to `/`.
2. **Auth state** in `src/auth/`: the access token lives only in memory (D-029), reusing the E01-S06 client store. On load the app calls `POST /api/auth/refresh` with the header `X-Requested-With: twin` before deciding between the app and `/login`, so a reload keeps the person signed in. A `401` that survives the client's one refresh retry sends the person to `/login`. Logout calls `POST /api/auth/logout` (same header) and clears state. The E01-S06 `refresh()` stub is replaced with the real call.
3. The Google start link is a plain navigation to `/api/auth/google/start`; the app never sees Google's tokens.

### Screens (each designed from the shared tokens and components, D-046; English text written directly, D-045)

4. **Sign up:** email, password with a show/hide toggle, a hint "At least 10 characters", submit. States: idle, submitting (button disabled), field errors from `details.fields`, `weak_password` shown under the password field, `email_taken` shown as "An account with this email already exists." with a Log in link (D-030). On success the app opens `/`.
5. **Log in:** email, password, submit, a link to Sign up. A `401 invalid_credentials` shows one generic line; `429 rate_limited` shows how long to wait from `Retry-After`. `/login?error=account_exists` shows the same "An account with this email already exists." message and `?error=google_failed` shows "Google sign-in did not work. Please try again."
6. **Continue with Google** appears on both screens only when `GET /api/auth/providers` says `google: true`, below an "or" divider. When Google is off, the screens show email and password only.
7. **Signed-in shell** (`/`): a top bar with the app name, the person's email and a Log out button; an empty-vault message ("This vault is empty. Files will appear here.") inside the content area. E08-S01 replaces this shell.
8. **Account** (`/account`): shows the email and a change-password form (current password, new password, confirm). On success it says "Password changed. Your other devices were signed out." Accounts where `has_password` is false see an explanation instead: "This account signs in with Google, so there is no password to change." (D-042).
9. Messages come from API error codes through `errorMessage()`; unknown codes show the generic line.

### Responsive and accessible (D-043, FLOWS.md 3.3, issues/README.md rules)

10. At 390 px width: one column, full-width fields and buttons, no horizontal scroll. At 1280 px: a centred card at most 420 px wide.
11. Every input has a visible label and `autocomplete` values (`email`, `current-password`, `new-password`); focus rings are visible; touch targets are at least 44 px; errors are announced with `aria-live`; the form submits with Enter.
12. Works in current Chrome, Edge, Firefox and Safari (D-044).

## Acceptance criteria

1. A new person can go from the first screen to the empty vault using only the UI. (Playwright.)
2. Reloading the page keeps the person signed in; after Log out a reload shows `/login`. (Playwright.)
3. A logged-in person can change their password from the account screen and log in with the new one. (Playwright.)
4. Every error code the screens can receive shows its message, not a raw code: `email_taken`, `weak_password`, `invalid_credentials`, `rate_limited`, `validation_error`, `wrong_password`, `account_exists`. (Vitest, one test per code.)
5. The Google button is absent when `providers` says `false` and present when `true`. (Vitest.)
6. Signed-out access to `/` and `/account` redirects to `/login`. (Vitest router test.)
7. At 390 px and 1280 px no screen overflows horizontally and every control is reachable by keyboard. (Playwright checks on both projects.)
8. The access token is never written to `localStorage`, `sessionStorage` or a cookie readable by scripts. (Playwright assertion.)

## Tests

- Vitest: `src/auth/*.test.tsx`, `src/pages/SignUp.test.tsx`, `Login.test.tsx`, `Account.test.tsx`, `src/routes.test.tsx`.
- Playwright: `e2e/auth.spec.ts` covering criteria 1 to 3, 7 and 8 at desktop and phone.
- Backend change only if an endpoint the screens need is missing.

## Verification (proof type `ui`)

- Audit passes on the final commit, including `biome ci`, `eslint`, `typecheck`, `npm test` and `npm run build`.
- `factory-proof.sh ui` on the final commit records Chromium at 1280 and 390 with video and screenshots into `.verification/e02-s06/`: sign up screen (empty, filled, each error state), login screen (including the account-exists message), the empty vault shell, the account screen before and after changing the password, and the video of the whole flow.
- Per D-049, the feature is also exercised once by hand through Claude in Chrome where that is possible, and the PR says whether it was.

## Out of scope

The file explorer shell (E08-S01), email verification and password reset (D-031), connecting Google to an existing account (E10-S08), a settings area beyond change password (D-042).

## Open questions

None.
