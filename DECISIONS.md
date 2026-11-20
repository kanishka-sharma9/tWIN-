# Decisions

Every product and technical decision for the dual-name file explorer, with the options that were weighed. Add new entries at the end of a section and never renumber: stories in `issues/` refer to these IDs.

**Status values**

- **Accepted**: chosen by the project owner (all on 2026-11-10 unless dated otherwise). "Changed" in the index means the owner chose differently from the default first proposed.
- **Proposed**: a default put forward during planning so the picture is complete. The owner has not confirmed it. Confirm or change it before any story that lists it moves to Ready.
- **Deferred**: intentionally left for later. The entry records the current recommendation.

| ID | Decision | Status |
|---|---|---|
| D-001 | Storage model: app-managed vault | Accepted |
| D-002 | The (name, alter) pair is unique across the whole vault | Accepted |
| D-003 | The second name is called the "Alter" | Accepted |
| D-004 | The alter is always typed by the user | Accepted |
| D-005 | Comparison ignores case, display keeps it | Accepted |
| D-006 | The extension is part of the name | Accepted |
| D-007 | Folders have a name only | Accepted |
| D-008 | Delete goes to a recycle bin and frees the pair | Accepted |
| D-009 | One private vault per account | Accepted |
| D-010 | Login by email + password and by Google | Accepted |
| D-011 | v1 scope | Accepted |
| D-012 | Bulk upload uses a table with a pattern helper | Accepted |
| D-013 | Theme: oxblood, dusty rose, electric cyan | Accepted |
| D-014 | Web first, desktop and mobile later | Accepted |
| D-015 | Python backend, TypeScript frontend | Accepted |
| D-016 | Frontend framework: Vite + React | Accepted |
| D-017 | UI kit: Tailwind + shadcn/ui | Accepted |
| D-018 | Backend framework: FastAPI | Accepted |
| D-019 | Database: PostgreSQL from the start | Accepted |
| D-020 | PostgreSQL runs through Docker Compose | Accepted |
| D-021 | Hosting: local only for now | Accepted (host choice Deferred) |
| D-022 | Testing: rules, API and a few browser tests | Accepted |
| D-023 | Work tracking and living documents | Accepted |
| D-024 | Architecture: ports and adapters, SOLID | Accepted |
| D-025 | Repository layout: `backend/` and `frontend/` | Accepted (changed) |
| D-026 | Persistence stack | Accepted |
| D-027 | How pair uniqueness is enforced | Accepted |
| D-028 | Blob storage: inside PostgreSQL | Accepted (changed) |
| D-029 | Login tokens: JWT access and refresh | Accepted (changed) |
| D-030 | Password hashing and the Google sign-in rule | Accepted (changed) |
| D-031 | Email: not in v1 | Accepted (changed) |
| D-032 | Name and alter validation rules | Accepted |
| D-033 | Search and jump-by-pair behaviour | Accepted (changed) |
| D-034 | Thumbnails: made on first view | Accepted (changed) |
| D-035 | Recycle bin details | Accepted |
| D-036 | Upload size and vault quota | Accepted |
| D-037 | API contract and frontend data layer | Accepted |
| D-038 | Tooling | Accepted |
| D-039 | Copy, move and download semantics | Accepted |
| D-040 | Desktop and mobile wrappers | Deferred |
| D-041 | CI and dev container | Accepted |
| D-042 | Account settings in v1: change password only | Accepted |
| D-043 | Screens: fully responsive, phones included | Accepted |
| D-044 | Supported browsers | Accepted |
| D-045 | Interface language: English only | Accepted |
| D-046 | Visual design happens in code, story by story | Accepted |
| D-047 | Product name: tWIN!! | Accepted |
| D-048 | Stories are not sized | Accepted |
| D-049 | Definition of done | Accepted |
| D-050 | Python package and script name: twin | Accepted |
| D-051 | Where the version pins live | Accepted |
| D-052 | How the theme colours are applied | Accepted |
| D-053 | Typeface, icon set, theme variant and API client libraries | Proposed |
| D-054 | TypeScript pinned to 5.9 for typescript-eslint and openapi-typescript | Accepted |
| D-059 | E02-S01 build choices: root folder name, credential rule, unit of work | Proposed |
| D-060 | E02-S02 build choices: signup validation, hasher and logging | Proposed |
| D-062 | E02-S04 build choices: Google flow, state cookie, ID token checks and failures | Proposed |
| D-063 | E02-S07 build choices: change-password order of checks, kept session, shared limiter, Swagger bearer | Proposed |
| D-064 | E02-S08 build choices: set-password reads, errors and help | Proposed |
| D-065 | E02-S06 build choices: auth state, routes, messages and dev proxy | Proposed |

---

## Product

### D-001 Storage model: app-managed vault

**Status:** Accepted

**Decision:** Files are imported into the app's own storage. File bytes are stored under generated IDs, and every name lives in the database.

**Options considered**

- **App-managed vault (chosen):** two files in one folder can share a name and differ only by alter, and it behaves the same on web, desktop and mobile. Files are not visible in Windows Explorer or Finder unless downloaded.
- **Real files on disk:** no import step and familiar. The OS forbids two same-named files in one folder, changes made outside the app break alters, and browsers and phones restrict disk access heavily.
- **Cloud drive with accounts from day one:** reachable from any device. Needs a backend, hosting and security work immediately.

**Consequences:** upload and download are the only way in and out. The name a user sees has nothing to do with what is on disk.

### D-002 The (name, alter) pair is unique across the whole vault

**Status:** Accepted

**Decision:** No two live files in a vault may have the same (name, alter) pair. Two files may share a name, or share an alter, but not both. The folder a file sits in plays no part in the rule.

**Options considered**

- **Across the vault (chosen):** the pair works as an address, so any file can be opened from anywhere by name + alter, and moving a file can never collide. Finding a free pair gets harder as the vault grows.
- **Within a folder:** like normal file systems and simple to explain. Moves and copies can collide and need a rename prompt.

**Consequences:** enables jump-by-pair (D-033). File moves need no conflict handling. A copy always needs a new pair (D-039).

### D-003 The second name is called the "Alter"

**Status:** Accepted

**Decision:** The alternate name is called the **Alter** (short for alter ego). It is shown in its own sortable column beside Name, as in Explorer's details view, and it is searchable.

**Options considered:** Alter (chosen), Codename, Callsign, Flipside.

### D-004 The alter is always typed by the user

**Status:** Accepted

**Decision:** Every file must have an alter and the user always types it. The app never generates one and never allows it to be blank.

**Options considered**

- **Always typed (chosen):** every alter is deliberate. Importing many files means supplying many alters.
- **Auto-suggested, editable:** effortless bulk import. Generated alters feel arbitrary.
- **Optional:** least friction. Only one file per name could be blank, and files without an alter lose the feature.

**Consequences:** every path that creates a file (upload, bulk upload, copy, restore after a collision) must collect an alter. Bulk paths use the table in D-012.

### D-005 Comparison ignores case, display keeps it

**Status:** Accepted

**Decision:** When checking whether a pair is taken, `Report.pdf` and `report.pdf` are the same. The capitalisation the user typed is stored and displayed.

**Options considered**

- **Ignore case (chosen):** matches Windows and macOS, prevents look-alike duplicates, makes search forgiving.
- **Case matters:** more pairs available, at the price of look-alike files and stricter search.

### D-006 The extension is part of the name

**Status:** Accepted

**Decision:** `report.pdf` and `report.docx` are different names, exactly as in Explorer, so they may share an alter.

**Options considered**

- **Part of the name (chosen):** familiar.
- **Stored separately:** cleaner names, but unlike Explorer, and two formats of one document would need different alters.

### D-007 Folders have a name only

**Status:** Accepted

**Decision:** Folders have one name and no alter. A folder's name must be unique among the folders in the same parent.

**Options considered**

- **Name only (chosen):** keeps the alter special to files and keeps breadcrumbs short.
- **Folders get alters too:** consistent, but more typing for every folder and longer paths.

