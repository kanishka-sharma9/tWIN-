# E04-S01 Folder model and rules

- **Epic:** E04 Folders
- **Status:** Draft
- **Depends on:** E02-S01, E03-S01
- **Decisions:** D-007, D-032
- **Flows:** FLOWS.md 6.1

## Goal

Folders form a tree with Explorer's naming rule.

## Scope

- `folders` table with a parent link and one root folder per vault.
- Sibling names unique among live folders, ignoring case.
- No cycles.

## Acceptance criteria

- A duplicate sibling name is refused; the same name under different parents is allowed.
- The root folder cannot be renamed, moved or deleted.

## Open questions

None yet.
