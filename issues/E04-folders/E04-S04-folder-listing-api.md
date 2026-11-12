# E04-S04 Folder tree and listing API

- **Epic:** E04 Folders
- **Status:** Draft
- **Depends on:** E04-S01, E03-S02
- **Decisions:** D-003, D-011
- **Flows:** FLOWS.md 3.1

## Goal

The UI can show the tree and the contents of any folder.

## Scope

- Children-of-folder endpoint for the lazily loaded tree.
- Listing endpoint returning subfolders and files with name, alter, type, size and modified date.
- Sorting by any column on the server, with paging.
- Breadcrumb path in the response.

## Acceptance criteria

- Sorting by Alter works in both directions.
- Folders come before files.
- A folder with thousands of files still answers quickly, one page at a time.

## Open questions

- Page size, and cursor or offset paging?