**Note:** applying the D-005 case rule to folder names is part of D-032 (Proposed).

### D-008 Delete goes to a recycle bin and frees the pair

**Status:** Accepted

**Decision:** Deleted items go to a recycle bin and can be restored. While an item is in the bin its pair is free for other files to use.

**Options considered**

- **Bin, pair freed (chosen):** a pair is reusable immediately. Restoring can collide with a newer file and then needs a new name or alter.
- **Bin, pair stays reserved:** restore always works, but the pair is blocked until the bin is emptied.
- **Permanent delete:** simplest, no undo.

**Consequences:** the uniqueness guarantee covers live files only (D-027). Restore needs a collision flow (FLOWS.md section 7.2).

### D-009 One private vault per account

**Status:** Accepted

**Decision:** Anyone can sign up, and each account gets its own vault. "Across everything" in D-002 means across that one vault. Two accounts can hold the same pair.

**Options considered**

- **Private vault per account (chosen):** the product shape. Needs sign-up, login, password reset and per-user limits in v1.
- **One shared team vault:** no public sign-up. Becoming a public product later would mean adding vault ownership.
- **Single user:** simplest. More users later would be a retrofit.

**Consequences:** every query is scoped to the caller's vault. Login is part of v1 even though the app only runs locally.

### D-010 Login by email + password and by Google

**Status:** Accepted

**Decision:** v1 offers both email + password and Google sign-in.

**Options considered**

- **Both (chosen):** widest choice for users. Roughly double the login work and testing.
- **Email + password only:** works fully offline. The project owns its security and needs an email service for resets once hosted.
- **Google only:** no passwords to store. Needs a Google Cloud setup and excludes people without a Google account.
- **Managed service (Clerk, Auth0):** least security code. An outside dependency that needs internet even locally and is hard to leave.

**Consequences:** Google sign-in needs an OAuth client created in the Google Cloud Console and an internet connection during that login. Email + password keeps working offline.

### D-011 v1 scope

**Status:** Accepted (the core list was presented and no objection was raised; the extras were chosen explicitly)

**Core**

- Sign-up and login (D-010).
- Folder tree with breadcrumbs.
- Details list with sortable Name, Alter, Type, Size and Modified columns.
- Upload (asks for the alter), download, rename of either name, move, copy, delete, new folder.
- Right-click menu.
- Search across names and alters.
- Jump-by-pair: type a name and an alter to open that file from anywhere.

**Extras chosen for v1:** thumbnail grid view, bulk select with keyboard shortcuts, drag and drop.

**Offered and not chosen for v1:** file preview (kept in the backlog as E10-S06).

**Adjusted on 2026-11-11:** change password is added (D-042); every screen also works at phone width (D-043); password reset by email leaves v1 (D-031).

### D-012 Bulk upload uses a table with a pattern helper

**Status:** Accepted

**Decision:** When several files are uploaded together, each is listed in a table with an alter box. An optional helper fills alters from a pattern the user types (for example a prefix and a running number), and each row stays editable.

**Options considered**

- **Table plus pattern helper (chosen):** faster for batches. Patterned alters carry less meaning.
- **Table, type each alter:** truest to D-004, slow for large batches.

### D-013 Theme: oxblood, dusty rose, electric cyan

**Status:** Accepted

**Decision:** Three colours: two that blend and one that does not.

| Role | Colour | Hex |
|---|---|---|
| Base (dark) | Oxblood | `#4A0E1B` |
| Base (light) | Dusty rose | `#E3B5AE` |
| Accent | Electric cyan | `#00E5FF` |

**Rules that follow from the colours**

- Oxblood and dusty rose contrast at about 8.4:1, so either can be text on the other.
- Cyan on oxblood contrasts at about 10:1. Cyan on dusty rose is about 1.2:1, so cyan is only ever used on oxblood surfaces.
- The three values live in one token file, so changing the theme is a one-place edit.

**Options considered:** an earlier neutral set (sand + black & orange, bone + navy & lime, fog + forest & pink, lilac + aubergine & yellow) was rejected as too basic. The bold set offered was Klein blue + periwinkle & chartreuse, oxblood + dusty rose & cyan (chosen), mustard + olive & ultraviolet, tomato + peach & cobalt.

---

## Platform and stack

### D-014 Web first, desktop and mobile later

**Status:** Accepted

**Decision:** The goal is an app on desktop and mobile. v1 is a web app, because the team has not built or published an app before and a web app has nothing to install, sign or get through store review.

**Migration path** (efforts are rough planning estimates; fees are as known at planning time and need re-checking before paying)

| Step | What changes | Rough effort | Money |
|---|---|---|---|
| 1. Local web app (v1) | Nothing is published | The `issues/` backlog | None |
| 2. Hosted web app | API, database and files move to a server; HTTPS; backups; real email | About 1 week | $4-6/month (D-021) plus a domain name |
| 3. Desktop app | The same web build wrapped in a desktop shell; installers; signing; updates | 1-2 weeks | Apple Developer Program ($99/year) for macOS; a Windows code-signing certificate |
| 4. Mobile app | Wrapper around the web build; store listings and review. The phone layout (D-043) and token login (D-029) are already part of v1 | 1-3 weeks (was 3-6 before D-043) | Apple ($99/year, shared with macOS); Google Play ($25 once); a Mac or a cloud Mac build service for iOS |

**Consequences**

- Because the backend is a Python server with PostgreSQL (D-018, D-019), the desktop and mobile apps will be online clients of the hosted server. Hosting (step 2) therefore comes before either app.
- An offline mode is out of scope.
- The frontend must stay a pure client-side build so it can be wrapped (this drove D-016).

### D-015 Python backend, TypeScript frontend

**Status:** Accepted

**Decision:** The team is comfortable with Python and JavaScript/TypeScript, so those are the only languages used. Flutter was excluded because it needs Dart.

### D-016 Frontend framework: Vite + React

**Status:** Accepted

**Options considered** (judged for an interactive tool with no SEO needs that gets wrapped for desktop and mobile later)

| Option | Wraps into desktop/mobile later | Main strength | Main cost |
|---|---|---|---|
| **Vite + React (chosen)** | Yes, builds to plain static files | Same React components and libraries as Next.js with far fewer moving parts | No server rendering (not needed here); the router is chosen separately |
| Next.js | Only in static-export mode, which switches off its server features | Largest ecosystem; best for SEO-heavy public sites | Its server would duplicate the Python backend |
| SvelteKit | Yes, with its static adapter | Least boilerplate, small bundles | Smaller ecosystem for tree views, virtual lists and drag-and-drop |
| Expo (React Native) | Native on mobile; desktop support is weak | Real native mobile UI | Web and desktop become second-class |

### D-017 UI kit: Tailwind + shadcn/ui

**Status:** Accepted

**Options considered**

- **Tailwind + shadcn/ui (chosen):** accessible unstyled parts that the project owns and themes fully, which suits D-013. More assembly; the table and tree come from separate libraries.
- **MUI:** data grid and tree view ready-made. Looks like Google Material unless heavily overridden; advanced grid features are paid.
- **Ant Design:** rich table, tree and upload components. Strong default look that resists theming; large download.
- **Plain CSS:** total control. Slowest, and keyboard and screen-reader behaviour is built by hand.

### D-018 Backend framework: FastAPI

**Status:** Accepted

**Options considered**

- **FastAPI (chosen):** typed, generates API docs and a schema the frontend types are built from, and fits layered architecture cleanly. Login, database layer and migrations come from separate libraries.
- **Django + REST framework:** login, admin, database layer and migrations built in. Heavier, and its database-everywhere style makes clean layering harder to keep.
- **Flask:** smallest. Everything assembled by hand, no built-in validation or typed docs.

### D-019 Database: PostgreSQL from the start

**Status:** Accepted

**Options considered**

