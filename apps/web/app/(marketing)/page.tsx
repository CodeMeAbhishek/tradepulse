"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { BrandMark } from "@/components/BrandMark";
import { useCountUp } from "@/lib/useCountUp";

const STATS = [
  { label: "Agent debate cap", value: 3, suffix: " rounds", hint: "Bounded swarm — never endless LLM loops" },
  { label: "Identity ladder", value: 4, suffix: " states", hint: "Candidate → LEI → vLEI → unresolved" },
  { label: "Kernel docs", value: 2, suffix: "+", hint: "Invoice required; BoL for post-shipment" },
  { label: "AWS region", value: 1, suffix: " live", hint: "ap-south-1 ECS Fargate demo" },
] as const;

const PILLARS = [
  {
    title: "Bounded agentic extraction",
    body: "Extract → validate → challenge → arbitrate. Max three rounds. Disagreements surface as REVIEW_REQUIRED — never averaged away.",
  },
  {
    title: "Identity confidence ladder",
    body: "GLEIF name hits are candidates. Document LEI is stronger. vLEI is separate evidence. Fuzzy match is never identity proof.",
  },
  {
    title: "Examiner case pack",
    body: "Maker–checker handoff with evidence, not an AI approval badge. Decision support for Head of Trade Finance Ops.",
  },
] as const;

function StatCard({
  label,
  value,
  suffix,
  hint,
  delay,
}: {
  label: string;
  value: number;
  suffix: string;
  hint: string;
  delay: number;
}) {
  const reduce = useReducedMotion();
  const n = useCountUp(value, reduce ? 1 : 900 + delay * 120);
  return (
    <div className="rounded-xl border border-[var(--tp-line)] bg-[var(--tp-elevated)]/90 p-4 shadow-sm">
      <p className="tp-label text-[var(--tp-muted)]">{label}</p>
      <p className="mt-2 font-display text-3xl font-semibold text-[var(--tp-brand-blue)]">
        {n}
        <span className="text-lg font-medium text-[var(--tp-muted)]">{suffix}</span>
      </p>
      <p className="mt-1 text-xs leading-snug text-[var(--tp-muted)]">{hint}</p>
    </div>
  );
}

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
      <section className="relative min-h-[100svh] overflow-hidden">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 70% 10%, rgba(233,99,29,0.12), transparent 55%), radial-gradient(ellipse 70% 50% at 15% 80%, rgba(27,79,158,0.14), transparent 50%), linear-gradient(160deg, #f8fafc 0%, #eef3f8 45%, #f4f2ed 100%)",
          }}
        />
        <div
          aria-hidden
          className={
            reduce
              ? "pointer-events-none absolute inset-0 opacity-30"
              : "pointer-events-none absolute inset-0 opacity-35 [background-image:radial-gradient(circle_at_1px_1px,rgba(27,79,158,0.09)_1px,transparent_0)] [background-size:26px_26px]"
          }
        />
        {!reduce ? (
          <motion.div
            aria-hidden
            className="pointer-events-none absolute -right-16 top-28 h-80 w-80 rounded-full bg-[rgba(233,99,29,0.18)] blur-3xl"
            animate={{ x: [0, -18, 0], y: [0, 14, 0] }}
            transition={{ duration: 16, repeat: Infinity, ease: "easeInOut" }}
          />
        ) : null}

        <div className="relative z-10 mx-auto flex min-h-[100svh] max-w-6xl flex-col justify-center px-4 pb-16 pt-28 sm:px-6">
          <motion.div className="flex items-center gap-4" {...fade}>
            <BrandMark className="h-16 w-16 sm:h-20 sm:w-20" />
            <div>
              <p className="tp-label text-[var(--tp-brand-orange)]">GIFT IFSC · Track 1 Agentic AI</p>
              <h1 className="font-display text-4xl font-semibold tracking-tight text-[var(--tp-navy)] sm:text-5xl md:text-6xl">
                TradePulse
              </h1>
            </div>
          </motion.div>
          <motion.p
            className="mt-6 max-w-2xl text-xl font-semibold leading-snug text-[var(--tp-ink)] sm:text-2xl"
            {...fadeDelay(0.08)}
          >
            Documentary trade-compliance decision support — not autopilot approval.
          </motion.p>
          <motion.p
            className="mt-4 max-w-xl text-base leading-relaxed text-[var(--tp-muted)] sm:text-lg"
            {...fadeDelay(0.16)}
          >
            For the Head of Trade Finance Ops at a GIFT City IBU: turn invoice and transport packs
            into one evidence-backed case, with an identity ladder and examiner handoff. Humans
            decide. Missing data never becomes PASS.
          </motion.p>
          <motion.div className="mt-8 flex flex-wrap gap-3" {...fadeDelay(0.24)}>
            <Link href="/workbench" className="tp-btn-primary px-5 py-3 text-base">
              Enter workbench
            </Link>
            <Link href="/workbench/cases/new" className="tp-btn-secondary px-5 py-3 text-base">
              New case with samples
            </Link>
          </motion.div>
          <motion.p className="mt-4 text-xs text-[var(--tp-muted)]" {...fadeDelay(0.3)}>
            Prototype · SYNTHETIC_DEMO fixtures labelled · Live on AWS ap-south-1
          </motion.p>
        </div>
      </section>

      <section className="border-t border-[var(--tp-line)] bg-[var(--tp-elevated)]">
        <div className="mx-auto grid max-w-6xl gap-4 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4">
          {STATS.map((s, i) => (
            <StatCard key={s.label} {...s} delay={i} />
          ))}
        </div>
      </section>

      <section id="how-it-works" className="border-t border-[var(--tp-line)]">
        <div className="mx-auto max-w-6xl space-y-14 px-4 py-20 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              Built for examiners, not black boxes
            </h2>
            <p className="mt-3 text-[var(--tp-muted)] leading-relaxed">
              Manual packs miss quantity mismatches and identity ambiguity. Commodity AI checkers
              overclaim. TradePulse keeps failure modes honest and audit-ready.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {PILLARS.map((p) => (
              <article
                key={p.title}
                className="rounded-xl border border-[var(--tp-line)] bg-[var(--tp-elevated)] p-5"
              >
                <div
                  className="mb-3 h-1 w-10 rounded-full"
                  style={{ background: "linear-gradient(90deg, #1B4F9E, #E9631D)" }}
                />
                <h3 className="font-display text-lg font-semibold text-[var(--tp-navy)]">{p.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[var(--tp-muted)]">{p.body}</p>
              </article>
            ))}
          </div>

          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
              What it never claims
            </h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-[var(--tp-muted)]">
              <li>Physical goods inside a container</li>
              <li>Customs clearance or ICEGATE filing</li>
              <li>AI approval, rejection, or confirmed sanctions without authoritative evidence</li>
            </ul>
          </div>

          <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-[var(--tp-line)] bg-[var(--tp-bg)] p-6 sm:p-8">
            <BrandMark className="h-14 w-14" />
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-2xl font-semibold text-[var(--tp-navy)]">
                Try the officer workbench
              </h2>
              <p className="mt-1 text-sm text-[var(--tp-muted)]">
                Open the queue, pick a labeled sample pack from the cloud library, or upload your own
                invoice / BoL — then review the identity ladder and examiner pack.
              </p>
            </div>
            <Link href="/workbench" className="tp-btn-primary shrink-0">
              Enter workbench
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
