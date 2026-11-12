# E05-S01 Blob store port and PostgreSQL adapter

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E01-S03
- **Decisions:** D-001, D-028
- **Flows:** FLOWS.md 5.1

## Goal

File bytes are stored safely inside PostgreSQL, behind an interface that lets them move elsewhere later.

## Scope

- `BlobStore` port: store a stream, open a stream, delete, report size.
- PostgreSQL adapter that keeps bytes in their own table, apart from the file rows.
- Reading and writing in pieces, so a large file is never held whole in memory.
- An in-memory fake for tests.

## Acceptance criteria

- Listing and search queries never load file bytes.
- A stored file reads back byte-for-byte identical.
- Uploading and downloading a file at the size limit keeps memory use flat.
- The same tests pass against the PostgreSQL adapter and the fake.

## Open questions

- Chunked rows or PostgreSQL large objects?
- Do the bytes and the file row share one transaction, and how does the port express that?
