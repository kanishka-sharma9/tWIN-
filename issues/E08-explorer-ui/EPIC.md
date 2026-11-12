# E08 Explorer UI

- **Status:** Draft
- **Depends on:** E01, E02, and the API story each screen uses

## Outcome

The app looks and behaves like a desktop file explorer, with Alter as a first-class column.

## Stories

| ID | Story | Depends on | Status |
|---|---|---|---|
| [E08-S01](E08-S01-app-shell.md) | App shell and navigation | E04-S04, E02-S06, E01-S05 | Draft |
| [E08-S02](E08-S02-details-list.md) | Details list with Name and Alter columns | E08-S01 | Draft |
| [E08-S03](E08-S03-thumbnail-generation.md) | Thumbnail generation on first view | E05-S01, E05-S02 | Draft |
| [E08-S04](E08-S04-grid-view.md) | Thumbnail grid view | E08-S02, E08-S03 | Draft |
| [E08-S05](E08-S05-context-menu.md) | Right-click menu and toolbar actions | E08-S02 | Draft |
| [E08-S06](E08-S06-upload-dialog.md) | Upload dialog with alter table and pattern helper | E05-S02, E05-S03, E03-S03, E08-S01 | Draft |
| [E08-S07](E08-S07-rename-move-copy.md) | Rename, move and copy interactions | E05-S05, E05-S06, E05-S07, E04-S02, E04-S03, E08-S05 | Draft |
| [E08-S08](E08-S08-selection-bulk.md) | Selection and bulk actions | E08-S02, E05-S06, E05-S08, E06-S01 | Draft |
| [E08-S09](E08-S09-keyboard-shortcuts.md) | Keyboard shortcuts | E08-S07, E08-S08 | Draft |
| [E08-S10](E08-S10-drag-and-drop.md) | Drag and drop | E08-S06, E08-S07 | Draft |
| [E08-S11](E08-S11-bin-view.md) | Recycle bin view | E06-S02, E06-S03, E06-S04, E08-S01 | Draft |
| [E08-S12](E08-S12-search-and-goto.md) | Search box and Go-to dialog | E07-S01, E07-S02, E08-S01 | Draft |
| [E08-S13](E08-S13-states.md) | Empty, loading and error states | E08-S01, E05-S09 | Draft |

## Applies to every story in this epic

- Each screen is built and tested at desktop and phone width, with a touch route for anything that needs a mouse or keyboard (D-043, FLOWS.md 3.3).
- Supported browsers are the current Chrome, Edge, Firefox and Safari (D-044).
- Interface text is English, written directly into the screens (D-045).
- There is no up-front design. Each story settles its own look using the tokens, typeface, icons and breakpoints from E01-S05 (D-046).
- Done means the three conditions in D-049, including a pass through Claude in Chrome.
