# E03-S01 Name and Alter value objects

- **Epic:** E03 Naming core
- **Status:** Draft
- **Depends on:** E01-S02
- **Decisions:** D-005, D-006, D-032
- **Flows:** FLOWS.md 4.1

## Goal

Names and alters are validated and compared the same way everywhere.

## Scope

- `FileName`, `Alter` and `FolderName` types that own their validation.
- Comparison keys built by trimming, Unicode NFC normalisation and case-folding.
- One error code per broken rule.

## Acceptance criteria

- Tests cover case differences, composed versus decomposed Unicode, whitespace and forbidden characters.
- An invalid name or alter cannot be constructed.

## Open questions

- Is 100 characters the right maximum for an alter?
- Should Windows-reserved names such as CON be refused?
- Are emoji allowed? (proposed: yes)
