# E03-S02 Pair uniqueness invariant

- **Epic:** E03 Naming core
- **Status:** Draft
- **Depends on:** E03-S01, E02-S01
- **Decisions:** D-002, D-008, D-027
- **Flows:** FLOWS.md 4.1, 4.2

## Goal

No two live files in a vault can ever share a (name, alter) pair.

## Scope

- Name-key and alter-key columns on the file row.
- A partial unique index over live files per vault.
- The repository turns the database violation into a domain pair-taken error.
- A pre-check in the use cases for friendly messages.

## Acceptance criteria

- Two simultaneous creates of the same pair: exactly one succeeds.
- Same name with a different alter succeeds; same alter with a different name succeeds.
- A file in the bin does not block its pair.
- Pairs in different vaults never clash.

## Open questions

None yet.
