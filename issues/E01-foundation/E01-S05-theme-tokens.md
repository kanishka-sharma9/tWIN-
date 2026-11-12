# E01-S05 Theme tokens

- **Epic:** E01 Foundation
- **Status:** Draft (spec complete; waits for D-053 to be confirmed and for the navbar check below)
- **Depends on:** E01-S04
- **Decisions:** D-013, D-043, D-046, D-052, D-053 (Proposed)
- **Flows:** None

## Goal

The three-colour identity is defined once and used everywhere, and every later screen inherits its fonts, icons, spacing and breakpoints from here.

## How the colours are applied (D-052, from the owner's reference design)

| Role | Colour |
|---|---|
| Page and panel backgrounds | Oxblood `#4A0E1B` |
| Text, the navbar and hover highlights | Dusty rose `#E3B5AE` |
| Everything else: buttons, links, icons, focus rings, selection, active states, progress | Electric cyan `#00E5FF` |

Consequences, all consistent with D-013's rule that cyan appears only on oxblood:

- Cyan never sits on rose. A rose hover highlight flips the text and icons on it to oxblood.
- A rose navbar carries oxblood text and icons; its active item is marked by an oxblood underline or fill, not cyan.
- Oxblood on rose and rose on oxblood both contrast at about 8.4:1; cyan on oxblood at about 10:1.

**To confirm against the reference image:** "navbar is rose" is read here as a rose-filled bar with oxblood content. If the design shows an oxblood bar with rose text, only the navbar tokens and the rule above change.

## Scope

1. `frontend/src/styles/tokens.css`, the only file allowed to contain colour values. Base tokens: `--oxblood`, `--rose`, `--cyan`. Derived tints, each given a name and a purpose:
   - `--oxblood-raised`: a slightly lighter oxblood for cards and dialogs on the oxblood page.
   - `--oxblood-sunken`: a slightly darker one for input wells.
   - `--rose-muted`: rose at reduced strength for secondary text, which must still pass AA.
   - `--rose-line`: rose at low opacity for borders and dividers (decoration, not text).
   - `--cyan-dim`: pressed or disabled cyan.
2. Semantic tokens that components use, never the base colours directly: `--background`, `--foreground`, `--surface`, `--navbar`, `--navbar-foreground`, `--hover`, `--hover-foreground`, `--primary`, `--primary-foreground`, `--ring`, `--selection`, `--border`, `--muted-foreground`, `--destructive` (needs a status colour that works on oxblood; chosen in the story and added to the contrast list).
3. Map the semantic tokens onto shadcn/ui's variables in `src/index.css`, so every shadcn component picks them up, and onto Tailwind's theme so classes like `bg-background` and `text-foreground` work.
4. A single theme (D-053). No light variant and no theme switch in v1.
5. Focus and selection styles: a 2 px cyan focus ring offset from the element (visible on oxblood); selected rows use `--selection` with a cyan edge; text selection is cyan on oxblood. Focus must stay visible in a rose navbar, so the ring there uses oxblood.
6. Typeface: Inter variable, self-hosted through `@fontsource-variable/inter` (no external font requests), with a system-font fallback. A monospace stack for IDs and sizes. Icons: `lucide-react`, sized 16, 20 or 24 px only.
7. Spacing: Tailwind's 4 px scale, with 8 px as the layout rhythm. Radius: one token pair, `--radius` and `--radius-sm`.
8. Breakpoints, fixed once: **phone** below 640 px, **tablet** from 640 px (`sm`) and 768 px (`md`), **desktop** from 1024 px (`lg`), wide from 1280 px (`xl`). Minimum supported width 360 px (D-043). Touch targets at least 44 px on phone widths.
9. Written usage rules in `frontend/docs/theme.md`: the table above, the cyan-never-on-rose rule, which semantic token to use for what, and "no colour values outside `tokens.css`".
10. A dev-only route `/dev/tokens` that shows every semantic token, each text-on-background pairing, a focus ring, a hover row and the navbar. It is excluded from the production build.

## Acceptance criteria

1. Changing one base token recolours the whole app. (Vitest: render the showcase, change `--cyan` on the root, and assert computed styles of primary elements follow. Confirmed visually through Claude in Chrome.)
2. Every text-on-background pairing in use meets WCAG AA: 4.5:1 for body text, 3:1 for large text and UI icons. (Vitest reads `tokens.css`, computes contrast for a declared list of pairings and fails below the threshold. A new pairing is added to the list in the same change.)
3. No colour values exist outside the token file. (A test greps `src/` for hex, `rgb(`, `hsl(` and `oklch(` outside `tokens.css`, and for Tailwind's built-in colour classes such as `bg-red-500`.)
4. Cyan is never used as a background for text or on rose. (Part of the pairing list: no pairing has cyan text on a rose surface, and a test asserts it.)
5. Focus ring is visible on the oxblood page and in the navbar. (Claude in Chrome check, plus a pairing in the contrast list.)
6. The showcase renders without horizontal scroll at 360 px and 1280 px. (Playwright smoke test, E01-S07, and a Claude in Chrome check.)
7. The font loads from the app's own files. (Test that the built CSS has no `https://` font URL.)

## Tests

- `src/styles/tokens.test.ts` for contrast, hygiene and the cyan rule. `/dev/tokens` is the visual check.

## Out of scope

Real screens and components beyond the shadcn base (each UI story adds its own), a light theme, internationalisation.

## Open questions

- Confirm D-053's typeface (Inter) and icon set (lucide), and "single theme".
- Check the navbar reading above against the reference image.