- **PostgreSQL from the start (chosen):** the same database in development and production, built for many simultaneous users. A database server must run before any feature exists.
- **SQLite now, PostgreSQL-ready:** a single file with no setup. One writer at a time, and a migration step later.

**Consequences:** Docker is needed to develop (D-020). A desktop app cannot simply bundle the backend, which is why D-014 treats the apps as online clients.

### D-020 PostgreSQL runs through Docker Compose

**Status:** Accepted

**Decision:** A `docker-compose.yml` starts a pinned PostgreSQL version. The same file can later run on the hosted server.

**Options considered**

- **Docker Compose (chosen):** one command, reproducible. Docker Desktop must be running during development.
- **Installed in WSL with apt:** lighter. Version tied to Ubuntu, manual setup per machine, differs from the hosted setup.

**One-time setup needed:** Docker Desktop is installed on Windows, but its WSL integration is off for the Ubuntu distro. Turn it on under Settings > Resources > WSL integration.

### D-021 Hosting: local only for now

**Status:** Accepted for v1. The choice of host is **Deferred**.

**Decision:** v1 runs on the developer's own machine. Nothing is hosted until v1 works.

**Recommendation recorded for later:** a DigitalOcean Droplet at $4-6/month, holding the API, PostgreSQL and the files on one always-on machine.

**Why not a free tier:** the app needs Python compute, a database and persistent file storage, and no free tier offers all three in one place. Figures below were gathered on 2026-11-10 from third-party pages dated September to October 2026; free tiers were cut repeatedly during 2025-26, so re-check before choosing.

| Option | Cost | What it gives | Catches |
|---|---|---|---|
| **DigitalOcean Droplet (recommended)** | $4/month (512 MB) or $6/month (1 GB) | One always-on machine for everything | Not free; the server needs maintaining (updates, backups, HTTPS) |
| DigitalOcean free tier | $0 | Static sites only (3 apps, 1 GiB transfer each) | No free compute, database or file storage; it could host only the built frontend |
| Render free + Neon + object storage | $0 | 512 MB Python service, 1 GB PostgreSQL, separate file storage | Sleeps after 15 idle minutes and takes about a minute to wake; disk is wiped on restart; three or four services to wire together |
| Oracle Cloud Always Free | $0 | A real VM (2 cores, 12 GB RAM) | Card required; capacity often unavailable; idle machines can be reclaimed; hardest setup |
| Koyeb free | $0 | One 512 MB web service | Card with a $29 hold; no persistent disk; scales to zero after an hour |

**Not confirmed:** sources disagree on whether Cloudflare R2 still has a 10 GB free allowance, and on DigitalOcean's sign-up credit ($5 on its pricing page, $200 for 60 days on some third-party pages). The list the owner pointed to (hostlist.io/best/free-hosting) could not be read because it blocked automated access.

**What keeps this decision cheap to change:** the database and file storage sit behind interfaces (D-024, D-028), so the host is a configuration choice.

