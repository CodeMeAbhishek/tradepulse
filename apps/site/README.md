# TradePulse Evidence

You are the design lead at a studio known for restraint. Build a complete,

finished, production-quality website for TradePulse AI in one pass. Simple,

classic, severe. Nothing decorative. Every element earns its place.

STACK

Vite + React 18 + TypeScript + Tailwind + react-router-dom + Framer Motion

(the `motion` package). No backend, no auth, no CMS. All copy in typed files

under src/content/, all demo data in src/data/. Runs with

npm install && npm run dev.

BUILD IN THIS ORDER, and do not move on until each is right:

  1. tailwind.config.js — colours, three font families, the exact type scale

  2. The shell — TopBar, LedgerRail, Footer, and the ui/ primitives

  3. The bench component — the signature interaction, the hardest thing here

  4. The home page

  5. /product, /method, /contact

  6. A final self-audit against the BANNED list at the end of this brief

WHAT THE PRODUCT IS

TradePulse AI is verification middleware for cross-border trade finance. A

bank compliance officer uploads a set of trade documents — commercial invoice,

bill of lading, packing list, certificate of origin, and the letter of credit

(SWIFT MT700). Four agents run: extraction, cross-document consistency against

UCP 600 discrepancy rules, price verification against UN Comtrade unit-value

bands (which catches over- and under-invoicing, i.e. trade-based money

laundering), and sanctions screening. The output is a scored, explainable

exception report that a human signs off on.

The claim the whole design must express: THE MODEL EXTRACTS, DETERMINISTIC

CODE DECIDES. Nothing is scored by a language model. Every finding traces to

a source document, page and field. Design this as evidence, not as a

dashboard.

Audience: bank compliance officers, trade finance ops leads, regulators.

Register: institutional, unexcited, specific. It should look like the site of

a company that already has customers and does not need to raise its voice.

────────────────────────────────────────────────────────────────

VISUAL SYSTEM

────────────────────────────────────────────────────────────────

COLOUR — these eight values and nothing else:

  #F4F2ED  Bench      page background

  #FFFDF8  Paper      document surfaces and raised planes only

  #12202E  Ink        headings, top bar, primary text, footer plane

  #3A4A5C  Slate      body copy, metadata, captions

  #D9D4CB  Rule       every hairline, divider, border, table grid

  #C1272D  Stamp      CRITICAL FINDINGS ONLY

  #D68910  Amber      needs review

  #2D7D5A  Verified   passed checks

STAMP RED DISCIPLINE — the most important rule in this project.

#C1272D appears nowhere except on an actual critical finding and its

annotation box. Not the logo. Not a button. Not a link, hover state,

underline, nav item, footer, or statistic. Its scarcity is its entire

meaning. Audit for this before you finish and report what you removed.

TYPE — IBM Plex family from Google Fonts. The identity decision:

DISPLAY AND ALL HEADINGS ARE SET IN IBM PLEX MONO. Not a sans. Trade

documents come from the telex world; monospace is native to the subject, and

at large sizes with tight leading it reads as severe and institutional rather

than technical. Do not substitute a sans for headlines under any

circumstances.

  IBM Plex Mono            every heading, and every piece of document data —

                           HS codes, LC references, amounts, dates, port

                           codes, vessel names, UCP article numbers,

                           citations. Always font-variant-numeric:

                           tabular-nums.

  IBM Plex Sans            body copy, paragraphs, navigation

  IBM Plex Sans Condensed  eyebrows, labels, all-caps markers, table headers

Define fontFamily.mono, fontFamily.sans, fontFamily.condensed in

tailwind.config.js. `font-sans-condensed` is not a real Tailwind class and

silently falls back — never write it.

TYPE SCALE — put these in the config as named steps and use ONLY these.

