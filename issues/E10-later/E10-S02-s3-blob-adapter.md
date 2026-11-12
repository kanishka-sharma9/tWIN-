# E10-S02 Move file bytes to object storage

- **Epic:** E10 Later: hosting and apps
- **Status:** Backlog
- **Depends on:** None
- **Decisions:** D-028
- **Flows:** None

## Goal

File bytes can live in object storage if the database grows too large.

## Scope

- An S3-compatible `BlobStore` adapter.
- A way to move the existing bytes out of PostgreSQL.

## Acceptance criteria

- The blob store tests pass against the new adapter.
- Switching adapters is a configuration change.

## Open questions

None yet.
