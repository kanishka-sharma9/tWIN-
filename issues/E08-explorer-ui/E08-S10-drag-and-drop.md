# E08-S10 Drag and drop

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E08-S06, E08-S07
- **Decisions:** D-011, D-043
- **Flows:** FLOWS.md 9

## Goal

A user can drop files in to upload and drag items onto folders to move them.

## Scope

- Dropping files from the desktop opens the upload dialog for that destination.
- Dragging items onto a folder in the list, tree or breadcrumb moves them.
- Highlight valid targets; refuse invalid ones.
- On touch screens the same uploads and moves are reachable from the file picker and the Move to action.

## Acceptance criteria

- Nothing uploads from a drop until every alter is typed.
- A folder cannot be dropped into itself or its own subtree.

## Open questions

- Should dropping a whole folder from the desktop be supported? (proposed: not in v1)
