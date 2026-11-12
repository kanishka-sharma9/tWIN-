# E05-S08 Download several items as a zip

- **Epic:** E05 Files
- **Status:** Draft
- **Depends on:** E05-S04
- **Decisions:** D-039
- **Flows:** FLOWS.md 5.3

## Goal

A user can download a selection in one go.

## Scope

- Streamed zip of the selected files.
- Entries that would share a name get ` [alter]` before the extension.

## Acceptance criteria

- Two selected files with the same name both appear in the zip, told apart by alter.
- Large selections stream without being built in memory.

## Open questions

- If the selection includes folders, are their contents included as subfolders?
