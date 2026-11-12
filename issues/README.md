# Issues

The work for v1, arranged as 10 epics and 64 stories. Each story has a barebones spec that is meant to be fleshed out before it is implemented.

## How this folder works

- Each epic has a folder holding `EPIC.md` and one file per story.
- IDs are stable. A new story takes the next number in its epic, and nothing is renumbered.
- Every story lists the decisions (`DECISIONS.md`) and flows (`FLOWS.md`) it rests on.

**Status values**

- **Draft**: barebones spec; needs detail.
- **Ready**: spec fleshed out and open questions answered.
- **In progress**, then **Done**.
- **Backlog**: recorded for after v1.

**Before a story moves from Draft to Ready**

1. Answer its open questions.
2. Get every **Proposed** decision it lists confirmed or changed in `DECISIONS.md`.
3. Add the detail: API shapes, UI states and the list of tests.

## Definition of done (D-049)

A story is Done when:

1. All CI checks pass.
2. Every acceptance criterion has an automated test, or a written reason why it cannot have one.
3. For frontend work, the feature has been exercised in a real browser through Claude in Chrome, wherever that is possible and necessary.

Stories are not sized or dated (D-048).

## Rules for every UI story

- Built and tested at desktop and phone width, with a touch route for anything that needs a mouse or keyboard (D-043, FLOWS.md 3.3).
- Works in current Chrome, Edge, Firefox and Safari (D-044).
- English text, written directly into the screens (D-045).
- No up-front design: the story settles its own look using the shared tokens and components (D-046).

## Suggested order

Start with E01-S09, which moves the project into `backend/` and `frontend/`. Then build E01 to E07 in order. Build each E08 screen alongside the API story it depends on, so every slice can be seen working. E09 closes v1. E10 is the backlog.

## Epics

| ID | Epic | Outcome | Stories | Status |
|---|---|---|---|---|
| [E01](E01-foundation/EPIC.md) | Foundation | A developer can start the database, API and web app with documented commands and run every check. | 9 | Planned |
| [E02](E02-accounts/EPIC.md) | Accounts and login | A person can create an account with email + password or Google, gets a private vault, and stays logged in. | 8 | Draft |
| [E03](E03-naming-core/EPIC.md) | Naming core | The dual-name rule is enforced in one place and cannot be bypassed, even by simultaneous requests. | 3 | Draft |
| [E04](E04-folders/EPIC.md) | Folders | Users can build and rearrange a folder tree like Explorer's. | 4 | Draft |
| [E05](E05-files/EPIC.md) | Files | Files can be brought in, taken out, renamed, moved and copied without ever breaking the pair rule. | 9 | Draft |
| [E06](E06-recycle-bin/EPIC.md) | Recycle bin | Deleting is safe: items go to a bin, free their pair, and can come back. | 4 | Draft |
| [E07](E07-search-and-jump/EPIC.md) | Search and jump | Any file can be found by either name, or opened directly by its pair. | 2 | Draft |
| [E08](E08-explorer-ui/EPIC.md) | Explorer UI | The app looks and behaves like a desktop file explorer, with Alter as a first-class column. | 13 | Draft |
| [E09](E09-release-readiness/EPIC.md) | Release readiness (local v1) | v1 demonstrably works end to end on a developer machine, and someone new can run it. | 3 | Draft |
| [E10](E10-later/EPIC.md) | Later: hosting and apps | The path beyond v1 is written down so it is not lost. None of this is v1. | 9 | Backlog |

## Stories

### E01 Foundation

| ID | Story | Depends on |
|---|---|---|
| [E01-S01](E01-foundation/E01-S01-dev-environment.md) | Developer environment | E01-S09 |
| [E01-S02](E01-foundation/E01-S02-backend-skeleton.md) | Backend skeleton and layering | E01-S01, E01-S09 |
| [E01-S03](E01-foundation/E01-S03-database.md) | PostgreSQL and migrations | E01-S02 |
| [E01-S04](E01-foundation/E01-S04-frontend-skeleton.md) | Frontend skeleton | E01-S01, E01-S09 |
| [E01-S05](E01-foundation/E01-S05-theme-tokens.md) | Theme tokens | E01-S04 |
| [E01-S06](E01-foundation/E01-S06-api-contract.md) | API contract and typed client | E01-S02, E01-S04 |
| [E01-S07](E01-foundation/E01-S07-test-harness.md) | Test and lint harness | E01-S03, E01-S04 |
| [E01-S08](E01-foundation/E01-S08-ci-devcontainer.md) | CI and dev container | None |
| [E01-S09](E01-foundation/E01-S09-restructure-layout.md) | Restructure into backend/ and frontend/ | None |

