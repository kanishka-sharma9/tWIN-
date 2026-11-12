# E07-S02 Jump by pair

- **Epic:** E07 Search and jump
- **Status:** Draft
- **Depends on:** E03-S02
- **Decisions:** D-002, D-033
- **Flows:** FLOWS.md 8.2

## Goal

A user who knows a file's name and alter can go straight to it.

## Scope

- Lookup endpoint taking an exact name and alter, ignoring case.
- Returns the file and its folder path, or a not-found answer.

## Acceptance criteria

- An existing pair returns exactly one file.
- A pair that exists only in the bin is reported as not found.

## Open questions

None yet.