No arbitrary sizes anywhere in the codebase.

  display   64 / 1.00 / -0.025em / 500 / mono

  h1        46 / 1.06 / -0.02em  / 500 / mono

  h2        32 / 1.14 / -0.015em / 500 / mono

  h3        21 / 1.28 / -0.01em  / 500 / mono

  body-lg   19 / 1.55 / 400 / sans

  body      17 / 1.62 / 400 / sans

  small     15 / 1.5  / 400 / sans

  label     12 / 1.2  / 0.10em / 600 / uppercase / condensed

  data      16 / 1.45 / mono / tabular-nums

Everything is ~1.25x normal web sizing because this gets demoed on a

projector to people sitting ten feet away. Legibility beats density.

LAYOUT — THE LEDGER GRID, the structural signature.

A persistent 72px vertical rail runs down the left edge of every page,

divided from the content by one hairline. It is the margin of a bound ledger.

Inside it, rotated -90deg in condensed caps at 12px, the current section

number and name — "02 · METHOD" — updating as you scroll. At the rail's

bottom, a 1px scroll-progress line fills as you descend. Hidden below 1024px.

Content sits in a 12-column grid to the right of the rail, 32px gutter,

max-width 1440px.

NOTHING IS CENTERED. Section headings hang in columns 1–4; body copy sits in

columns 5–11. Rotate three content widths so the page has rhythm: full-bleed,

12-column, and a narrow 6-column reading measure for prose. Never let two

adjacent sections share a width.

VERTICAL RHYTHM MUST BE UNEVEN. Section spacing rotates through 96px, 180px

and 260px depending on weight. A constant gap between every section is the

single clearest sign of generated work. Vary it deliberately.

────────────────────────────────────────────────────────────────

BANNED — if you produce any of these, stop and choose differently

────────────────────────────────────────────────────────────────

  - Any centered hero, centered heading, or centered section

  - Cards with icons in circles. No icon cards anywhere. No icons at all.

  - Any border-radius above 2px

  - Any box-shadow

  - Any gradient, mesh, blur, glassmorphism, or backdrop glow

  - Emoji or warning triangles. The only permitted glyphs: → · ✺ + − =

  - Photography of any kind, especially people in offices. Where a normal

    site would place a photograph, place a document facsimile.

  - A circular or arc risk gauge

  - Lorem ipsum or any placeholder-shaped content

  - The words: seamless, seamlessly, powered by AI, unlock, leverage,

    revolutionise, cutting-edge, game-changing, robust, solution, empower

  - A section that is a heading with one sentence under it. Every section

    carries real content.

────────────────────────────────────────────────────────────────

SHELL — src/components/shell/

────────────────────────────────────────────────────────────────

TopBar — sticky, 68px, bench-coloured, hairline bottom rule. Left: "✺

TRADEPULSE" in Plex Mono 18px, letter-spacing 0.06em. Centre-left: nav in

Plex Sans 15px — The bench, Method, Contact. Right: one text link "Book a

walkthrough" whose hairline underline draws in from the left over 180ms on

hover. After 60px of scroll the rule darkens and a 1px progress line appears

beneath the bar.

LedgerRail — as specified above.

Footer — ink plane, full bleed, 180px top padding. Across the top, one line

in h2 mono: "Every finding names its document, its page, and its field."

Beneath, three link columns with condensed-caps headers. Bottom strip in

condensed caps, slate on ink: "GIFT IFSC · AHMEDABAD" and "IN→AE CORRIDOR

LIVE · SG, UK, US IN DEVELOPMENT".

ui/ primitives, each in its own file: Eyebrow, SectionHeading, RuleDivider,

DataTable (hairline grid, mono cells, condensed-caps headers, zebra-free),

DocumentFacsimile, StatFigure, Accordion, QuietButton, Finding,

InlineCitation.

DocumentFacsimile is used throughout and must be convincing: a paper-coloured

plane, a realistic letterhead with a fictional company name and address

block, a reference block top-right, a field grid with hairline rules, a

