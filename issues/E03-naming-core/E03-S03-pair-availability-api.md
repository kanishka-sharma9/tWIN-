# E03-S03 Pair availability check

- **Epic:** E03 Naming core
- **Status:** Draft
- **Depends on:** E03-S02
- **Decisions:** D-037
- **Flows:** FLOWS.md 4.1, 5.2

## Goal

The UI can tell the user a pair is taken before they submit.

## Scope

- An endpoint answering whether one pair is free, and a batch version.
- On a clash, return where the conflicting file is.
- The batch version also flags duplicates inside the batch.

## Acceptance criteria

- Answers always match what a real create would do at that moment.
- A batch containing the same pair twice flags both rows.

## Open questions

- Should the response include the conflicting file's folder path? (proposed: yes)
