# E05-S04 Download one file

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S02
- **Decisions:** D-039
- **Flows:** FLOWS.md 5.3

## Goal

A user can get a file back out, under its name.

## Scope

- Streaming download endpoint scoped to the caller's vault.
- Correct content type and a download name that survives non-English characters.

## Acceptance criteria

- Downloaded bytes are identical to what was uploaded.
- Another account requesting the same file gets 404.

## Open questions

None yet.
