# E05-S06 Move files

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S02, E04-S01
- **Decisions:** D-002, D-039
- **Flows:** FLOWS.md 5.5

## Goal

A user can move one or many files to another folder.

## Scope

- Move endpoint for one or many files.
- Refuse destinations in the bin or in another vault.

## Acceptance criteria

- A file move never returns a pair conflict.
- Moved files appear in the destination and leave the source.

## Open questions

- Is a multi-file move all-or-nothing?
