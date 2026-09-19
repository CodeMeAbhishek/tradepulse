/**
 * All landing-page copy. The team edits wording here, never in components.
 *
 * Wording rules (from the team repo's frontend rules and do-not-claim list):
 * - Say "potential match", "review required", "discrepancy".
 * - Never say fraud, sanctioned, AI approved, cleared, or imply TradePulse
 *   moves, tracks or inspects freight.
 * - Every statistic carries its period and source.
 *
 * Length rule: the rendered page stays under 450 words. The audience is a CXO
 * with sixty seconds who has never worked a trade desk. `npm run words`
 * enforces it.
 *
 * Style rule: no strings joined by middle dots, no ALL-CAPS labels, no arrows
 * inside link text. Write sentences.
 */

export const LINKS = {
  /**
   * The desk seeds its own sample cases on arrival, so this lands on a working
   * queue rather than an empty screen. Case IDs are generated per visit, which
   * is why we never deep-link to one.
   *
   * Set NEXT_PUBLIC_REVIEW_DESK_URL at build time to point at another
   * deployment of apps/web; the default is the current Cloud Run demo.
   */
  reviewDesk:
    process.env.NEXT_PUBLIC_REVIEW_DESK_URL ??
    "https://tradepulse-web-gk63mqpoca-el.a.run.app/workbench",
  linkedin: "https://www.linkedin.com/company/tradepulseai/",
  email: "tradepulse004@gmail.com",
} as const;

export type Status = "verified" | "review" | "mismatch";

export const NAV = [
  { label: "What it catches", href: "#proof" },
  { label: "How it works", href: "#how" },
  { label: "Questions", href: "#faq" },
] as const;

export const HERO = {
  kicker: "Documentary trade review",
  headline: "Two documents. One number that doesn’t match.",
  /** Split so the opening clause can be lit and the rest recede. */
  bodyLead: "TradePulse reads every field of a trade document against its invoice.",
  bodyRest: "Your officer gets a case they can defend.",
  primary: "Open the review desk",
  secondary: "See how it works",
  residency: "Selected for the GIFT IFIH Young Builders' Program residency, 2026",
  /**
   * The hero is this comparison, set as type rather than as a screenshot: it is
   * the one thing a visitor has to understand, and it is the product's whole
   * argument in two numbers.
   */
  compare: {
    ref: "Case TP-2208",
    field: "Quantity",
    left: { doc: "Commercial invoice", value: "500", unit: "cartons" },
    right: { doc: "Bill of lading", value: "350", unit: "cartons" },
    verdict: "These have to agree. They don’t.",
  },
} as const;

export const PROOF = {
  label: "Evidence",
  title: "The same case, in the product.",
  shot: {
    src: "/shots/compare-2.png",
    width: 2496,
    height: 1064,
    alt: "Invoice and bill of lading compared field by field, with a quantity mismatch flagged",
  },
  caption: "The live review desk, showing demo data.",
  /** The three outcomes any field can land on, read as a legend for the table. */
  notes: [
    { field: "Quantity", body: "500 against 350.", status: "mismatch" as Status },
    { field: "Goods, ports, reference", body: "Matched after normalisation.", status: "verified" as Status },
    { field: "On one document only", body: "Stays open. Never a pass.", status: "review" as Status },
  ],
} as const;

/** Guarantees, not traction. Each one is enforced in the product's code. */
export const GUARANTEES = [
  { figure: "0", label: "automatic approvals", hint: "Every case ends at a named officer." },
  { figure: "3", label: "review rounds at most", hint: "Unresolved after three, it comes to you." },
  { figure: "5", label: "references per finding", hint: "Document, page, field, rule, version." },
  { figure: "4", label: "rungs of identity", hint: "A similar name is a lead, not proof." },
] as const;

export const HOW = {
  label: "Method",
  title: "Three steps to a defensible case.",
  steps: [
    {
      n: 1,
      title: "Upload the pack",
      body: "The invoice, plus the transport documents the case needs.",
      shot: { src: "/shots/docs-2.png", width: 2496, height: 526, alt: "Document checklist showing required, conditional and optional documents" },
      caption: "A missing required document blocks the case.",
    },
    {
      n: 2,
      title: "Read, checked, challenged",
      body: "Up to three passes. Disagreements stay open, never averaged away.",
      shot: { src: "/shots/checks-2.png", width: 2496, height: 432, alt: "Screening, price plausibility and duplicate-submission checks, each with its evidence source" },
      caption: "Every check names its source.",
    },
    {
      n: 3,
      title: "Your officer decides",
      body: "Maker reviews, checker confirms. TradePulse never approves.",
      shot: { src: "/shots/ladder-2.png", width: 2496, height: 708, alt: "Four-rung identity confidence ladder, from a document name up to a verifiable credential" },
      caption: "A counterparty climbs only on evidence.",
    },
  ],
} as const;

export const NEED = {
  label: "Why now",
  lead: "Capacity has multiplied.",
  rest: "Examination has not.",
  figures: [
    { figure: "USD 106 bn", label: "Banking assets at GIFT IFSC", period: "December 2025" },
    { figure: "7.5×", label: "Growth in five years", period: "September 2020 to December 2025" },
    { figure: "37", label: "Banks examining that paperwork", period: "December 2025" },
  ],
  sources:
    "IFSCA figures via CII and the HSBC–EY GIFT IFSC compendium, December 2025. Market figures, not ours.",
} as const;

export const NEVER = {
  label: "Limits",
  title: "What it never claims",
  items: [
    "What is physically inside a container",
    "Customs clearance or any government filing",
    "That a transaction is approved, rejected or cleared",
    "That a similar name proves who a company is",
  ],
} as const;

export const FAQ = {
  label: "Questions",
  title: "Asked by every desk.",
  items: [
    {
      q: "Does it approve or reject transactions?",
      a: "No. It prepares the evidence. Every route ends at a named officer.",
    },
    {
      q: "Which documents does it read?",
      a: "The commercial invoice, plus whichever transport documents the case profile requires.",
    },
    {
      q: "Is a matching company name proof of identity?",
      a: "Never. A name is a lead. A Legal Entity Identifier matched to the global registry is evidence.",
    },
    {
      q: "Is it production-ready?",
      a: "Not yet. It is a working prototype. Demo documents are labelled and every output needs review.",
    },
  ],
} as const;

export const FINAL_CTA = {
  title: "Open a case. Walk the findings.",
  primary: "Open the review desk",
  fine: "A prototype. Sample documents are labelled as demo data.",
} as const;

export const FOOTER = {
  blurb: "Documentary trade review support. Your officers decide, not the software.",
  legal: "Outputs are decision support only and require authorised human review.",
  copyright: "© 2026 TradePulse",
} as const;