signature line, and a faint circular rubber-stamp mark rotated a few degrees.

Variants: invoice, billOfLading, certificateOfOrigin, mt700. The mt700

variant renders fixed-width SWIFT tags in Plex Mono on paper — :20:, :31D:,

:32B:, :44E:, :45A:, :46A:, :47A: — with realistic values.

────────────────────────────────────────────────────────────────

THE BENCH — the signature. Build this before the pages.

────────────────────────────────────────────────────────────────

A working, interactive examination bench. Not a screenshot, not a video.

It appears full-bleed on the home page and is the whole of /product.

Layout: document viewer left (~60%) on paper, findings panel right (~40%) on

bench, a thin status strip above both showing document count, corridor, and

HS code in mono.

EMPTY STATE — a wide drop zone on paper stock, hairline dashed border, with

the accepted types in condensed caps: COMMERCIAL INVOICE · BILL OF LADING ·

PACKING LIST · CERTIFICATE OF ORIGIN · LETTER OF CREDIT (MT700). One

prominent button, "Load sample document set", which populates everything in

a single click. Never require a real file — a live demo will use the button.

RUN STATE — four agents surface findings one at a time, staggered, under four

seconds total. Each agent row: name in condensed caps, a thin determinate

sweep line that fills left to right, then its findings sliding into the panel

beneath it. No percentage counters. No spinners. No fake progress bars.

RESULT STATE — the findings panel leads with the count in display mono,

"3 discrepancies — 2 critical", with the numeric risk score small and

secondary beside it. Then the findings list. Each finding shows: severity in

condensed caps, title in h3, body in body copy, and a citation line in mono —

"Commercial Invoice · p.1 · line 3" — plus the UCP article where one applies.

THE SIGNATURE INTERACTION — the most important thing you will build:

Clicking a finding makes the left pane scroll and zoom to the exact region of

the document that finding cites, and draws an annotation box around it. For

findings of type "cross_document" the left pane splits horizontally — invoice

above, bill of lading below — and an SVG path is drawn between the two

conflicting values. One orchestrated camera move, not scattered effects.

Implementation rules for this, non-negotiable:

  - Never hardcode annotation coordinates in pixels. Store normalised

    fractions {x,y,w,h} in the finding data, measure the target with

    getBoundingClientRect() relative to the scroll container, and

    requestAnimationFrame one frame after any layout change before

    positioning. Attach a ResizeObserver to the document container and

    recompute on resize.

  - The zoom is a FLIP-style transform on the document container so it reads

    as one continuous camera move, not a jump plus a fade.

  - The annotation box draws its four sides via SVG stroke-dashoffset over

    400ms, then pulses border-opacity once over 1.4s. Once — not looping.

  - The cross-document connector is an SVG path animated with pathLength 0→1

    over 600ms, with a small dot travelling along it.

  - The horizontal split animates open with a spring; it does not cut.

────────────────────────────────────────────────────────────────

ROUTE 1 — / (home)

────────────────────────────────────────────────────────────────

01 HERO — full bleed, asymmetric, no photograph

   Eyebrow: "VERIFICATION MIDDLEWARE · CROSS-BORDER TRADE FINANCE"

   Headline in display mono, hanging in columns 1–7, three lines:

     Twenty documents.

     Three days.

     One discrepancy that matters.

   Body in columns 8–12: "TradePulse reads a cross-border trade document set,

   checks it against UCP 600 and market price bands, and returns a scored

   exception report with every finding traced to its source clause. The model

   extracts. Code decides."

   Two quiet actions: "See a live examination" (scrolls to the bench) and

   "How a finding is proved" (routes to /method).

   Behind the headline at 6% opacity, a very large Plex Mono block of MT700

   tags, parallaxing upward 40px across the hero's scroll range.

   Section closes on a full-bleed hairline strip in condensed caps listing

   the five accepted document types.

