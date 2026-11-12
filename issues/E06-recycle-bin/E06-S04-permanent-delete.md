# E06-S04 Permanent delete and empty bin

- **Epic:** E06 Recycle bin
- **Status:** Draft
- **Depends on:** E06-S02, E05-S09
- **Decisions:** D-035
- **Flows:** FLOWS.md 7.3

## Goal

A user can remove items for good and reclaim space.

## Scope

- Permanently delete one bin item, or everything in the bin.
- Remove rows, bytes and thumbnails.
- Update the vault's used space.

## Acceptance criteria

- The bytes are gone from the blob store.
- The item can no longer be restored.
- Usage drops by the item's size.

## Open questions

- Should the bin purge itself after some number of days? (proposed: not in v1)
