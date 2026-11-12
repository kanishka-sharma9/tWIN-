# E07-S01 Search names and alters

- **Epic:** E07 Search and jump
- **Status:** Draft
- **Depends on:** E05-S02, E04-S04
- **Decisions:** D-003, D-033
- **Flows:** FLOWS.md 8.1

## Goal

A user can find items by typing part of a name or an alter.

## Scope

- Case-insensitive contains-match across file names, alters and folder names, over the whole vault.
- Exclude the bin.
- Results carry each item's location; paged.
- Add a text index if needed for speed.

## Acceptance criteria

- Typing part of an alter finds the file.
- Items in the bin and in other vaults never appear.

## Open questions

- Is a 'this folder only' option wanted?
