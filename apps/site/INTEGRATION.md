# TradePulse — frontend integration notes

Handoff doc for whoever wires the Python backend to this landing page.
Everything below is current as of this commit and was verified against a running
dev server, not assumed.

---

## 1. Running it

```bash
npm install
npm run dev
```

**The dev server binds to `:8080`, not Vite's usual 5173.** The Lovable config
(`@lovable.dev/vite-tanstack-config`) overrides the port. Don't waste ten minutes
on this like I did.

```bash
npm run build
```

Stack: Vite + React 19 + TypeScript + **TanStack Start** (SSR) + Tailwind v4 +
`motion` v13. Routes are file-based in `src/routes/`.

---

## 2. There is exactly one integration seam

`src/lib/analysis.ts` — one function, ~10 lines:

```ts
export async function runAnalysis(): Promise<DocumentSetResult> {
  await new Promise((resolve) => setTimeout(resolve, 450));
  return mockDocumentSet;
}
```

This is the **only** place mock data is referenced, and the **only** thing the
bench calls. Verified:

- `runAnalysis` is imported by exactly one file — `src/components/bench/ExaminationBench.tsx`
- `mockDocumentSet` is imported by exactly one file — `src/lib/analysis.ts`

Replace the body, keep the signature, and the whole UI follows. Nothing else in
the codebase needs to change.

### Three constraints on how you replace it

1. **Keep it a plain client-side async function.** Do NOT turn it into a
   TanStack server function or a server route. It is meant to become a `fetch`
   to an external FastAPI service. The seam must not depend on the framework.
2. **This app server-side renders.** Never touch `window` or `document` during
   render. Anything that measures must sit in `useEffect`/`useLayoutEffect`.
3. Don't reintroduce the mock import anywhere else — the single-import property
   above is what makes this swap safe.

### Suggested replacement

```ts
const API = import.meta.env['VITE_API_URL'] ?? 'http://localhost:8000';

export async function runAnalysis(): Promise<DocumentSetResult> {
  const res = await fetch(`${API}/api/analyze`, { method: 'POST' });
  if (!res.ok) throw new Error(`analyze failed: ${res.status}`);
  return (await res.json()) as DocumentSetResult;
}
```

For a live demo, consider falling back to `mockDocumentSet` inside a `catch` so
the bench never dies on stage if the backend is down.

---

## 3. The contract

Full types in `src/types/index.ts`. The envelope:

```ts
interface DocumentSetResult {
  document_id: string;
  extraction: ExtractionResult;
  verification: VerificationResult[];
  price_audit: PriceAuditResult;
  risk_level: 'green' | 'amber' | 'red';
  findings: Finding[];
}
```

`findings[]` is what drives the entire bench UI. Per finding:

```ts
interface Finding {
  id: string;
  severity: 'critical' | 'review' | 'passed';
  title: string;
  body: string;
  sourceDoc: string;        // display label, e.g. "Commercial Invoice"
  sourceKind: DocumentKind; // enum — picks which facsimile renders
  page: number;
  field: string;            // e.g. "line 3 · unit price"
  agent: AgentName;         // enum — picks which agent row it appears under
  ucpArticle: string | null;
  type: 'single' | 'cross_document';
  region: Region;           // REQUIRED
  secondDoc?: string;       // required when type === 'cross_document'
  secondKind?: DocumentKind;
  secondRegion?: Region;
}
```

### Enums are closed sets — a string outside these will break rendering

```
DocumentKind: 'invoice' | 'billOfLading' | 'packingList'
            | 'certificateOfOrigin' | 'mt700'

AgentName:    'extraction' | 'consistency' | 'price' | 'sanctions'
```

`agent` determines which of the four agent rows a finding is filed under, and
findings are revealed in that order. A finding with an unrecognised `agent`
value will simply never appear.

### `region` — read this one carefully

```ts
interface Region { x: number; y: number; w: number; h: number }  // fractions 0–1
```

**Normalised fractions of the document plane, never pixels.** This is what lets
the viewer scroll-and-zoom to the cited region and draw the annotation box at
any window size. Example from the mock:

```ts
region: { x: 0.06, y: 0.545, w: 0.88, h: 0.085 }
```

