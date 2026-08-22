"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { BrandMark } from "@/components/BrandMark";

/**
 * Landing page.
 *
 * Presented as a document rather than a marketing page: paper ground, hairline
 * rules, mono figures with tabular numerals, and severity carried on a left
 * edge. No gradient washes, no drifting blur, no dot grid — the decoration a
 * bank audience reads as noise.
 *
 * The four figures below are guarantees, not traction metrics. Each one is
 * verifiable in the codebase:
 *
 * - 0 auto-approvals — `route_risk()` has no auto-approve outcome; every route
 *   terminates at a named human action.
 * - 3 rounds — `MAX_DEBATE_ROUNDS` in the shared contracts package.
 * - 5 references — document, page, field, rule ID, rule-pack version.
 * - 4 rungs — `LADDER_RUNG_ORDER` in `identity_ladder.py`.
 *
 * They are set as static figures. Counting up to a single digit trivialises a
 * number that is meant to read as a commitment.
 */

const STATS = [
  {
    figure: "0",
    label: "Automatic approvals",
    hint: "No case clears on its own. Every route ends at a named officer.",
  },
  {
    figure: "3",
    unit: "max",
    label: "Review rounds",
    hint: "Checks stop after three passes. Anything unresolved comes to your desk.",
  },
  {
    figure: "5",
    unit: "refs",
    label: "Evidence per finding",
    hint: "Document, page, field, rule ID and rule-pack version on every result.",
  },
  {
    figure: "4",
    unit: "rungs",
    label: "Identity ladder",
    hint: "A similar name is a lead. Only a matched legal-entity ID is proof.",
  },
] as const;

/**
 * GIFT IFSC context figures.
 *
 * Every number here is published and attributed on the page itself, with the
 * period it refers to. That is deliberate: this is a product about evidence
 * provenance, so an unsourced statistic on its own landing page would
 * contradict the thing being sold. Figures corroborated across IFSCA-derived
 * reporting (CII, December 2025) and the HSBC–EY GIFT IFSC compendium
 * unveiled 5 December 2025.
 *
 * Do not add a figure here without a source and a date.
 */
const NEED_FIGURES = [
  {
    figure: "USD 106 bn",
    label: "Banking assets at GIFT IFSC",
    detail: "Up from USD 14 bn in September 2020.",
    period: "December 2025",
  },
  {
    figure: "7.5×",
    label: "Growth in five years",
    detail: "Driven primarily by external commercial borrowings and trade finance.",
    period: "Sept 2020 — Dec 2025",
  },
  {
    figure: "37",
    label: "Banks operating in GIFT IFSC",
    detail: "Including 20 foreign banks — 37 separate examination desks.",
    period: "December 2025",
  },
  {
    figure: "1,200+",
    label: "IFSCA registrations granted",
    detail: "Across more than 30 business segments in five years.",
    period: "to December 2025",
  },
] as const;

const PILLARS = [
  {
    title: "Documents read with challenge built in",
    body: "Fields are pulled from the packet, checked again, and challenged when something looks off. If checks disagree, the case is flagged for you — values are never silently averaged.",
  },
  {
    title: "Counterparty identity, step by step",
    body: "A similar name is only a lead. A matching Legal Entity Identifier on the document is stronger. Verifiable role credentials (vLEI) are separate. Fuzzy name match is never identity proof.",
  },
  {
    title: "Maker–checker ready handoff",
    body: "Download an examiner pack with evidence for dual control. This is decision support for Trade Finance Ops — not an AI approval stamp.",
  },
] as const;

const NEVER_CLAIMS = [
  "What is physically inside a container",
  "Customs clearance or government filing on your behalf",
  "That software approved, rejected, or confirmed a sanctions hit without your review",
] as const;