02 THE PROBLEM — three rows, hairline separated. Not cards.

   Each row: a mono figure hanging left, a heading, a paragraph.

     USD 2.5tn  The trade finance gap — attach an InlineCitation reading

                "ADB Trade Finance Gaps Report — verify figure and year

                before quoting" so it is honest and trivial to correct

     3 days     Median manual review time for one full document set

     80%        Share of trade-based money laundering that moves through

                over- and under-invoicing

   Closing line in h3: "Every one of those days is an exporter's working

   capital, frozen."

03 THE BENCH — full bleed, live, as specified above.

   Heading above it in h2: "One document set. Four agents. Nine seconds."

04 METHOD — sticky scroll-linked stack, four steps

   Left column: four numbered steps that highlight as scroll progresses.

   Right column: the matching panel cross-fades and rises. Numbering is

   earned — this is a real pipeline in real order.

     01 Extract — the model reads. Fields, never conclusions.

     02 Cross-check — UCP 600 rules in deterministic code. Invoice against

        bill of lading against packing list against LC.

     03 Verify price — declared unit value against UN Comtrade bands for the

        HS code and corridor.

     04 Screen and score — parties, vessel, ports. Then one report a human

        signs.

   Use useScroll and useTransform so the stack tracks scroll position

   continuously, not a once-off trigger.

05 WHY IT CANNOT HALLUCINATE — two columns, one vertical hairline

   Left header in condensed caps "WHAT THE MODEL DOES", right "WHAT CODE

   DOES". Four lines under each.

     Model: reads pixels · locates fields · normalises formats · transcribes

            values

     Code:  compares values across documents · applies UCP 600 articles ·

            tests against price bands · assigns severity

   Beneath the divider, one h2 line: "A model cannot invent a discrepancy it

   is not permitted to declare."

06 THE NUMBERS — four figures on hairlines, no cards

   Counters animating from zero on first entry:

     < 30s   per document set

     5       document types read

     0       decisions scored by a model

     100%    findings carrying a source citation

07 USE CASES — six full-width hairline rows, a → appearing on hover

   Import LC examination · Export document presentation · TBML price

   screening · Sanctions and vessel screening · Discrepancy audit trail ·

   Correspondent bank review

   Each row expands in place on click — no modal — to reveal two sentences of

   scenario, which agents run, and the corridor it applies to. Height

   animates with a spring and inner content staggers.

08 FAQ — accordion on hairlines, no boxes, generous rows, a rotating

   hairline plus/minus. Five questions, answered in full sentences:

     Where do the reference prices come from?

     Are you checking against UCP 600?

     What happens when you produce a false positive?

     What if the model hallucinates a discrepancy?

     Who signs off?

09 CLOSING — ink plane above the footer. h1 in mono: "See it examine a real

   document set." One action: "Book a walkthrough".

────────────────────────────────────────────────────────────────

ROUTE 2 — /product ("The examination bench")

────────────────────────────────────────────────────────────────

Hero: h1 mono "The document is never replaced by a summary of itself."

  Body: what the bench is, who uses it, and why the document stays on screen.

The bench itself, full width, the same component, in its own right.

"What is on screen at all times" — a DataTable of the interface regions and

  what each is for.

"The four agents" — one row each on hairlines. Columns: agent, what it reads,

  what it emits, and — the interesting one — what it is not permitted to

  decide. State that plainly for each.

"One finding, fully traced" — take finding 1 and expand it completely:

  source document, page, field, the extracted value, the rule applied, the

  reference band, the arithmetic shown in mono, and the resulting severity.

  This is the most persuasive object on the site. Make it real and detailed.

────────────────────────────────────────────────────────────────

ROUTE 3 — /method ("The model extracts. Code decides.")

────────────────────────────────────────────────────────────────

Reads like a technical note, not marketing. Prose in a 6-column measure,

