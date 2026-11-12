# E05-S07 Copy files

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S02
- **Decisions:** D-004, D-039
- **Flows:** FLOWS.md 5.6

## Goal

A user can duplicate a file under a new pair.

## Scope

- Copy endpoint that requires a new alter and accepts a new name.
- Batch input for copying several files.
- Quota applies to the copy.

## Acceptance criteria

- A copy that keeps the original pair is refused.
- The copy appears in the destination with its own bytes.

## Open questions

- Duplicate the bytes (proposed) or share them between copies?
- Confirm that copying folders is left out of v1.
