# E05-S03 Upload several files

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S02, E03-S03
- **Decisions:** D-012, D-037
- **Flows:** FLOWS.md 5.2

## Goal

A user can add many files in one go, each with its own alter.

## Scope

- One request per file, so failures are independent.
- Use the batch availability check before starting.
- Limit how many uploads run at once.

## Acceptance criteria

- In a batch where one pair is taken, the rest upload and the failing file is reported with its reason.
- Duplicates inside the batch are caught before any upload starts.

## Open questions

- Per-file results (proposed) or all-or-nothing for the batch?
