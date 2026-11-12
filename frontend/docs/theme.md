# Theme

The identity is three colours (D-013, D-052). One theme only (D-053): there is no light variant and no switch.

| Role | Colour |
|---|---|
| Page and panel backgrounds | Oxblood `#4A0E1B` |
| Text, the navbar and hover highlights | Dusty rose `#E3B5AE` |
| Everything else: buttons, links, icons, focus rings, selection, active states, progress | Electric cyan `#00E5FF` |

## Rules

1. **No colour values outside `src/styles/tokens.css`.** No hex, `rgb(`, `hsl(` or `oklch(` anywhere else in `src/`, and no Tailwind built-in colour classes such as `bg-red-500`. A test enforces both.
2. **Components use semantic tokens**, never the base colours: `bg-background`, `text-foreground`, `bg-surface`, `bg-primary text-primary-foreground`, `text-muted-foreground`, `text-destructive`, `border-border`, and so on. Changing one base token (`--oxblood`, `--rose`, `--cyan`) recolours the app.
3. **Cyan never sits on rose.** A rose hover highlight flips its text and icons to oxblood (`bg-hover text-hover-foreground`). The rose navbar carries oxblood content, its active item is marked by an oxblood underline or fill, and its focus ring is oxblood. Cyan text or icons on a rose surface is forbidden. Oxblood text on a cyan fill (a primary button) is fine: the cyan is the surface there, not the text.
4. **Every new text-on-background pairing is added to the list in `src/styles/tokens.test.ts`** in the same change. Body text needs 4.5:1; large text and UI icons need 3:1.

## Which token for what

| Token | Use |
|---|---|
| `--background` | Page background |
| `--foreground` | Body text |
| `--surface` | Cards, dialogs and panels on the page (oxblood-raised) |
| `--navbar`, `--navbar-foreground` | The navbar and what is on it |
| `--hover`, `--hover-foreground` | Hovered rows and menu items |
| `--primary`, `--primary-foreground` | Buttons, links, icons, active states, progress |
| `--ring` | Focus ring (2 px, offset 2 px; oxblood inside the navbar) |
| `--selection` | Selected rows, with a cyan edge (`border-l-primary`) |
| `--border` | Borders and dividers (decoration, not text) |
| `--muted-foreground` | Secondary text |
| `--destructive` | Errors and destructive actions (amber, readable on oxblood) |

Derived tints in `tokens.css`: `--oxblood-raised`, `--oxblood-sunken` (input wells), `--oxblood-selected`, `--rose-muted`, `--rose-line`, `--cyan-dim` (pressed or disabled cyan).

## Type, icons, spacing

- Typeface: Inter variable, self-hosted through `@fontsource-variable/inter` (no external requests). A system stack is the fallback. Monospace (`font-mono`) for IDs and sizes.
- Icons: `lucide-react`, 16, 20 or 24 px only.
- Spacing: Tailwind's 4 px scale, with 8 px as the layout rhythm. Radius: `--radius` and `--radius-sm`.

## Breakpoints

Phone below 640 px, tablet from 640 px (`sm`) and 768 px (`md`), desktop from 1024 px (`lg`), wide from 1280 px (`xl`). The minimum supported width is 360 px. Touch targets are at least 44 px (`min-h-11`) on phone widths.

## Dev showcase

Run `npm run dev` and open `/dev/tokens`. It shows every semantic token, the text pairings, a focus ring, hover and selected rows, and the navbar. The route is left out of the production build (`npm run build` fails if it leaks).
