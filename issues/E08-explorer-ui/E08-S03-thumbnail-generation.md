# E08-S03 Thumbnail generation on first view

- **Epic:** E08 Explorer UI
- **Status:** Draft
- **Depends on:** E05-S01, E05-S02
- **Decisions:** D-028, D-034
- **Flows:** FLOWS.md 10

## Goal

Images get a small preview picture for the grid view, made the first time it is needed.

## Scope

- `ThumbnailGenerator` port with an image-library adapter.
- Thumbnail endpoint that makes the thumbnail on the first request for a JPEG, PNG, GIF or WebP, stores it in PostgreSQL and reuses it afterwards.
- One thumbnail when two first requests arrive together.
- Remember images that cannot be thumbnailed, so they are not retried on every view.

## Acceptance criteria

- The first request for a photo returns a thumbnail, and the second does not make it again.
- A text file and a corrupt image both fall back to a type icon.
- Uploading an image does no thumbnail work.

## Open questions

- What thumbnail size?