If the backend can't produce real coordinates yet, send plausible constants —
the UI degrades gracefully in position but **not** in presence. A missing
`region` means no annotation box and no camera move, which removes the single
most impressive interaction on the site.

For `type: 'cross_document'`, `secondRegion` + `secondKind` are what split the
viewer horizontally and draw the connector between the two conflicting values.

---

## 4. Known issues to handle during integration

**a) Long API calls produce dead air.**
`ExaminationBench.load()` awaits `runAnalysis()` *before* starting the agent
animation timers:

```ts
const set = await runAnalysis();   // ← real latency lands here
setResult(set);
// ...then the staged reveal timers start
```

The staged reveal is a fixed ~3.5s client-side sequence (`SWEEP_MS` in
`ExaminationBench.tsx`), independent of real backend timing. So an 8-second API
call = 8 seconds of "EXAMINING" with no movement, *then* the animation. Options:
start the sweep optimistically before the await, or stream per-agent results.

**b) The risk score is computed client-side and ignores the backend.**
In `FindingsPanel.tsx`:

```ts
const riskScore = criticals * 30 + (discrepancies - criticals) * 10;
```

If the backend returns its own score, wire it through — right now
`risk_level` is displayed but the numeric score is invented by the UI.

**c) The bench measures inside `requestAnimationFrame`**, which is parked while
a tab is hidden. There's a `visibilitychange` re-measure guard in
`DocumentPane.tsx` for the background-tab case — don't remove it.

---

## 5. Dead code, deliberately left in place

Not bugs — don't be confused by them, and don't feel obliged to wire them up:

- `src/components/home/HeroBackdrop.tsx` — built, then removed from the hero on
  request. Unreferenced.
- `src/components/kit/Accordion.tsx` and `src/components/kit/StatFigure.tsx` —
  zero importers since the FAQ and Numbers sections were cut from the home page.
- `numbers`, `useCases` and `faq` in `src/content/home.ts` — exported, no longer
  imported.

The home page was cut from 9 sections to 5 for the demo. All of the above is
kept so any section can be restored with one import line.

---

## 5a. Layout invariants — please don't revert these

Each of these fixed a measured bug. They look like small style details:

- **`min-w-0` on the bench grid children** (`FindingsPanel`, `DocumentStage`).
  Grid items default to `min-width: auto` and cannot shrink below min-content;
  without this the 64px display figure forced 245px of horizontal page scroll
  at 1024px.
- **The bench grid splits at `xl:`, not `lg:`.** At 1024 a 60/40 split gives the
  document pane ~450px, narrower than the facsimile table's ~591px min-content,
  and the document overflows its own pane. Stacking until 1280 gives it the
  full column.
- **The stage height is responsive** (`560 / 620 / 760 / 860`). The facsimile is
  ~1082px tall at narrow widths; a fixed 620px stage scaled it to 0.57, i.e.
  ~7px body text. At 1920 the document now renders at true 1:1.
- **Keyboard nav reads buttons in DOM order**, not by index into
  `result.findings`. Findings render grouped by agent, so the two orders differ
  (`1,2,4,0,3` vs `0,1,2,3,4`) and arrow keys jumped around the panel.
- **The hero headline steps down through the type scale** on small screens.
  64px monospace cannot fit 375px and will not break mid-word.

---

## 6. State at handoff

Verified against a running dev server, not assumed:

- `npx tsc --noEmit` — clean
- `npm run build` — passes
- `/`, `/product`, `/method` — all 200; unknown paths 404 correctly
- No console errors, no React warnings, no hydration mismatch
- **No horizontal scroll at 375 / 1024 / 1280 / 1920** on any route
- Bench verified end-to-end against the mock: 5 findings, 4 agents,
  "3 discrepancies", "2 critical · risk score 70 / 100 · RED"
- Cross-document finding opens the split pane with 2 annotation boxes and
  1 connector path
- Keyboard nav walks the findings in visual order and holds the selection at
  both ends of the list
- Document fit scale by viewport: 0.94 @1024, 0.79 @1280, **1.00 @1920**

There is no `/contact` route — it was removed, along with every link to it.

One caveat: the bench measures inside `requestAnimationFrame`, which is parked
in a hidden tab. If you automate checks against it, patch `rAF` to `setTimeout`
before the pane mounts or your measurements will silently read as unmeasured.
