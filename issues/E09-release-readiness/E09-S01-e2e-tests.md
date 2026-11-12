# E09-S01 End-to-end browser tests

- **Epic:** E09 Release readiness (local v1)
- **Status:** Draft
- **Depends on:** E08
- **Decisions:** D-022, D-043, D-044
- **Flows:** None

## Goal

The main flows are proven in a real browser.

## Scope

- Sign up, upload with an alter, hit a pair conflict, change the alter.
- Move, delete, reuse the freed pair, restore with a collision.
- Search and Go-to.
- Bulk upload with the pattern helper.
- Run against the local stack with a clean database.
- Run on Chromium, Firefox and WebKit, with the main flows repeated at phone size.

## Acceptance criteria

- The suite passes from a clean checkout following the README.

## Open questions

None yet.
