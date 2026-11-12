# E05-S02 Upload one file with its alter

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E03-S02, E04-S01, E05-S01
- **Decisions:** D-002, D-004, D-037
- **Flows:** FLOWS.md 5.1

## Goal

A user can add a file by giving it a name and an alter.

## Scope

- Multipart endpoint taking the file, name, alter and destination folder.
- Validate, check size and quota, store the bytes, insert the row.
- On pair-taken, remove the stored bytes and return 409 `pair_taken`.
- Record size and content type.

## Acceptance criteria

- An upload without an alter is refused.
- An upload with a taken pair is refused and leaves no bytes behind.
- The file appears in the folder listing.

## Open questions

None yet.