**Sources:** [flaviocopes free tiers](https://flaviocopes.com/hosting-free-tiers/), [DigitalOcean pricing](https://www.digitalocean.com/pricing), [SnapDeploy state of free hosting](https://snapdeploy.dev/state-of-free-hosting), [Swyftstack free Postgres](https://swyftstack.com/blog/free-postgresql-hosting).

### D-022 Testing: rules, API and a few browser tests

**Status:** Accepted

**Decision:** Three layers of automated tests: fast tests on the rules (uniqueness, bin, move), API tests against a real PostgreSQL, and a handful of end-to-end browser runs of the main flows.

**Options considered:** the chosen set; rules + API only (UI regressions caught by hand); rules only (most breakage found manually).

### D-023 Work tracking and living documents

**Status:** Accepted

**Decision:** Decisions are recorded in `DECISIONS.md`, flows in `FLOWS.md`, and the work is arranged as epics and stories under `issues/`, each with a barebones spec that is fleshed out before it is implemented. The architecture follows SOLID principles. Choices are put to the owner with trade-offs instead of being assumed.

### D-041 CI and dev container

**Status:** Accepted on 2026-11-11. This replaces "No CI pipeline in v1", which was proposed in D-038.

**Decision**

- **CI:** GitHub Actions (`.github/workflows/ci.yml`) runs on pushes to `main` and on pull requests, with one job each for Python and web. The Python job runs `uv sync --locked`, `ruff format --check`, `ruff check`, `ty check`, `mypy` and `pytest`. The web job runs `npm ci`, `biome ci`, `eslint`, `npm run typecheck`, `npm test` and `npm run build`, and does nothing until `frontend/package.json` exists (E01-S04).

  *Update 2026-11-12 (E01-S09):* the Python job runs from `backend/` and the web job from `frontend/` (earlier text said `web/`).
- **Dev container:** `.devcontainer/` is built on the `base:ubuntu-24.04` image with features for uv, Node 26 and Docker-in-Docker. Docker-in-Docker lets `docker compose up` for PostgreSQL (D-020) work as it does in WSL. The container's virtualenv lives at `/home/vscode/.venv` (`UV_PROJECT_ENVIRONMENT`), outside the bind-mounted checkout, so it never clashes with the `.venv` made in WSL. Working in WSL directly (E01-S01) stays supported.
- Versions come from one place each: Python from `backend/.python-version`, Node from `frontend/.nvmrc` (the dev container's Node feature has to be kept in step with it by hand), and Python packages from `backend/uv.lock`.

**Options considered**

- **Docker-in-Docker (chosen):** the container runs its own daemon, so the compose file and `localhost:5432` behave the same as in WSL. Images are pulled again inside the container, and the container runs privileged.
- **Docker-outside-of-Docker:** reuses Docker Desktop's daemon and image cache. Published ports land on the host rather than the container, so `localhost` from inside the container does not reach PostgreSQL without extra network setup.
- **PostgreSQL as a dev-container compose service:** always running. It duplicates the root `docker-compose.yml` (D-020) and the two can drift.

**Not yet covered:** PostgreSQL in CI, which is added with the API tests (E01-S03 and E01-S07), and Playwright in CI, added with E09-S01.

---

## Architecture and behaviour details

These were first written as proposed defaults on 2026-11-10 and were put to the owner on 2026-11-11. Each entry says whether it was confirmed as proposed or changed.

### D-024 Architecture: ports and adapters, SOLID

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision:** The backend has three layers, and dependencies point inward only.

- **Domain:** files, folders, names, alters, the pair rule. No framework imports.
- **Application:** one use case per user action (upload a file, restore from the bin), plus the **ports**: small interfaces for everything outside (file repository, folder repository, blob store, thumbnail generator, password hasher, token issuer, identity provider, clock).
- **Adapters:** FastAPI routers, SQLAlchemy repositories, the PostgreSQL blob store, the token issuer, the Google provider. A single composition root wires adapters into use cases.

**How this meets SOLID**

- **Single responsibility:** each use case has one reason to change; routers only translate HTTP; value objects own their own validation.
- **Open/closed:** a new storage backend or login provider is a new adapter, with no edit to any use case.
- **Liskov substitution:** any adapter can stand in for another behind the same port, including in-memory fakes in tests.
- **Interface segregation:** many small ports instead of one large "storage" interface.
- **Dependency inversion:** use cases depend on ports they define; concrete adapters are injected at the composition root.

**Options considered**

- **Ports and adapters (chosen):** the pair rule lives in one place, storage and host swap by configuration, and rule tests run without a database. More files and indirection: each feature touches three or four files.
- **Routers + services:** routers call service functions that use the database library directly. Fewer files, but rules mix with database code and dependency inversion is not met.
- **Routers straight to the database:** the least code, with the pair rule scattered across endpoints.

### D-025 Repository layout: `backend/` and `frontend/`

**Status:** Accepted on 2026-11-11 (changed from the proposal, which kept the Python project at the root with the frontend in `web/`)

**Decision:** The backend and the frontend each get their own top-level folder.

```
backend/
  pyproject.toml  uv.lock
  src/twin/
    domain/          entities, value objects, rules
    application/     use cases and ports
    adapters/
      api/           FastAPI routers and schemas
      persistence/   SQLAlchemy models, repositories, migrations
      blobs/         blob store adapters
      auth/          password hasher, token issuer, Google provider
    bootstrap.py     composition root
  tests/
frontend/            Vite + React + TypeScript app
docker-compose.yml
.github/  .devcontainer/
issues/  DECISIONS.md  FLOWS.md  CLAUDE.md
```

**Options considered**

- **`backend/` and `frontend/` (chosen):** symmetrical, with each side self-contained. The existing project files move, and CI, the dev container and the paths in CLAUDE.md are redone.
- **Python at the root, frontend in `web/`:** nothing moves, and it is what CI and the dev container were first built around.

**Consequences:** the move is story E01-S09 and comes before the other Foundation stories. Until it is done, D-041's workflow, the dev container and CLAUDE.md still describe the old layout (a root `pyproject.toml` and `web/`).

**Update 2026-11-12:** E01-S09 is done. The project files are in `backend/`, the package is `twin` (D-050), and CI, the dev container and CLAUDE.md use the new paths.

### D-026 Persistence stack

**Status:** Accepted on 2026-11-11 (as proposed, with the owner's condition that a later move to async stays easy)

**Decision:** SQLAlchemy 2 with the psycopg 3 driver, Alembic for migrations, and synchronous database calls.

**Keeping async open**

- psycopg 3 serves both synchronous and async code, so the driver does not change.
- Queries use SQLAlchemy's 2.0 `select()` style, which reads the same in a sync or an async session.
- No lazy loading, and no ORM objects leave the repositories: repositories return domain objects. Lazy loading is the main thing that breaks under async.
- All database access stays inside the persistence adapters.
- With those rules, going async means writing async versions of the adapters and adding `async`/`await` to the ports and use cases. That is a mechanical edit across those files, not a redesign.

**Options considered**

- **SQLAlchemy, synchronous (chosen):** easiest to read and debug, and enough at this scale. A lower ceiling on simultaneous requests.
- **SQLAlchemy, async with asyncpg:** a higher ceiling and a good fit for long uploads. Harder to debug, and async spreads through every use case and test.
- **SQLModel:** one class is both table and API schema. It ties the API shape to the table shape, which works against D-024.

### D-027 How pair uniqueness is enforced

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision:** Each file row stores the name and alter as typed, plus a comparison key for each (trimmed, Unicode-normalised, case-folded). A partial unique index on (vault, name key, alter key) covering only live files is the final guard. The domain builds the keys; the database guarantees the rule when two requests race. A pre-check gives a friendly message before the write.

**Why:** computing the keys in code makes D-005 behave identically whatever the database's own text-comparison settings are. Limiting the index to live files implements "the bin frees the pair" (D-008).

**Options considered**

- **Key columns + unique index (chosen).**
- **PostgreSQL's own case-insensitive text:** no extra columns, but the comparison rule would live in database configuration instead of code, Unicode look-alikes would not be normalised, and it is harder to test.
- **Check in code only:** simpler, but two simultaneous uploads could both pass the check.

### D-028 Blob storage: inside PostgreSQL

**Status:** Accepted on 2026-11-11 (changed from the proposal, which stored bytes on local disk)

**Decision:** File bytes are stored inside PostgreSQL, behind a `BlobStore` port. Thumbnails (D-034) are stored the same way.

- Bytes live in their own table, apart from the file rows, so listings and searches never load them.
- Files are read and written in pieces, so a large file is never held whole in memory. How the bytes are laid out (chunked rows or PostgreSQL large objects) is settled in E05-S01.
- The port stays, so the bytes can move to object storage later without touching use cases (E10-S02).

**Options considered**

- **Inside PostgreSQL (chosen):** one thing to run and one thing to back up, and a file's bytes and names can be saved together. The database grows with every file, large files strain it, and managed databases charge heavily for that size.
- **Local disk under generated IDs:** nothing extra to run, and cheap storage. A second place to back up, plus a second adapter and a one-off move at hosting.
- **S3-compatible from the start (MinIO locally):** hosting becomes a configuration change. Another container, more setup and slower tests.

**Consequences**

- The limits in D-036 matter more, because every byte counts toward database size.
- Free hosted databases with small size caps (the Render + Neon route in D-021) stop being realistic. The Droplet recommendation is unaffected.
- User-supplied text still never becomes a path on disk.

### D-029 Login tokens: JWT access and refresh

**Status:** Accepted on 2026-11-11 (changed from the proposal, which used server-side sessions)

**Decision**

- Login issues a short-lived **access token** (a JWT) and a longer-lived **refresh token**.
- The web app keeps the access token only in the page's memory and sends it in the `Authorization` header.
- The refresh token sits in an httpOnly, SameSite cookie that scripts cannot read. It is recorded in the database and replaced each time it is used, so logout and a password change can revoke it.
- On page load the web app silently exchanges the refresh cookie for a new access token.
- The refresh endpoint is protected against cross-site request forgery.
- A future mobile app sends both tokens in headers (E10-S05).
- Token lifetimes are set in E02-S03.

**Options considered**

- **JWT access + refresh (chosen):** works the same for web and a future mobile app, with no database lookup on ordinary requests. More moving parts, and an access token cannot be revoked before it expires, which is why it is short-lived.
- **Server-side session + cookie:** instantly revocable and simpler. One lookup per request, and the mobile app would need token login added.
- **Both tokens in browser storage:** simplest, but rejected because any injected script could steal both.

### D-030 Password hashing and the Google sign-in rule

**Status:** Accepted on 2026-11-11 (changed from the proposal, which linked accounts automatically)

**Decision**

- Google sign-in uses the OAuth authorization-code flow with PKCE, handled by the backend.
- **No automatic linking.** If someone signs in with Google and that email already belongs to a password account, the sign-in is refused, a message says an account with that email already exists, and they are sent to the login screen.
- The same holds the other way round: signing up with a password for an email that already has an account is refused with the same message.
- v1 has no setting to connect Google to a password account (D-042), so an email keeps the login method it signed up with.
- Passwords are hashed with Argon2id. This part was not put to the owner as a separate choice.

**Options considered**

- **Ask for the password first (chosen):** safest, with no reliance on a third party's verification. An extra step, and a message that may confuse people who forgot they signed up with a password.
- **Link automatically on a verified Google email:** seamless, but it relies on Google's verification and needs a subtle rule for accounts whose email was never verified.
- **Keep separate accounts:** simplest to build, but one person ends up with two vaults.

### D-031 Email: not in v1

**Status:** Accepted on 2026-11-11 (changed from the proposal, which wrote emails to the server log)

**Decision:** v1 sends no email at all. Everything that needs email waits for hosting (E10-S03).

**Consequences**

- **Password reset** is not in v1, and story E02-S05 moves to the backlog. A developer can reset a password from the command line (E02-S08), and a logged-in user can change theirs (D-042).
- **Email verification** at sign-up is not in v1 and is decided at hosting. Until then anyone can register an address they do not own, which is acceptable while the app only runs locally.
- No `EmailSender` port is built until it is needed.

**Options considered**

- **No email in v1 (chosen):** nothing to build or run now. No self-service recovery of a forgotten password.
- **Write the link to the server log:** the reset flow would exist, but only developers could complete it.
- **Local mail catcher (Mailpit):** exercises the real email path, at the price of another container.

### D-032 Name and alter validation rules

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision**

- **Names (files and folders):** 1 to 255 characters after trimming; no control characters; none of `\ / : * ? " < > |`; no trailing space or dot. These are the rules that let any file download cleanly on Windows, macOS and Linux.
- **Alters:** the same character rules, 1 to 100 characters, to keep the column readable.
- **Comparison key:** Unicode NFC normalisation, then case-folding.
- **Folders:** sibling names are compared with the same case-insensitive key as files (extends D-005 to folders).

The 100-character maximum for alters is still an open question in E03-S01.

**Options considered**

- **Windows-safe rules (chosen):** every file downloads cleanly on any system. Some names from macOS or Linux must be changed at upload.
- **Permissive:** anything except slashes and control characters, with unsafe characters swapped at download. A downloaded file's name could differ from its name in the app.

### D-033 Search and jump-by-pair behaviour

**Status:** Accepted on 2026-11-11 (search as proposed; jump changed to offer both ways of typing a pair)

**Decision**

- **Search:** case-insensitive "contains" match across file names, alters and folder names, over the whole vault, excluding the bin. Results show each item's location.
- **Jump-by-pair, two ways:**
  - a Go-to dialog with two fields, Name and Alter;
  - typing `name | alter` in the search box. The `|` can never appear in a name or an alter (D-032), so it is unambiguous.
- Either way, an exact (case-insensitive) match opens the containing folder and selects the file.

**Options considered**

- **Search:** contains (chosen); starts-with (fastest on very large vaults, but misses text in the middle); fuzzy (forgives typos, but gives surprising results and is more to build).
- **Jump:** both (chosen); the dialog only (nothing to learn); the separator only (fastest for keyboard users, but a syntax to learn).

### D-034 Thumbnails: made on first view

**Status:** Accepted on 2026-11-11 (changed from the proposal, which made them at upload)

**Decision:** A thumbnail is made on the backend the first time the grid view asks for it, for raster images (JPEG, PNG, GIF, WebP). It is then stored (D-028) and reused. Other file types show a type icon.

- Two simultaneous first views produce one thumbnail.
- An image that cannot be thumbnailed is remembered as such, so it is not retried on every view, and shows a type icon.
- Uploads are never slowed or failed by thumbnails.

**Options considered**

- **On first view (chosen):** no storage spent on images nobody looks at, and uploads stay fast. The first display of a folder of new images is slower, and there is more logic.
- **At upload:** the grid is fast from the first look. Storage for thumbnails nobody may view, and slightly slower uploads.
- **In the browser before upload:** no image library on the server, but inconsistent, it trusts the client, and a future mobile app would have to reimplement it.

### D-035 Recycle bin details

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision**

- Deleting a folder moves the folder and everything in it to the bin as one unit.
- Nothing is purged automatically in v1. Items stay until restored or permanently deleted.
- Bytes are removed from the blob store only on permanent delete, and bin contents count toward the quota until then.
- Restore returns an item to its original folder. If that folder no longer exists, the user picks a destination.

**Options considered for a missing original folder:** ask for a destination (chosen); recreate the original folders as Windows does (no extra step, but rebuilt folders can clash and deliberately removed ones reappear); restore to the top of the vault (simplest, but the user may not notice where it went).

### D-036 Upload size and vault quota

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision:** v1 enforces both a maximum file size and a per-vault quota. Both are settings. The numbers are fixed in E05-S09; 100 MB per file and 5 GB per vault are placeholders.

**Options considered**

- **File-size cap and vault quota (chosen):** protects the database, which also holds the file bytes (D-028), and is ready for hosting.
- **File-size cap only:** guards against one huge file, but a vault could still grow without bound.
- **No limits until hosting:** least work now, with both limits a retrofit before going public.

### D-037 API contract and frontend data layer

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision**

- REST with JSON under `/api`.
- FastAPI generates the OpenAPI schema, and the frontend's TypeScript types are generated from it, so the two cannot drift silently.
- Every error uses one shape with a machine-readable code (for example `pair_taken`).
- Uploads are multipart, one request per file, so one failure in a batch does not sink the rest.
- The frontend uses TanStack Query for server data and React Router for navigation.
- Requests carry the access token described in D-029.

**Options considered**

- **REST + generated TypeScript types (chosen):** a backend change that breaks the frontend fails the type check. A generate step runs after API changes.
- **REST + hand-written types:** no generate step, but the two sides can drift silently.
- **GraphQL:** the client asks for exactly the fields it wants, at the price of a second schema system and awkward file uploads.

### D-038 Tooling

**Status:** Accepted on 2026-11-11 (changed from the proposal: Pyright replaced by ty + mypy, Prettier replaced by Biome, and CI added in D-041)

**Decision**

- **Python:** uv, Ruff for linting and formatting, **ty and mypy (strict)** for type checking, pytest. Both type checkers run, because ty is fast but still pre-1.0 (0.0.x), while mypy is mature and catches what ty does not yet check. Config lives in `pyproject.toml`.
- **Frontend:** Node 26 LTS, pinned in `.nvmrc` and installed through nvm (WSL currently has Node 18, which is too old), npm, Vitest, Playwright, and:
  - **Biome** for formatting and the general lint rules, including Tailwind class sorting (`useSortedClasses`).
  - **ESLint**, limited to the rules Biome lacks: typescript-eslint's type-aware rules (for example `no-floating-promises`, which matters with fetch and TanStack Query) and the official `react-hooks` plugin. Rules that overlap with Biome stay off in ESLint.
  - **TypeScript 7** (`tsc --noEmit`) for type checking.
- Prettier is not used, because a second formatter would fight Biome.

**Options considered (frontend)**

- **ESLint + Prettier:** the most rules and the default in the Vite and shadcn templates. Two tools, more config, slower.
- **Biome alone:** one fast tool, similar to Ruff. Fewer React and type-aware rules.
- **Oxlint + Prettier:** fast, and ports most ESLint rules. Its type-aware mode and plugin coverage are younger.
- **Biome + a slim ESLint (chosen):** Biome's speed and single formatter, plus the type-aware and hooks rules only ESLint has. Two linters to configure.

### D-039 Copy, move and download semantics

**Status:** Accepted on 2026-11-11 (as proposed)

**Decision**

- **Copy a file:** the user must type a new alter and may change the name. Copying several files uses the bulk table (D-012).
- **Copy a folder:** not in v1, because every file inside would need a new alter (E10-S07).
- **Move a file:** never conflicts (D-002).
- **Move a folder:** can clash with a same-named sibling, which prompts for a new folder name. A folder cannot be moved into itself or its own descendants.
- **Download one file:** saved under its name.
- **Download several:** one zip. Entries that would share a name inside the zip get ` [alter]` added before the extension.

**Options considered**

- **Folder copy:** left out of v1 (chosen); or included using the bulk alter table, which is sizeable extra work and means long tables for large folders.
- **Alter in download names:** only on clashes in a zip (chosen); always (the alter survives outside the app, but downloaded names differ from the names in the app); never (clashes numbered (1), (2), so you cannot tell the files apart).

### D-040 Desktop and mobile wrappers

**Status:** Deferred until v1 is hosted

**Current recommendation:** Tauri 2, which covers desktop and mobile with one tool and produces small installers; its mobile side is the younger part. The alternative is Electron for desktop (mature, large installers) with Capacitor for mobile. Re-evaluate both when step 3 of D-014 starts.

---

## Planning wrap-up (2026-11-11)

Gaps that no earlier decision covered, put to the owner on 2026-11-11.

### D-042 Account settings in v1: change password only

**Status:** Accepted on 2026-11-11

**Decision:** v1 has one account setting: change password, by entering the current password and a new one.

**Offered and not chosen for v1** (kept in the backlog as E10-S08): connect or disconnect Google; delete the account and its files; change email.

**Consequences**

- With D-030, a password account cannot add Google sign-in in v1.
- With D-031, changing the password while logged in is the only self-service route. A forgotten password needs the developer command (E02-S08).

### D-043 Screens: fully responsive, phones included

**Status:** Accepted on 2026-11-11

**Decision:** Every screen of the v1 web app works from phone width up to desktop.

**Rules that follow**

- Each UI story delivers and tests both a desktop and a phone layout.
- Anything that needs a mouse or keyboard has a touch route: a long-press opens the right-click menu, moves are also available as "Move to", uploads also start from the file picker, and keyboard shortcuts are a desktop extra.
- How each screen rearranges on a phone is decided in its own story (D-046).

**Options considered**

- **Fully responsive (chosen):** removes the layout rework from the later mobile-app step. Noticeably more UI work in every story.
- **Desktop-sized only:** the fastest v1, but unusable in a phone browser.
- **Down to tablets:** modest extra work, with phones still left for later.

**Consequences:** the estimate for step 4 in D-014 drops from 3-6 weeks to 1-3 weeks. Both figures are rough.

### D-044 Supported browsers

**Status:** Accepted on 2026-11-11

**Decision:** The current versions of Chrome, Edge, Firefox and Safari.

**Options considered:** the four main browsers (chosen); Chrome and Edge only (one engine to test, but Firefox and Safari users may hit bugs, and Safari matters for the later iOS app).

**Consequences:** browser tests run on Playwright's three engines (Chromium, Firefox, WebKit). Real Safari needs a Mac or an iPhone; where none is available, Playwright's WebKit stands in for it.

### D-045 Interface language: English only

**Status:** Accepted on 2026-11-11

**Decision:** The interface is in English, with text written directly into the screens.

**Options considered:** English only (chosen); English with every text routed through a translation file (cheap to add languages later, a little friction on every screen); several languages in v1.

**Consequences:** adding a language later means touching every screen.

### D-046 Visual design happens in code, story by story

**Status:** Accepted on 2026-11-11

**Decision:** There is no up-front mock-up or Figma design. Each UI story settles its own look, within the theme (D-013) and the shared components (D-017).

**Options considered**

- **Design in code as we go (chosen):** no up-front step. Screens can drift apart and need rework, and that risk is higher with two layouts per screen (D-043).
- **A static mock-up of the main screens first:** one extra story, with the look agreed before the UI stories start.
- **Figma designs from the team:** full control, at the price of design time and the UI stories waiting on it.

**What limits the risk:** E01-S05 fixes the typeface, icon set, spacing and breakpoints once, and every screen is built from the same shared components.

### D-047 Product name: tWIN!!

**Status:** Accepted on 2026-11-11

**Decision:** The product is called **tWIN!!**, written exactly as the owner typed it.

**Options considered:** Namesake, Twofold, Doppel, or deciding later.

**Consequences:** the name appears in the app header, the page title and the README. The Python package and console script were renamed to `twin` in E01-S09 (D-050); the repository keeps its name.

### D-048 Stories are not sized

**Status:** Accepted on 2026-11-11

**Decision:** Stories carry no sizes, estimates or dates. They are worked through in order.

**Options considered:** S / M / L without dates; day estimates with milestone dates; no sizing (chosen).

**Consequences:** there is no early warning when an epic turns out bigger than expected. The rough efforts in D-014 are the only estimates in the project.

### D-049 Definition of done

**Status:** Accepted on 2026-11-11

**Decision:** A story is Done when all of these hold.

1. All CI checks pass (D-041).
2. Every acceptance criterion has an automated test, or a written reason why it cannot have one.
3. For frontend work, the feature has been exercised in a real browser through Claude in Chrome, wherever that is possible and necessary.

**Offered and not chosen as conditions of Done:** keeping `DECISIONS.md` and `FLOWS.md` in step (still expected under D-023, but not a gate), and the owner trying the feature personally.

**How condition 3 sits beside D-022:** the Playwright tests stay as the repeatable browser tests that CI runs. The Claude in Chrome pass is hands-on verification while the story is being implemented.

### D-050 Python package and script name: twin

**Status:** Accepted on 2026-11-12. The owner chose to rename the package and console script to match tWIN!! (D-047) and to keep the repository name, and confirmed the spelling `twin`.

**Decision:** The importable package becomes `twin`, the distribution becomes `twin`, and the console script becomes `twin` (`uv run twin`). Environment variables use the prefix `TWIN_`. The repository keeps its name.

**Options considered**

- **Keep `multiid_folder_mgmt` (offered and not chosen):** no churn, but the code never matches the product.
- **Rename package and script, keep the repository (chosen as the direction):** code reads like the product, and nothing exists yet that would break. The package name has to be a valid identifier, so `tWIN!!` is shortened to `twin`.
- **Rename everything, including the repository:** fully consistent, and also free today, but touches the folder name and every path in CLAUDE.md.

**Consequences:** done in E01-S09, before any feature code. Other spellings (`twin_app`, `twinfs`) change only that story and the `TWIN_` prefix in E01-S02.

### D-051 Where the version pins live

**Status:** Accepted on 2026-11-12

**Decision:** `.python-version` lives in `backend/` and `.nvmrc` in `frontend/`, each beside the project that uses it. CI and the dev container read the new paths. The Node version in the dev container's feature still has to be kept in step with `frontend/.nvmrc` by hand (D-041).

**Options considered:** each pin with its side (chosen); both at the root (one place to look, but the pins no longer sit with their projects).

### D-052 How the theme colours are applied

**Status:** Accepted on 2026-11-12, from the owner's reference design (a ChatGPT-made mock-up the owner described in words)

**Decision:** Oxblood is the background of the whole app. Dusty rose is used for text, the navbar and hover highlights. Electric cyan is used for everything else: buttons, links, icons, focus rings, selection and active states. This keeps D-013's rule that cyan is only used on oxblood; a rose hover highlight flips its text and icons to oxblood.

**Options considered:** rose content areas with oxblood chrome (the recommendation offered); oxblood throughout with free use of cyan; rose throughout with oxblood text. The owner's design is closest to the second, with rose reserved for text, the navbar and hover.

**Consequences:** long lists are read as rose text on oxblood, so every text pairing is checked for AA contrast in E01-S05. "Navbar is rose" is read as a rose bar with oxblood content; to be checked against the reference image.

### D-053 Typeface, icon set, theme variant and API client libraries

**Status:** Proposed (2026-11-12). Defaults put forward so E01-S05 and E01-S06 are complete; the owner has not answered these questions.

**Decision**

- **Typeface:** Inter, variable, self-hosted through `@fontsource-variable/inter`.
- **Icons:** `lucide-react`, which is what shadcn/ui uses.
- **Theme variant:** one theme only (the D-052 look); no light or dark switch in v1.
- **API client:** `openapi-typescript` generates the types and `openapi-fetch` makes the calls, with the generated files committed and checked in CI.

**Options considered**

- Typeface: Inter (chosen, neutral and very legible at small sizes in a dense list); a system font stack (no download, less distinctive); a display face for the brand with Inter for the body (more character, a second font to load).
- Icons: lucide (chosen); Phosphor (more weights and a friendlier look, a second set beside shadcn's own); Tabler (large set, not shadcn's default).
- Variant: single theme (chosen, because the identity is the oxblood look); a light variant (an accessibility option, but it doubles every contrast check and the cyan rule has no good light-mode home).
- API client: `openapi-typescript` + `openapi-fetch` (chosen, small and types come straight from the schema); a hand-written `fetch` wrapper over the generated types (fewer dependencies, more code); an all-in-one generator such as Orval or hey-api (generates hooks too, heavier and more to learn).

**Consequences:** used by E01-S05 and E01-S06, which stay Draft until these are confirmed or changed.

*Update 2026-11-12:* E01-S05 was built on the typeface, icon set and single theme as proposed, and E01-S06 on the API client libraries, under the owner's instruction to proceed without questions. This entry stays Proposed until the owner confirms or changes it.

### D-054 TypeScript pinned to 5.9 for typescript-eslint and openapi-typescript

**Status:** Accepted on 2026-11-12 (decided while building E01-S04, under the owner's instruction to proceed without questions)

**Decision:** `frontend/` uses TypeScript `~5.9`. Vite's template ships TypeScript 7, but typescript-eslint 8 declares support for `>=4.8.4 <6.1.0` (D-038 needs its type-aware rules, `no-floating-promises` and `no-misused-promises`) and openapi-typescript 7 (D-053, E01-S06) declares `^5`. Only 5.x satisfies both.

**Options considered**

- **TypeScript 5.9 (chosen):** every peer dependency resolves cleanly, with no flags. 6.0 satisfied typescript-eslint but not openapi-typescript.
- **TypeScript 7 with `--legacy-peer-deps`:** newer and faster, but the type-aware lint rules run on an unsupported compiler.
- **Drop the type-aware rules:** removes the reason for ESLint in D-038.

**Consequences:** move to a newer TypeScript once both typescript-eslint and openapi-typescript support it; the change is one line in `frontend/package.json`.

### D-055 Vaults separate from users; one root folder per vault

**Status:** Proposed (E02-S01)

**Decision:** `vaults` is its own table, one per user for now (unique owner), and every vault has exactly one root folder row in `folders`. E04-S01 extends `folders`.

**Options considered:** vault columns on `users` (simpler, blocks shared vaults later); separate table (chosen, small cost now).

### D-056 Password rules

**Status:** Proposed from the owner's choice during E02 planning

**Decision:** minimum 10 and maximum 128 characters, no composition rules, Argon2id hashing with library defaults.

### D-057 Token lifetimes

**Status:** Proposed from the owner's choice during E02 planning

**Decision:** access token 15 minutes, refresh token 30 days rotated on every use with reuse detection, no remember-me.

### D-058 Google sign-in is optional configuration

**Status:** Proposed

**Decision:** Google sign-in is enabled only when `TWIN_GOOGLE_CLIENT_ID`, `TWIN_GOOGLE_CLIENT_SECRET` and `TWIN_GOOGLE_REDIRECT_URI` are set; the owner supplies the OAuth client. Email and password never depends on it. Automated tests use a fake provider.
### D-059 E02-S01 build choices: root folder name, credential rule, unit of work

**Status:** Proposed (decided while building E02-S01 under the instruction to proceed without questions; D-055 to D-058 are on the plan branch)

**Decision:**
- Each vault root folder is named `Home`. It is the only folder with no parent, and a partial unique index allows one per vault.
- A user must have a password hash or a Google subject (at least one), so a later account can hold both. `users.email` is stored as typed (trimmed) and made unique on `lower(email)`.
- `CreateUser` runs through a `UnitOfWork` port, so user, vault and root folder are stored in one transaction. `get_current_vault` resolves the caller through a `UserAuthenticator` port; until E02-S03 the adapter authenticates nobody, so vault routes answer 401 `unauthorized`.
- A token for a user with no vault is also 401, not 404, so an id cannot be probed.

**Options considered**

- Root name: `Home` (chosen, reads well in a breadcrumb); an empty name (needs special cases in every path display); `/`.
- Credentials: at least one required (chosen); exactly one (blocks linking Google to a password account later).
- Transaction: a `UnitOfWork` port (chosen, keeps the rule testable with fakes); each repository committing on its own (a failure could leave a user without a vault).

**Consequences:** E04-S01 extends `folders`; E02-S03 replaces the null authenticator.

### D-060 E02-S02 build choices: signup validation, hasher and logging

**Status:** Proposed (decided while building E02-S02 under the instruction to proceed without questions)

**Decision:**
- Password length counts characters (Unicode code points), 10 to 128, no composition rules and no trimming (D-056). Both too short and too long answer 422 `weak_password` with `details.min_length` and `details.max_length`.
- A bad email address answers 422 `validation_error` with `details.fields`, because the request model runs the `Email` rule; the `email_taken` check stays in `CreateUser`.
- The request model holds the password as a `SecretStr`, `Password` hides its text from `repr`, and the validation error handler never echoes the submitted input, so the password cannot reach logs, errors or OpenAPI.
- The Argon2id adapter uses the argon2-cffi defaults; `argon2-cffi` was vetted (old and widely used, last release over 500 days ago, flagged stale) and is allowed by the owner.

**Options considered**

- Length: characters (chosen, what a person counts); bytes (a 10-character password in some scripts would be refused).
- Email error: `validation_error` (chosen, as the story specifies); the domain `invalid_email` code (still raised by use cases called outside HTTP).

**Consequences:** E02-S03 reuses `PasswordHasher.verify` and `needs_rehash` for login.

### D-061 E02-S03 build choices: tokens, rotation, CSRF and rate limit

**Status:** Proposed (decided while building E02-S03 under the instruction to proceed without questions; D-057 holds the token lifetimes)

**Decision:**
- Access token: JWT HS256 with `sub`, `vid`, `iat`, `exp`, signed with `TWIN_JWT_SECRET` (32+ characters; the API refuses to start without it). Expiry is judged against the app clock, only `HS256` is accepted, and `sub`, `exp` and `iat` are required. The vault is still looked up per request, so `vid` is informational.
- Refresh token: 256-bit random string, stored only as its SHA-256 hash, in a family. Each use inserts a new token in the same family and marks the old one replaced. Presenting a replaced or revoked token revokes the whole family and answers 401 `invalid_refresh_token`; an expired or unknown one answers the same 401 without revoking. Rows are locked (`FOR UPDATE`) so two concurrent refreshes cannot both succeed.
- Logout revokes the whole family of the presented token and always answers 204 (an unknown or missing cookie is ignored). It requires the same CSRF header as refresh, so another site cannot log a person out.
- CSRF: header `X-Requested-With: twin` is required, and an `Origin` header, when present, must have the same host name as the `Host` header. The cookie is `SameSite=Lax`, `Path=/api/auth`, `Secure` when `TWIN_COOKIE_SECURE`.
- Login: unknown email, wrong password, a malformed email and an account with no password all answer 401 `invalid_credentials`; an unknown email still runs one hash verify. The password is capped at 1024 characters on this route.
- Rate limit: 5 failed logins per email and client address per 15 minutes, sliding window, 429 `rate_limited` with `Retry-After`. It is blocked even for the right password, and a successful login resets the count. Held in process memory behind the `LoginLimiter` port.
- Signup also signs the person in (same response and cookie as login). The response `user` is `{id, email, has_password}`.
- `twin export-openapi` uses a placeholder secret so CI can regenerate the schema.

**Options considered**

- Logout scope: whole family (chosen, one login session ends); only the presented token (same result with rotation, but leaves siblings if a replay raced).
- Logout CSRF: required (chosen, costs nothing); exempt as the story only names refresh.
- Limiter store: in memory (chosen, the story allows it for one process); PostgreSQL table (survives restarts, more code now).
- Client address: the direct peer address. Behind a reverse proxy every person would share the proxy address, so deployment must pass the real address through (for example uvicorn `--proxy-headers` with a trusted proxy list) before this limit means anything.

**Consequences:** E02-S06 sends the CSRF header on refresh and logout and keeps the access token in memory. Expired and revoked token rows are never deleted yet (see the follow-ups in the PR). A password change (E02-S07) should revoke the person's families.

### D-062 E02-S04 build choices: Google flow, state cookie, ID token checks and failures

**Status:** Proposed (decided while building E02-S04 under the instruction to proceed without questions; D-058 holds the "off until the owner supplies a client" rule)

**Decision:**
- Authorization code with PKCE (S256) run by the backend with `httpx` (now a runtime dependency; vetted). Scope is `openid email`; `prompt=select_account` so a shared browser asks which Google account.
- `state` and the PKCE verifier live in a signed httpOnly cookie `oauth_state` (HS256 JWT, key derived from `TWIN_JWT_SECRET`, own audience so it can never pass as an access token, 10 minutes, `Path=/api/auth/google`, `SameSite=Lax` because the callback is a top-level navigation from Google, `Secure` per `TWIN_COOKIE_SECURE`). The cookie is deleted by every callback answer, so a state cannot be replayed.
- The ID token is verified against Google's signing keys (RS256, JWKS from `https://www.googleapis.com/oauth2/v3/certs`, fetched with `httpx`, kept in memory and refetched when a token names an unknown `kid`; needs the `pyjwt[crypto]` extra, i.e. `cryptography`, vetted); then issuer (either Google form), audience, expiry against the app clock, `email_verified` being `true`, and a non-empty subject and email are all required.
- The account is found by `google_subject` first (so a changed Google email still lands in the same vault), then the email decides: an email that already has any account is refused (D-030), otherwise a user with no password hash and a vault are created. A lost race on the email also counts as "account exists".
- Every callback failure is a 302 to the login page, not a JSON error: `?error=account_exists`, or `?error=google_failed` for bad or missing state, declined consent, a refused code or a failed ID token check. The UI (E02-S06) maps these two codes to messages. Success is a 302 to `/` with the refresh cookie set; the UI then calls `/api/auth/refresh` for an access token.
- Google is enabled only when the client id, the secret and the redirect URI are all non-empty; otherwise `identity_provider` is `None`, `/api/auth/providers` says `{"google": false}` and the two Google routes answer 404 `not_found`.
- Nothing about Google is reachable from tests: they swap in `FakeIdentityProvider`, and `GoogleIdentityProvider` is tested against `httpx.MockTransport`.

**Options considered**

- ID token signature: verify against Google's JWKS (chosen, the story requires it; adds `cryptography`); claims only (allowed by OIDC for a direct token-endpoint response, simpler).
- State storage: signed cookie (chosen, no table); server-side table (revocable, needs a migration and cleanup); `itsdangerous` (new dependency for what PyJWT already does).
- Failure form: redirect to login (chosen, the person is mid-navigation); JSON error (unreadable in a browser tab).

**Consequences:** E02-S06 reads `?error=` on `/login`, shows the Google button when `/api/auth/providers` says so, and calls `/api/auth/refresh` after the redirect to `/`. Real Google has not been exercised; the owner must create the client (`docs/google-oauth-setup.md`) and try one sign-in by hand.

### D-063 E02-S07 build choices: change-password order of checks, kept session, shared limiter, Swagger bearer

**Status:** Proposed (decided while building E02-S07 under the instruction to proceed without questions; D-029, D-042 and D-056 hold the rules it applies)

**Decision:**
- `POST /api/auth/change-password` (bearer) answers 204. Order of checks: rate limit, then the account has a password (`409 no_password`), then the current password (`401 wrong_password`), then the new one against the 10 to 128 rule (`422 weak_password`). The current password is verified before the new one is checked, so a wrong current password never reveals anything about the new one.
- The hash change and the revocation of every other login session happen in one unit of work. The session that stays logged in is the one whose refresh cookie accompanies the request (`ChangePassword.family_of` finds its family, and only if the token belongs to the caller and is not spent). Without a valid cookie, every session of the person ends, including the caller's; the access token in hand keeps working until it expires (15 minutes).
- Wrong current passwords count against the same in-memory limiter as logins, keyed `change-password|<user id>` (5 failures in 15 minutes, then `429 rate_limited` with `Retry-After`). A correct password clears the count. The key is the account, not the address, because the caller is already authenticated.
- The password fields are `SecretStr`, capped at 1024 characters in the request model only to bound the work a body can cause; the 10 to 128 rule is the domain's, so 129 characters answers `weak_password`, not `validation_error`.
- The bearer scheme (`HTTPBearer(auto_error=False)`) is now declared on the authenticated routes so Swagger UI shows an Authorize button; it never rejects a request itself. Swagger UI hides `Authorization` header parameters, so without a declared scheme the docs page could not call any bearer route.
- The access tokens already issued to other devices stay valid until they expire (at most 15 minutes); only refresh is cut off, as the story says.

**Options considered**

- Keep-session signal: the refresh cookie (chosen, no new field for clients, matches how logout finds its session); a session id inside the access token (needs a token change in S03).
- Limiter key: user id (chosen); user id plus address (a thief with a stolen access token could rotate addresses).
- Without a cookie: end every session (chosen, the conservative reading); refuse the request (blocks API clients that keep the refresh token elsewhere).

**Consequences:** E02-S06's account screen sends the request with the bearer token from memory and the browser sends the refresh cookie on its own (cookie path `/api/auth` matches). Immediate cut-off of other devices' access tokens would need a token version or a revocation list; not done.

### D-064 E02-S08 build choices: set-password reads, errors and help

**Status:** Proposed (decided while building E02-S08 under the instruction to proceed without questions; D-031 and D-056 hold the rules it applies)

**Decision:**
- `twin set-password <email>` takes exactly one argument; any other count prints `Usage: twin set-password <email>` and exits 1.
- The password comes from a no-echo prompt asked twice when stdin is a terminal, otherwise from the first line of stdin (trailing newline removed, nothing else trimmed). Empty stdin is refused with `No password given on standard input.`
- Checks run in this order: the email is well formed (`Enter a valid email address.` otherwise, as in sign-up), the account exists, the account has a password, the new password satisfies 10 to 128 characters. The use case is `ResetPassword` in `application/reset_password.py`; `adapters/cli.py` turns a `DomainError` into one line on standard error and exit code 1.
- The email is matched ignoring case, and the success line prints the email as stored.
- Every refresh-token family of the account is revoked, none kept (unlike change-password there is no current session). Access tokens already issued live on for up to 15 minutes, as in D-063.
- No rate limit: the command needs shell access to the database, which already means full control.
- `create_reset_password` in `bootstrap.py` wires the use case and needs no `TWIN_JWT_SECRET`, so a password can be reset without configuring the API.
- `twin --help` / `-h` prints the usage of the server, `export-openapi` and `set-password` (before, any argument other than `export-openapi` was an error).

**Options considered**

- Password source: prompt or stdin (chosen, keeps it out of shell history and `ps`); a `--password` flag (leaks into both); an environment variable (leaks into child processes).
- Revoke every family (chosen, the story says every device logs in again); keep one (there is no current session to keep).

**Consequences:** E10-S03 (email reset) can reuse `ResetPassword` behind a token check.

### D-065 E02-S06 build choices: auth state, routes, messages and dev proxy

**Status:** Proposed (decided while building E02-S06 under the instruction to proceed without questions; D-029, D-030, D-042 and D-043 hold the rules it applies)

**Decision:**
- The access token lives in a module variable of the E01-S06 client (D-029), never in web storage. `AuthProvider` asks `POST /api/auth/refresh` once on load; `refreshSession()` shares one in-flight request, because refresh tokens rotate and React StrictMode mounts twice in development.
- Refresh and logout use plain `fetch` (with `X-Requested-With: twin`), not the client, so a 401 from them cannot start another refresh. Login and sign-up go through the client, so a wrong password also makes one harmless refresh attempt that fails.
- Logout clears local state even if the API call fails.
- Routes: `/signup` and `/login` (signed-in visitors go to `/`), `/` and `/account` (signed-out visitors go to `/login`). The E01 health page moved to `/health`; the smoke test follows it.
- Error text comes from one code-to-message table in `errors.ts`. `rate_limited` adds the wait from `details.retry_after` (the client copies the `Retry-After` header into it when the body has none). Sign-up field errors from `details.fields` use fixed texts ("Enter a valid email address.") rather than the pydantic wording of the server.
- Screens use `noValidate`: the server is the one validator, and its answers fill the same message slots as everything else.
- Change password asks for the new password twice; a mismatch is caught in the browser without a request.
- The Vite dev proxy uses the object form `{ target }`, because the string form rewrites `Host`, and the API CSRF check compares `Origin` with `Host` on refresh and logout.
- The signed-out refresh on every load shows a 401 line in the browser console; the smoke test ignores exactly that message.

**Options considered**

- Token storage: memory (chosen, D-029); `sessionStorage` (survives reload but readable by any script).
- Refresh on load: always (chosen, the HttpOnly cookie cannot be read to know if a session exists); a non-HttpOnly "logged in" hint cookie (extra state to keep in step).
- Moving the health page to `/health` (chosen, `/` is now the vault); keeping it on `/` for signed-out visitors (mixes two purposes).

**Consequences:** E08-S01 replaces `AppShell` and `Home` and keeps the guards. Deployment behind a proxy must keep the browser `Host` (or the same origin) for refresh and logout to pass the CSRF check.
