# E01-S04 Frontend skeleton

- **Epic:** E01 Foundation
- **Status:** Done (browser check pending)
- **Depends on:** E01-S01, E01-S09
- **Decisions:** D-016, D-017, D-025, D-037, D-038, D-044, D-047
- **Flows:** None

## Goal

The web app builds, passes the checks CI already runs, and talks to the API.

## Scope

1. `frontend/` created from Vite's React + TypeScript template, with npm and Node 26 from `frontend/.nvmrc`. The page title in `index.html` is **tWIN!!** (D-047).
2. Tailwind (current major, Vite plugin) and shadcn/ui initialised: `components.json`, the `cn` helper, and the path alias `@/` for `src/`. No components are added beyond what the init creates. Colours stay at their defaults until E01-S05.
3. `vite.config.ts`: dev server on 5173, with `/api` proxied to `http://127.0.0.1:8000`, so development needs no CORS setup.
4. React Router with a single route `/` and a layout component holding an outlet. TanStack Query arrives in E01-S06.
5. Placeholder page: calls `GET /api/health` with plain `fetch` in an effect and shows "API: ok, database: up" or an error line. E01-S06 replaces the fetch with the typed client.
6. Tooling per D-038:
   - `biome.json`: formatter, linter, `useSortedClasses`, import organising.
   - `eslint.config.js`: typescript-eslint's type-aware rules (`no-floating-promises`, `no-misused-promises`) and `react-hooks` only, with every rule Biome covers switched off.
   - `tsconfig`: strict, with `noUncheckedIndexedAccess` on.
7. The npm scripts the CI web job calls: `dev`, `build` (`tsc --noEmit && vite build`), `typecheck`, `lint` (`biome check` then `eslint .`), `format`, `test`.
8. `test` runs `vitest run` with jsdom and Testing Library, plus one test that renders the placeholder page with a mocked `fetch`. The web job needs a passing `npm test` from day one; E01-S07 builds the conventions on top.
9. `npm run build` writes static files only to `frontend/dist/` (no server code, D-016).

## Acceptance criteria

1. With the API and database running, `npm run dev` shows a page displaying the API health result. (Exercised in a real browser through Claude in Chrome, D-049; the Vitest test covers the rendering logic with a mocked response.)
2. The page shows a readable error when the API is down. (Vitest.)
3. `npm run build` produces `dist/` containing only static assets. (A script check that every file is html, js, css, svg, ico, png, woff2 or json.)
4. `npx biome ci`, `npx eslint .`, `npm run typecheck`, `npm test` and `npm run build` all pass, and CI's web job now runs instead of skipping. (CI.)
5. The page is usable at 375 px and 1280 px wide. (Claude in Chrome check at both sizes; the page is trivial, but the habit starts here, D-043.)

## Tests

- `src/pages/Health.test.tsx`: API ok, database down, network error.

## Out of scope

Colours and fonts (E01-S05), the typed client and error handling (E01-S06), Playwright (E01-S07), any real screen.

## Open questions

None.

## Notes

- Vite's current template ships TypeScript 7, which typescript-eslint does not support yet, so TypeScript is pinned to `~6.0` (D-054).
- Biome 2.6's Tailwind class-sorting rule is `nursery/useTailwindSortedClasses` (the story called it `useSortedClasses`). Biome's own ignore-file lookup does not work from `frontend/` (the `.gitignore` is at the repo root), so `biome.json` lists `!dist` and `!node_modules` itself.
- shadcn/ui is configured by hand (`components.json`, `cn` helper, `@/` alias, Tailwind variables at their defaults) rather than through the interactive CLI; no components were added.
- The template's demo assets were removed and `public/favicon.svg` replaced with a titled SVG (Biome's accessibility rule rejects an untitled one).
- Criterion 2 and 4 (local): `npx biome ci`, `npx eslint .`, `npm run typecheck`, `npm test` (4 Vitest tests: ok, database down, network error, API error status) and `npm run build` all pass. CI's web job now runs instead of skipping.
- Criterion 3: `npm run build` ends with `scripts/check-dist.mjs`, which fails on any file outside html, js, css, svg, ico, png, woff2 or json.
- Criterion 1: with the API and database up, `curl localhost:5173/api/health` through the Vite proxy returned `{"status":"ok","database":"up"}` and the page title is tWIN!!. The in-browser check through Claude in Chrome (and the 375 px and 1280 px sizes, criterion 5) was **not done**: the browser tab could not load the WSL dev server. Still to be done by hand.
