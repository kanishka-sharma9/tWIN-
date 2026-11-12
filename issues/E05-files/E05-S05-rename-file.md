# E05-S05 Rename a name or an alter

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E03-S02
- **Decisions:** D-002, D-005
- **Flows:** FLOWS.md 5.4

## Goal

A user can change a file's name, its alter, or both.

## Scope

- One endpoint that changes either or both values.
- Revalidate and recheck the pair; clash returns `pair_taken` with the other file's location.

## Acceptance criteria

- Renaming to a pair held only by a file in the bin succeeds.
- Changing only the capitalisation of a file's own name or alter succeeds.

## Open questions

- Warn when a rename changes the extension, as Explorer does?
