# E04-S03 Move folders

- **Epic:** E04 Folders
- **Status:** Draft
- **Depends on:** E04-S01
- **Decisions:** D-039
- **Flows:** FLOWS.md 6.2

## Goal

A user can move a folder, with everything in it, to another place in the tree.

## Scope

- Move-to-parent endpoint.
- Refuse a move into the folder itself or a descendant.
- Sibling clash returns a conflict the UI can resolve with a new name.

## Acceptance criteria

- A folder cannot be moved into its own subtree.
- A clash is resolved by retrying with a new name.
- Files inside keep their pairs untouched.

## Open questions

None yet.
