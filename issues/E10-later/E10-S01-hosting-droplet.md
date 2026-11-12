# E10-S01 Host on a DigitalOcean Droplet

- **Epic:** E10 Later: hosting and apps
- **Status:** Backlog
- **Depends on:** None
- **Decisions:** D-014, D-021
- **Flows:** None

## Goal

The app is reachable on the internet.

## Scope

- Compose file for API, PostgreSQL and a reverse proxy with HTTPS.
- Backups for the database, which also holds the file bytes (D-028).
- Domain name and secrets handling.
- Re-check prices and the alternatives recorded in D-021 first.

## Acceptance criteria

- A second device can sign up and use a vault over HTTPS.
- A backup can be restored.

## Open questions

None yet.