export default function LandingPage() {
  const reduce = useReducedMotion();

  /** One restrained reveal, reused. Not a per-element stagger. */
  const reveal = (delay = 0) =>
    reduce
      ? {}
      : {
          initial: { opacity: 0, y: 8 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.42, delay, ease: [0.2, 0, 0, 1] as const },
        };

  return (
    <main className="bg-[var(--tp-bg)]">
      {/* ---------------------------------------------------------------- Hero */}
      <section className="border-b border-[var(--tp-line)]">
        <div className="mx-auto flex min-h-[76svh] max-w-6xl flex-col justify-center px-4 py-24 sm:px-6">
          <motion.div {...reveal()}>
            {/*
              One left axis for the whole hero. The mark is not repeated here —
              the nav carries it a few pixels above, and indenting the wordmark
              past a second copy broke the alignment of everything beneath it.
            */}
            <div>
              <p className="tp-label text-[var(--tp-brand-orange)]">
                For bank &amp; GIFT IFSC trade desks
              </p>
              <h1 className="mt-2.5 font-display text-4xl font-semibold tracking-tight text-[var(--tp-navy)] sm:text-5xl">
                TradePulse
              </h1>
            </div>
          </motion.div>

          <motion.p
            className="mt-10 max-w-3xl text-2xl font-semibold leading-[1.25] tracking-tight text-[var(--tp-ink)] sm:text-3xl"
            {...reveal(0.06)}
          >
            Documentary trade review support — your officers decide, not the software.
          </motion.p>

          {/* Body sits in a measured column against a rule, like a form note. */}
          <motion.p
            className="mt-7 max-w-xl border-l-2 border-[var(--tp-line)] pl-5 text-base leading-relaxed text-[var(--tp-muted)]"
            {...reveal(0.12)}
          >
            Built for Trade Finance Operations and compliance officers: turn invoice and transport
            packs into one evidence-backed case, check counterparty identity carefully, and hand off
            a clear pack for maker–checker. Missing information stays open — it is never treated as a
            pass.
          </motion.p>

          <motion.div className="mt-9 flex flex-wrap items-center gap-3" {...reveal(0.18)}>
            <Link href="/workbench" className="tp-btn-primary px-5 py-3 text-base">
              Open review desk
            </Link>
            <Link href="/workbench/cases/new" className="tp-btn-secondary px-5 py-3 text-base">
              Start a new case
            </Link>
          </motion.div>

          {/* Fine print stays quiet — uppercase would make a caveat shout. */}
          <motion.p className="mt-8 text-xs text-[var(--tp-muted)]" {...reveal(0.22)}>
            Prototype environment · Sample documents are clearly labelled as demo data
          </motion.p>
        </div>
      </section>

      {/* ------------------------------------------------- Guarantees / figures */}
      <section className="border-b border-[var(--tp-line)] bg-[var(--tp-surface)]">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            {STATS.map((s, i) => (
              <div
                key={s.label}
                className={[
                  "flex flex-col py-9",
                  // Hairline rules between columns rather than four boxes.
                  "border-t border-[var(--tp-line)] sm:border-t-0",
                  i === 0 ? "" : "sm:border-l sm:border-[var(--tp-line)]",
                  i === 0 ? "pr-6" : "px-6",
                  i > 1 ? "lg:border-t-0" : "",
                  i === 2 ? "sm:border-l-0 lg:border-l" : "",
                ].join(" ")}
              >
                <p className="font-display text-5xl font-medium leading-none text-[var(--tp-navy)]">
                  {s.figure}
                  {"unit" in s && s.unit ? (
                    <span className="ml-1.5 align-baseline text-base font-normal text-[var(--tp-muted)]">
                      {s.unit}
                    </span>
                  ) : null}
                </p>
                <p className="tp-label mt-4 text-[var(--tp-ink)]">{s.label}</p>
                <p className="mt-2 max-w-[26ch] text-sm leading-snug text-[var(--tp-muted)]">
                  {s.hint}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* --------------------------------------------------- Why it is needed */}
      <section id="why-tradepulse" className="border-b border-[var(--tp-line)]">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <div className="max-w-2xl">
            <p className="tp-label text-[var(--tp-brand-orange)]">The need</p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-[var(--tp-navy)]">
              GIFT IFSC is growing faster than the desks that check its paperwork
            </h2>
            <p className="mt-4 leading-relaxed text-[var(--tp-muted)]">
              Trade finance is one of the two named engines behind the centre&rsquo;s expansion. Every
              transaction it represents arrives as a packet of documents that a person has to read,
              cross-check and defend. Capacity has multiplied. Examination has not.
            </p>
          </div>

          {/* Figures carry their own provenance — the product's own argument. */}
          <dl className="mt-14 grid gap-px border border-[var(--tp-line)] bg-[var(--tp-line)] sm:grid-cols-2">
            {NEED_FIGURES.map((f) => (
              <div key={f.label} className="bg-[var(--tp-surface)] p-7">
                <dt className="tp-label text-[var(--tp-muted)]">{f.label}</dt>
                <dd>
                  <p className="mt-3 font-display text-4xl font-medium leading-none text-[var(--tp-brand-blue)]">
                    {f.figure}
                  </p>
                  <p className="mt-3 text-sm leading-relaxed text-[var(--tp-ink)]">{f.detail}</p>
                  <p className="mt-3 font-mono text-xs text-[var(--tp-muted)]">{f.period}</p>
                </dd>
              </div>
            ))}
          </dl>

          <div className="mt-8 flex flex-col gap-4 border-l-2 border-[var(--tp-brand-orange)] pl-5 sm:flex-row sm:items-baseline sm:justify-between">
            <p className="max-w-2xl text-base leading-relaxed text-[var(--tp-ink)]">
              Thirty-seven banks, twenty of them foreign, each examining cross-border document packets
              against its own house standard. That is where discrepancies survive — not in the rules,
              but in the reading.
            </p>
            <p className="shrink-0 text-xs leading-relaxed text-[var(--tp-muted)] sm:text-right">
              Sources: IFSCA-reported figures via CII;
              <br className="hidden sm:block" /> HSBC–EY GIFT IFSC compendium, 5 December 2025.
            </p>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------- How it works */}
      <section id="how-it-works">
        <div className="mx-auto max-w-6xl space-y-20 px-4 py-24 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold tracking-tight text-[var(--tp-navy)]">
              Built for the desk that has to defend the decision
            </h2>
            <p className="mt-4 leading-relaxed text-[var(--tp-muted)]">
              Manual packs miss quantity mismatches and unclear counterparties. Tools that
              over-promise create audit risk. TradePulse keeps exceptions visible and decisions with
              your desk.
            </p>
          </div>

          {/* Rules, not cards. Each column opens under a heavy ink rule. */}
          <div className="grid gap-10 md:grid-cols-3 md:gap-8">
            {PILLARS.map((p) => (
              <article key={p.title} className="border-t-2 border-[var(--tp-ink)] pt-5">
                <h3 className="font-display text-lg font-semibold leading-snug text-[var(--tp-navy)]">
                  {p.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-[var(--tp-muted)]">{p.body}</p>
              </article>
            ))}
          </div>

          {/* The strongest content on the page — given weight and a stamp rule. */}
          <div>
            <h2 className="font-display text-3xl font-semibold tracking-tight text-[var(--tp-navy)]">
              What TradePulse never claims
            </h2>
            <ul className="mt-6 max-w-3xl">
              {NEVER_CLAIMS.map((claim) => (
                <li
                  key={claim}
                  className="border-l-2 border-[var(--tp-danger)] py-2.5 pl-5 text-[var(--tp-ink)]"
                >
                  {claim}
                </li>
              ))}
            </ul>
          </div>

          <div className="flex flex-wrap items-center gap-5 border border-[var(--tp-line)] bg-[var(--tp-surface)] p-7 sm:p-9">
            <BrandMark className="h-12 w-12 shrink-0" />
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--tp-navy)]">
                Open the review desk
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--tp-muted)]">
                Work the case queue, choose a labelled demo packet or upload your own invoice and Bill
                of Lading, then review identity and findings before maker–checker action.
              </p>
            </div>
            <Link href="/workbench" className="tp-btn-primary shrink-0">
              Open review desk
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-[var(--tp-line)] px-4 py-9 text-center text-sm text-[var(--tp-muted)]">
        TradePulse · Documentary trade review support for bank and GIFT IFSC officers · Prototype
      </footer>
    </main>
  );
}
