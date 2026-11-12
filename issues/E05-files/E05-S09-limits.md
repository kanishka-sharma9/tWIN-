# E05-S09 Upload size and vault quota

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S02
- **Decisions:** D-036
- **Flows:** None

## Goal

Storage use is bounded per file and per vault.

## Scope

- Settings for maximum file size and per-vault quota.
- Enforced on upload and copy, with clear error codes.
- A usage endpoint for the UI.

## Acceptance criteria

- An oversized upload is refused before its bytes are kept.
- Usage reflects uploads, copies and permanent deletes.

## Open questions

- What are the real limits? (100 MB and 5 GB are placeholders)
- Does the bin count toward the quota? (proposed: yes)