### E02 Accounts and login

| ID | Story | Depends on |
|---|---|---|
| [E02-S01](E02-accounts/E02-S01-user-vault-model.md) | User and vault model | E01-S03 |
| [E02-S02](E02-accounts/E02-S02-signup-email.md) | Sign up with email and password | E02-S01 |
| [E02-S03](E02-accounts/E02-S03-sessions.md) | Log in, log out and tokens | E02-S02 |
| [E02-S04](E02-accounts/E02-S04-google-signin.md) | Google sign-in | E02-S03 |
| [E02-S05](E02-accounts/E02-S05-password-reset.md) | Password reset (not in v1, D-031) | E02-S03 |
| [E02-S06](E02-accounts/E02-S06-auth-screens.md) | Sign-up, login and account screens | E02-S03, E02-S04, E02-S07, E01-S05, E01-S06 |
| [E02-S07](E02-accounts/E02-S07-change-password.md) | Change password | E02-S03 |
| [E02-S08](E02-accounts/E02-S08-developer-password-reset.md) | Developer password reset command | E02-S02 |

### E03 Naming core

| ID | Story | Depends on |
|---|---|---|
| [E03-S01](E03-naming-core/E03-S01-name-alter-values.md) | Name and Alter value objects | E01-S02 |
| [E03-S02](E03-naming-core/E03-S02-pair-uniqueness.md) | Pair uniqueness invariant | E03-S01, E02-S01 |
| [E03-S03](E03-naming-core/E03-S03-pair-availability-api.md) | Pair availability check | E03-S02 |

### E04 Folders

| ID | Story | Depends on |
|---|---|---|
| [E04-S01](E04-folders/E04-S01-folder-model.md) | Folder model and rules | E02-S01, E03-S01 |
| [E04-S02](E04-folders/E04-S02-create-rename-folder.md) | Create and rename folders | E04-S01 |
| [E04-S03](E04-folders/E04-S03-move-folder.md) | Move folders | E04-S01 |
| [E04-S04](E04-folders/E04-S04-folder-listing-api.md) | Folder tree and listing API | E04-S01, E03-S02 |

### E05 Files

| ID | Story | Depends on |
|---|---|---|
| [E05-S01](E05-files/E05-S01-blob-store.md) | Blob store port and PostgreSQL adapter | E01-S03 |
| [E05-S02](E05-files/E05-S02-upload-file.md) | Upload one file with its alter | E03-S02, E04-S01, E05-S01 |
| [E05-S03](E05-files/E05-S03-bulk-upload.md) | Upload several files | E05-S02, E03-S03 |
| [E05-S04](E05-files/E05-S04-download-file.md) | Download one file | E05-S02 |
| [E05-S05](E05-files/E05-S05-rename-file.md) | Rename a name or an alter | E03-S02 |
| [E05-S06](E05-files/E05-S06-move-files.md) | Move files | E05-S02, E04-S01 |
| [E05-S07](E05-files/E05-S07-copy-files.md) | Copy files | E05-S02 |
| [E05-S08](E05-files/E05-S08-bulk-download.md) | Download several items as a zip | E05-S04 |
| [E05-S09](E05-files/E05-S09-limits.md) | Upload size and vault quota | E05-S02 |

### E06 Recycle bin

| ID | Story | Depends on |
|---|---|---|
| [E06-S01](E06-recycle-bin/E06-S01-delete-to-bin.md) | Delete to the bin | E05-S02, E04-S01 |
| [E06-S02](E06-recycle-bin/E06-S02-list-bin.md) | List the bin | E06-S01 |
| [E06-S03](E06-recycle-bin/E06-S03-restore.md) | Restore from the bin | E06-S02, E03-S02 |
| [E06-S04](E06-recycle-bin/E06-S04-permanent-delete.md) | Permanent delete and empty bin | E06-S02, E05-S09 |

