# E08-S06 Upload dialog with alter table and pattern helper

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E05-S02, E05-S03, E03-S03, E08-S01
- **Decisions:** D-004, D-012
- **Flows:** FLOWS.md 5.1, 5.2

## Goal

A user can upload one or many files, typing an alter for each.

## Scope

- One file: name prefilled from the file, alter empty and required.
- Several files: a table with name, alter and status per row.
- Pattern helper that fills empty alters from a prefix and a running number; rows stay editable.
- Live pair check per row and highlighting of duplicates inside the batch.
- Progress per row, and retry for failed rows only.

## Acceptance criteria

- Upload cannot start while any alter is empty or any pair is taken.
- A row that fails stays in the table with its reason.

## Open questions

- Exact pattern options: start number, zero padding, suffix?
