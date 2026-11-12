# E05 Files

- **Status:** Draft
- **Depends on:** E03, E04

## Outcome

Files can be brought in, taken out, renamed, moved and copied without ever breaking the pair rule.

## Stories

| ID | Story | Depends on | Status |
|---|---|---|---|
| [E05-S01](E05-S01-blob-store.md) | Blob store port and PostgreSQL adapter | E01-S03 | Draft |
| [E05-S02](E05-S02-upload-file.md) | Upload one file with its alter | E03-S02, E04-S01, E05-S01 | Draft |
| [E05-S03](E05-S03-bulk-upload.md) | Upload several files | E05-S02, E03-S03 | Draft |
| [E05-S04](E05-S04-download-file.md) | Download one file | E05-S02 | Draft |
| [E05-S05](E05-S05-rename-file.md) | Rename a name or an alter | E03-S02 | Draft |
| [E05-S06](E05-S06-move-files.md) | Move files | E05-S02, E04-S01 | Draft |
| [E05-S07](E05-S07-copy-files.md) | Copy files | E05-S02 | Draft |
| [E05-S08](E05-S08-bulk-download.md) | Download several items as a zip | E05-S04 | Draft |
| [E05-S09](E05-S09-limits.md) | Upload size and vault quota | E05-S02 | Draft |
