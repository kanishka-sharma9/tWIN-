# E06-S03 Restore from the bin

- **Epic:** E06 Recycle bin
- **Status:** Draft
- **Depends on:** E06-S02, E03-S02
- **Decisions:** D-008, D-035
- **Flows:** FLOWS.md 7.2

## Goal

A user can bring a deleted item back, even if its pair has since been taken.

## Scope

- Restore to the original folder; ask for a destination if that folder is gone.
- If any pair is now taken, return those files so the user can change a name or alter, then retry.
- Handle a folder-name clash at the destination.

## Acceptance criteria

- Restoring an item with no conflicts is one step.
- A conflicting restore succeeds once the user changes the name or alter.
- Restoring a folder with some conflicts lists exactly the conflicting files.

## Open questions

- Can a folder be partly restored, or is it all-or-nothing?
