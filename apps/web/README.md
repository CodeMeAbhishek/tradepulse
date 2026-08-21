# TradePulse web — compliance workbench

Ansh ownership: Next.js workbench shell for `v0.1-skeleton`.

## Run

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) (redirects to `/queue`).

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Local workbench |
| `npm run build` | Production build |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |

## Contracts note

`lib/contracts/mirror.ts` temporarily mirrors Abhishek’s frozen names from
`packages/contracts/tradepulse_contracts` (`feat/platform-skeleton` @ `71c24d1`).
That commit was not on origin when this shell was built. Replace the mirror when
the shared package is available — do not privately expand the shape.
