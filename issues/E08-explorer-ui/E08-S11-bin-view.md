# E08-S11 Recycle bin view

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E06-S02, E06-S03, E06-S04, E08-S01
- **Decisions:** D-008, D-035
- **Flows:** FLOWS.md 7

## Goal

A user can review, restore and permanently delete binned items.

## Scope

- A bin entry in the tree.
- List with name, alter, original location and deletion date.
- Restore, delete permanently, empty bin.
- Restore-conflict dialog asking for a new name or alter, as a table when there are several.

## Acceptance criteria

- A conflicting restore can be completed without leaving the bin view.
- Emptying the bin asks for confirmation.

## Open questions

None yet.
