# @tradepulse/landing

The public marketing page. Separate from `apps/web`, which is the review desk.

## Why it is its own app

`apps/web` runs **Next 15 + Tailwind 3**, and its `tailwind.config.ts` redefines
the whole Tailwind palette so that existing class names (`bg-teal-600`,
`text-slate-500`, and so on) render in the TradePulse eight-colour system.

This page runs **Next 16 + Tailwind 4**, where theming moves into CSS
(`@theme`, `@utility`) and the palette config model no longer applies. Merging
the two would mean a double major upgrade across the live workbench to gain a
marketing page — so they stay apart.

The repo is not an npm workspace: each app installs its own dependencies, so
the two trees never meet.

## Run it

```bash
cd apps/landing
npm install
npm run dev          # http://localhost:3000
```

| Script | What it does |
| --- | --- |
| `npm run build` | Production build (standalone output, for Docker) |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run words` | Fails if the rendered page exceeds 450 words (see below) |

## Deploy

```powershell
# from repo root
.\infra\gcp\deploy-landing.ps1
```

Builds `apps/landing/Dockerfile` and pushes to Cloud Run as
`tradepulse-landing`, alongside `tradepulse-web` and `tradepulse-api`. The
call-to-action URL is resolved from the deployed `tradepulse-web` service, or
set `REVIEW_DESK_URL` to override.

## How it is put together

- **All copy lives in `content/site.ts`.** Edit wording there, never in
  components. The header of that file carries the wording rules taken from the
  team's do-not-claim list: say "potential match", "review required",
  "discrepancy"; never "fraud", "sanctioned", "AI approved" or "cleared", and
  never imply TradePulse moves, tracks or inspects freight.
- **Under 450 words.** The audience is a CXO with a minute and no trade-finance
  background. `npm run words` enforces it rather than leaving it to judgement.
- **Twelve-column grid, edge-to-edge panels.** Vertical rules are always
  `border-left` on the right-hand cell — mixing that with `border-right` on the
  left cell puts the two rules on opposite sides of the same grid line and they
  land a pixel apart.
- **One palette switch.** `app/globals.css` defines three palettes; pick one
  with `data-palette` on `<html>` in `app/layout.tsx` (`ink`, `signal`,
  `ledger`).
- **Screenshots are real.** `public/shots/*.png` are captured from the live
  review desk with border radii flattened, so the frames' own corner radius
  does the clipping. Recapture with the script noted in the `Shot` component.
- **Motion is one sequence.** The hero plays a single orchestrated animation;
  nothing else animates on scroll, which is deliberate. Lenis handles smooth
  scrolling and needs its stylesheet imported — without it Lenis measures the
  viewport instead of the document and the page stops scrolling part-way down.

## Accessibility and quality gates

Every text and background pair is checked for WCAG AA contrast, there is no
horizontal overflow from 360px to 1920px, reduced-motion and no-JavaScript both
render the full page, and every pointer target is at least 24px.
