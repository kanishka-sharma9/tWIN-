# E08-S12 Search box and Go-to dialog

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E07-S01, E07-S02, E08-S01
- **Decisions:** D-033
- **Flows:** FLOWS.md 8

## Goal

A user can search and jump from anywhere in the app.

## Scope

- Search box in the toolbar with results showing name, alter and location.
- Open-location action on a result.
- Go-to dialog with Name and Alter fields that opens the folder and selects the file.
- Typing `name | alter` in the search box jumps straight to that file.

## Acceptance criteria

- Selecting a search result shows the item in its folder.
- Go-to with an unknown pair says so and stays open.
- `name | alter` in the search box behaves exactly like the Go-to dialog.

## Open questions

None yet.