diagrams full bleed.

  Hero with eyebrow "ARCHITECTURE".

  An SVG pipeline diagram — documents in, four agents, orchestrator, scored

    report out. Hairline strokes only, mono labels, no filled shapes. Paths

    draw left to right on scroll.

  "Where the boundary sits" — the model/code split from the home page,

    expanded into full paragraphs with worked examples.

  "The UCP 600 checks we run" — a real DataTable, at least ten rows.

    Columns: Article, Check, What triggers a discrepancy, Severity. Use

    genuine articles — 14(c) presentation period, 14(d) data consistency,

    14(e) goods description, 18(c) invoice description, 20 bill of lading,

    23 air waybill, 27 clean transport document, 28 insurance cover, 30

    tolerance in amount and quantity, 31 partial shipment. This table is the

    single most credible object on the site. Get it right.

  "Price bands" — how a Comtrade unit-value band is derived (trade value ÷

    quantity, by HS code and corridor), the arithmetic shown in mono, and an

    honest paragraph stating that the demo uses pre-computed bands for one

    corridor while production pulls live feeds.

  "What we do not do" — four plain paragraphs. We do not approve. We do not

    lend. We do not score with a model. We do not assert without a citation.

────────────────────────────────────────────────────────────────

ROUTE 4 — /contact

────────────────────────────────────────────────────────────────

Asymmetric — form in columns 1–6, details in 8–12. Fields are

hairline-underlined only: no boxes, no rounded inputs, no placeholder text

inside fields. Labels in condensed caps above each field. Submit is a text

link with a drawn underline. On submit, post nowhere: animate the form out

and a mono confirmation line in. Mark it // INTEGRATION SEAM.

────────────────────────────────────────────────────────────────

MOTION — few, precise, orchestrated. Restraint is the point.

────────────────────────────────────────────────────────────────

  - Page load: one sequence. The top bar rule draws left to right over 500ms;

    the headline reveals line by line through a clip-path mask with 70ms

    stagger; the ledger rail label fades last. 1000ms total, then stillness.

  - Route change: outgoing fades and lifts 12px, incoming fades in, the rail

    number flips like a counter. 260ms.

  - Scroll reveals: translateY 20px plus opacity on a spring (stiffness 90,

    damping 20). Trigger at 18% into viewport. Once only. Never on scroll up.

  - Hairline dividers: scaleX 0→1 from the left over 400ms as their section

    enters.

  - Counters: 0 to value over 1.2s, ease-out, first entry only.

  - Links and nav: hairline underline draws from the left over 180ms.

  - Buttons: 120ms border-colour and transform, 1px inward press on active.

    No scale-up, no glow, no bounce.

  - The bench interactions as specified in its own section above.

  - Hero MT700 backdrop parallax, 40px over the hero's scroll range.

  - prefers-reduced-motion: reduce — all of the above collapses to plain

    opacity fades and the document zoom becomes an instant scroll. Implement

    it properly.

Nothing loops. Nothing pulses continuously. Nothing moves unless the reader

caused it.

────────────────────────────────────────────────────────────────

DATA — src/data/mockDocumentSet.ts, every export commented

// SYNTHETIC DEMO DATA

────────────────────────────────────────────────────────────────

Cotton fabric, India to UAE, HS 5208.52, USD 181,280.

  LC applicant   = the BUYER: Al-Futtaim Textiles LLC, Dubai, UAE

  LC beneficiary = the SELLER: Global Textiles Pvt Ltd, Coimbatore, India

  The issuing bank serves the applicant, so Emirates NBD issues and State

  Bank of India advises. The certificate of origin consignee and the LC

  beneficiary are deliberately NOT the same party — that is finding 3.

  Invoice: 44,000 kg @ USD 4.12/kg = USD 181,280

  Bill of lading: 42,300 kg

  Comtrade band, HS 5208.52, IN→AE: USD 2.60–2.90/kg

  Vessel MV KOTA LAYANG. Ports INNSA (Nhava Sheva) → AEJEA (Jebel Ali).

  LC reference LC/EBI/2026/44817, invoice GTX-2026-0912, B/L KLYG4471882.

  Incoterms CIF Jebel Ali. Presentation period 21 days.

