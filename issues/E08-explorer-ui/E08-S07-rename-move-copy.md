# E08-S07 Rename, move and copy interactions

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E05-S05, E05-S06, E05-S07, E04-S02, E04-S03, E08-S05
- **Decisions:** D-004, D-039
- **Flows:** FLOWS.md 5.4, 5.5, 5.6, 6

## Goal

A user can rename, move and copy from the list, with clear messages on a pair clash.

## Scope

- Edit the name in place; edit the alter in its own cell.
- A clash message that says where the conflicting file is.
- Move through a folder picker.
- Copy dialog that asks for a new alter; several files reuse the upload table.

## Acceptance criteria

- A clash keeps the edit open with the message shown.
- A copy cannot be confirmed without a new alter.

## Open questions

None yet.
