# E08-S02 Details list with Name and Alter columns

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E08-S01
- **Decisions:** D-003, D-011
- **Flows:** FLOWS.md 3.1, 3.2

## Goal

A folder's contents show as a sortable table with Alter beside Name.

## Scope

- Columns: Name, Alter, Type, Size, Modified.
- Click a header to sort; click again to reverse.
- Rows rendered only when visible, so large folders stay smooth.
- Resizable columns; folders first.
- Double-click opens a folder or downloads a file.

## Acceptance criteria

- Sorting by Alter reorders the list.
- Scrolling a folder with thousands of files stays smooth.

## Open questions

- Is download the right double-click action for a file while there is no preview?