Findings:

  1. CRITICAL  Unit price exceeds reference band. Invoice declares USD

     4.12/kg. Comtrade band for HS 5208.52, IN→AE, is 2.60–2.90. Deviation

     +42% above band ceiling. Commercial Invoice · p.1 · line 3

  2. CRITICAL  Quantity does not reconcile across documents. Invoice states

     44,000 kg; bill of lading states 42,300 kg. UCP 600 Art. 14(d).

     type: cross_document

  3. REVIEW    Consignee named on the certificate of origin differs from the

     beneficiary named in the LC. type: cross_document

  4. PASSED    No sanctions matches on parties, vessel or ports.

  5. PASSED    LC expiry and presentation period within terms.

Each finding: id, severity, title, body, sourceDoc, page, field, agent,

ucpArticle (nullable), type ('single' | 'cross_document'), region {x,y,w,h}

as fractions 0–1, and secondRegion for cross_document findings.

COPY VOICE

Declarative, unexcited, specific. Active voice, sentence case, no filler, no

apologising. Findings read like an examiner's note. Marketing copy in the

same register — if a sentence could appear on any other AI company's site,

rewrite it with a real number or a real document term in it.

────────────────────────────────────────────────────────────────

BUILT FOR HANDOFF — a Python backend gets wired to this tomorrow

────────────────────────────────────────────────────────────────

  - One component per file under src/components/. No file over ~200 lines.

  - All types in src/types/index.ts, exactly this contract:

      ExtractionResult { item, quantity, unit_price, currency, buyer, seller,

        invoice_date, shipment_terms }

      VerificationResult { entity, match_status: 'clear'|'potential_match'|

        'confirmed_match', matched_name, confidence, source_list }

      PriceAuditResult { item, declared_price, benchmark_price,

        deviation_pct, flagged, threshold_pct }

      DocumentSetResult { document_id, extraction, verification[],

        price_audit, risk_level: 'green'|'amber'|'red', findings[] }

  - ONE async function runAnalysis(): Promise<DocumentSetResult> in

    src/lib/analysis.ts, currently resolving the mock through staged

    setTimeouts to drive the agent sequence. Comment it:

    // INTEGRATION SEAM — replace body with POST /api/analyze, keep signature

    Nothing else in the codebase may reference the mock data directly.

  - Motion durations and easings as named constants in src/lib/motion.ts.

  - NEVER construct a Tailwind class name at runtime. `border-[${color}]` and

    `text-${severity}` compile to nothing because Tailwind scans source

    statically. Use inline style={{ borderColor }} or a static map of

    complete class strings.

  - No localStorage or sessionStorage. React state only.

  - All colours as CSS custom properties on :root plus a Tailwind theme

    extend, so one edit restyles everything.

QUALITY FLOOR, unannounced: visible ink focus rings, arrow-key navigation

through the findings list, aria-live on the findings panel as findings

arrive, no horizontal scroll at 1280px, intact at 1024px with the rail hidden

and the bench stacking vertically.

────────────────────────────────────────────────────────────────

FINISH WITH A SELF-AUDIT

────────────────────────────────────────────────────────────────

Before you report done, check every file and tell me:

  1. Every instance of #C1272D and whether it is on a critical finding

  2. Any centered element, icon card, radius above 2px, shadow, or gradient

  3. Any banned word in the copy

  4. Any Tailwind class name built at runtime

  5. Any text using a size outside the named scale

Fix each and list what you changed.

BEFORE YOU WRITE CODE: state your layout plan in three sentences and name the

one element this site will be remembered by. Then build all four routes.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/28c57307-ce5f-4429-a0cc-3dd781f0dd23).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