### E07 Search and jump

| ID | Story | Depends on |
|---|---|---|
| [E07-S01](E07-search-and-jump/E07-S01-search.md) | Search names and alters | E05-S02, E04-S04 |
| [E07-S02](E07-search-and-jump/E07-S02-jump-by-pair.md) | Jump by pair | E03-S02 |

### E08 Explorer UI

| ID | Story | Depends on |
|---|---|---|
| [E08-S01](E08-explorer-ui/E08-S01-app-shell.md) | App shell and navigation | E04-S04, E02-S06, E01-S05 |
| [E08-S02](E08-explorer-ui/E08-S02-details-list.md) | Details list with Name and Alter columns | E08-S01 |
| [E08-S03](E08-explorer-ui/E08-S03-thumbnail-generation.md) | Thumbnail generation on first view | E05-S01, E05-S02 |
| [E08-S04](E08-explorer-ui/E08-S04-grid-view.md) | Thumbnail grid view | E08-S02, E08-S03 |
| [E08-S05](E08-explorer-ui/E08-S05-context-menu.md) | Right-click menu and toolbar actions | E08-S02 |
| [E08-S06](E08-explorer-ui/E08-S06-upload-dialog.md) | Upload dialog with alter table and pattern helper | E05-S02, E05-S03, E03-S03, E08-S01 |
| [E08-S07](E08-explorer-ui/E08-S07-rename-move-copy.md) | Rename, move and copy interactions | E05-S05, E05-S06, E05-S07, E04-S02, E04-S03, E08-S05 |
| [E08-S08](E08-explorer-ui/E08-S08-selection-bulk.md) | Selection and bulk actions | E08-S02, E05-S06, E05-S08, E06-S01 |
| [E08-S09](E08-explorer-ui/E08-S09-keyboard-shortcuts.md) | Keyboard shortcuts | E08-S07, E08-S08 |
| [E08-S10](E08-explorer-ui/E08-S10-drag-and-drop.md) | Drag and drop | E08-S06, E08-S07 |
| [E08-S11](E08-explorer-ui/E08-S11-bin-view.md) | Recycle bin view | E06-S02, E06-S03, E06-S04, E08-S01 |
| [E08-S12](E08-explorer-ui/E08-S12-search-and-goto.md) | Search box and Go-to dialog | E07-S01, E07-S02, E08-S01 |
| [E08-S13](E08-explorer-ui/E08-S13-states.md) | Empty, loading and error states | E08-S01, E05-S09 |

### E09 Release readiness (local v1)

| ID | Story | Depends on |
|---|---|---|
| [E09-S01](E09-release-readiness/E09-S01-e2e-tests.md) | End-to-end browser tests | E08 |
| [E09-S02](E09-release-readiness/E09-S02-run-guide.md) | README and run guide | E01-S07 |
| [E09-S03](E09-release-readiness/E09-S03-v1-acceptance.md) | v1 acceptance pass | E09-S01, E09-S02 |

### E10 Later: hosting and apps

| ID | Story | Depends on |
|---|---|---|
| [E10-S01](E10-later/E10-S01-hosting-droplet.md) | Host on a DigitalOcean Droplet | None |
| [E10-S02](E10-later/E10-S02-s3-blob-adapter.md) | Move file bytes to object storage | None |
| [E10-S03](E10-later/E10-S03-real-email.md) | Email: sending, password reset and verification | None |
| [E10-S04](E10-later/E10-S04-desktop-app.md) | Desktop app wrapper | E10-S01 |
| [E10-S05](E10-later/E10-S05-mobile-app.md) | Mobile app | E10-S01 |
| [E10-S06](E10-later/E10-S06-file-preview.md) | File preview | None |
| [E10-S07](E10-later/E10-S07-folder-copy.md) | Copy folders | None |
| [E10-S08](E10-later/E10-S08-more-account-settings.md) | More account settings | E10-S03 |
| [E10-S09](E10-later/E10-S09-privacy-and-terms.md) | Privacy policy and terms | E10-S01 |
