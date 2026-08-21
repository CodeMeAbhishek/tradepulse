"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";

export default function LandingPage() {
  const reduce = useReducedMotion();
  const fade = reduce
    ? {}
    : {
        initial: { opacity: 0, y: 14 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as const },
      };
  const fadeDelay = (delay: number) =>
    reduce
      ? {}
      : {
          initial: { opacity: 0, y: 12 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] as const },
        };

  return (
    <main>
      {/* Hero — brand first, one composition, light full-bleed atmosphere */}
      <section className="relative min-h-[100svh] overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "linear-gradient(135deg, #f8fafc 0%, #eef4f8 42%, #e6f0ef 100%)",
          }}
        />
        <div
          aria-hidden
          className={
            reduce
              ? "pointer-events-none absolute inset-0 opacity-40"
              : "pointer-events-none absolute inset-0 opacity-40 [background-image:radial-gradient(circle_at_1px_1px,rgba(12,35,64,0.07)_1px,transparent_0)] [background-size:28px_28px]"
          }
        />
        {!reduce ? (
          <motion.div
            aria-hidden
            className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-teal-200/35 blur-3xl"
            animate={{ x: [0, 24, 0], y: [0, 12, 0] }}
            transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          />
        ) : null}

        <div className="relative z-10 mx-auto flex min-h-[100svh] max-w-6xl flex-col justify-center px-4 pb-16 pt-28 sm:px-6">
          <motion.p
            className="font-display text-5xl font-semibold tracking-tight text-[var(--tp-navy)] sm:text-6xl md:text-7xl"
            {...fade}
          >
            TradePulse
          </motion.p>
          <motion.h1
            className="mt-5 max-w-2xl text-2xl font-semibold leading-snug text-[var(--tp-ink)] sm:text-3xl"
            {...fadeDelay(0.08)}
          >
            Scattered trade documents, one evidence-backed case file.
          </motion.h1>
          <motion.p
            className="mt-4 max-w-xl text-base leading-relaxed text-[var(--tp-muted)] sm:text-lg"
            {...fadeDelay(0.16)}
          >
            Make the digital evidence around a shipment complete, consistent, and actionable—so the
            right human can decide faster. We never claim to know what is inside a container.
          </motion.p>
          <motion.div className="mt-8 flex flex-wrap gap-3" {...fadeDelay(0.24)}>
            <Link href="/workbench" className="tp-btn-primary">
              Enter workbench
            </Link>
            <a href="#how-it-works" className="tp-btn-secondary">
              How it works
            </a>
          </motion.div>
        </div>
      </section>

      <section id="how-it-works" className="border-t border-[var(--tp-line)] bg-[var(--tp-elevated)]">
        <div className="mx-auto max-w-6xl space-y-16 px-4 py-20 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              The problem officers face
            </h2>
            <p className="mt-3 text-[var(--tp-muted)] leading-relaxed">
              Manual packs miss quantity mismatches, identity ambiguity, and price outliers. Audit
              trails scatter across inboxes. Reviewers need evidence in one place—not another black
              box.
            </p>
          </div>

          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              What TradePulse does
            </h2>
            <p className="mt-3 text-[var(--tp-muted)] leading-relaxed">
              Extract → validate → reconcile across invoice and bill of lading → anchor party
              identity (LEI / vLEI evidence) → screen configured lists → check price plausibility →
              route a human maker and checker. Agent consensus is an extraction signal only—never a
              legal or sanctions conclusion.
            </p>
          </div>

          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              What it never claims
            </h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-[var(--tp-muted)]">
              <li>Physical goods inside a container</li>
              <li>Customs clearance or ICEGATE filing</li>
              <li>AI approval, rejection, or confirmed sanctions match without authoritative evidence</li>
            </ul>
          </div>

          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              Demo path
            </h2>
            <p className="mt-3 text-[var(--tp-muted)] leading-relaxed">
              Enter the workbench, seed sample cases (or upload a packet), open a quantity-mismatch
              case, and use Investigate to see evidence side by side—then Decide with dual control.
            </p>
            <Link href="/workbench" className="tp-btn-primary mt-6">
              Open officer workbench
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-[var(--tp-line)] px-4 py-8 text-center text-sm text-[var(--tp-muted)]">
        TradePulse · Documentary trade-compliance decision support · GIFT IFSC prototype
      </footer>
    </main>
  );
}
