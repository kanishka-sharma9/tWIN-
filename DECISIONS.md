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
