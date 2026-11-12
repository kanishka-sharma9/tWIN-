# E06-S01 Delete to the bin

- **Epic:** E06 Recycle bin
- **Status:** Draft
- **Depends on:** E05-S02, E04-S01
- **Decisions:** D-008, D-035
- **Flows:** FLOWS.md 7.1

## Goal

A user can delete files and folders without losing them for good.

## Scope

- Mark files as deleted; a folder is marked with its whole subtree as one unit.
- Deleted items leave listings and search.
- Their pairs become free immediately.

## Acceptance criteria

- After a delete, a new file can take the same pair.
- Deleting a folder puts everything inside it in the bin.

## Open questions

None yet.
