# E04-S02 Create and rename folders

- **Epic:** E04 Folders
- **Status:** Draft
- **Depends on:** E04-S01
- **Decisions:** D-007
- **Flows:** FLOWS.md 6.1

## Goal

A user can add a folder and change its name.

## Scope

- Create-in-parent and rename endpoints.
- A `folder_name_taken` error on a sibling clash.

## Acceptance criteria

- A created folder appears in its parent's listing.
- Renaming to a sibling's name, in any capitalisation, is refused.

## Open questions

- What is the default name for a new folder?
