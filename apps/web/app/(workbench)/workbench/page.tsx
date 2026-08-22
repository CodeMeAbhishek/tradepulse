"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import { useDemo } from "@/lib/demo/DemoProvider";
import { RiskChip, WorkflowChip } from "@/components/ui/StatusChips";
import { profileLabel } from "@/lib/demo/store";
import { useCountUp } from "@/lib/useCountUp";

export default function OverviewPage() {
  const { cases, ready, mode, seedSamples, apiOnline, error } = useDemo();
  const reduce = useReducedMotion();
  const [seeding, setSeeding] = useState(false);
  const autoSeedTried = useRef(false);

  // Prototype API is in-memory: after redeploy the queue is empty. Auto-load a
  // varied sample desk once so the overview is never a barren zero state.
  useEffect(() => {
    if (!ready || mode !== "api" || apiOnline === false || cases.length > 0) return;
    if (autoSeedTried.current || seeding) return;
    autoSeedTried.current = true;
    setSeeding(true);
    void seedSamples()
      .catch(() => {
        /* empty state CTA remains available */
      })
      .finally(() => setSeeding(false));
  }, [ready, mode, apiOnline, cases.length, seedSamples, seeding]);

  if (!ready) return <p className="text-sm text-[var(--tp-muted)]">Loading your review desk…</p>;

  const pending = cases.filter((c) => c.workflow === "PENDING_MAKER").length;
  const checker = cases.filter((c) => c.workflow === "MAKER_APPROVED").length;
  const review = cases.filter(
    (c) =>
      c.riskRoute === "MAKER_REVIEW_REQUIRED" ||
      c.riskRoute === "REVIEW_REQUIRED" ||
      c.riskRoute === "HIGH_RISK_ESCALATION",
  ).length;
  const attention = [...cases].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 5);

  const runSeed = () => {
    setSeeding(true);
    void seedSamples().finally(() => setSeeding(false));
  };

  return (
    <motion.div
      className="space-y-6"
      initial={reduce ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <section className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-[var(--tp-navy)]">
            Desk overview
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-[var(--tp-muted)]">
            {mode === "api"
              ? "Cases ready for documentary review. Check the evidence, then act as maker or checker — TradePulse does not approve for you."
              : "Working with local demo cases. Connect to the review service to use shared cases."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {mode === "api" ? (
            <button
              type="button"
              onClick={runSeed}
              className="tp-btn-secondary"
              disabled={apiOnline === false || seeding}
            >
              {seeding ? "Loading sample desk…" : "Load sample cases"}
            </button>
          ) : null}
          <Link href="/workbench/cases/new" className="tp-btn-primary">
            Open new case
          </Link>
        </div>
      </section>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          Cannot reach the review service. Try Refresh. If the problem continues, contact your
          platform team.
        </div>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Awaiting maker", value: pending, href: "/workbench/queue" },
          { label: "Checker inbox", value: checker, href: "/workbench/approvals" },
          { label: "Needs scrutiny", value: review, href: "/workbench/queue" },
        ].map((k, i) => (
          <StatTile key={k.label} label={k.label} value={k.value} href={k.href} index={i} />
        ))}
      </section>

      <section className="tp-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-[var(--tp-line)] px-4 py-3">
          <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Needs attention</h2>
          <Link href="/workbench/queue" className="text-sm font-medium text-[var(--tp-accent)]">
            View full queue →
          </Link>
        </div>
        {attention.length === 0 ? (
          <div className="px-4 py-10 text-center">
            <p className="text-base font-semibold text-[var(--tp-navy)]">
              {seeding ? "Preparing a sample review desk…" : "No cases on this desk yet"}
            </p>
            <p className="mx-auto mt-2 max-w-md text-sm text-[var(--tp-muted)]">
              {seeding
                ? "Loading varied demo packets (different counterparties, corridors, and review profiles)."
                : "The live demo store resets when the review service restarts. Load sample cases to populate a working queue, or open a new case."}
            </p>
            {!seeding && mode === "api" ? (
              <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={runSeed}
                  className="tp-btn-primary"
                  disabled={apiOnline === false}
                >
                  Load sample cases
                </button>
                <Link href="/workbench/cases/new" className="tp-btn-secondary">
                  Open new case
                </Link>
              </div>
            ) : null}
          </div>
        ) : (
          <ul className="divide-y divide-[var(--tp-line)]">
            {attention.map((c, i) => (
              <li key={c.id} className="tp-reveal" style={{ "--i": i } as React.CSSProperties}>
                <Link
                  href={`/workbench/cases/${c.id}`}
                  className="tp-row flex flex-wrap items-center justify-between gap-3 px-4 py-3 hover:bg-[var(--tp-bg)]"
                >
                  <div className="min-w-0">
                    <p className="font-medium text-[var(--tp-navy)]">{c.reference}</p>
                    <p className="truncate text-sm text-[var(--tp-muted)]">
                      {c.counterparty} · {c.corridor} · {profileLabel(c.profile)}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <RiskChip route={c.riskRoute} />
                    <WorkflowChip state={c.workflow} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </motion.div>
  );
}

/**
 * A count-up tile. The number settles rather than snapping, so a queue filling
 * in reads as data arriving. The value shown is always the exact figure.
 */
function StatTile({
  label,
  value,
  href,
  index,
}: {
  label: string;
  value: number;
  href: string;
  index: number;
}) {
  const shown = useCountUp(value);
  return (
    <Link
      href={href}
      className="tp-card tp-reveal p-4 hover:border-slate-400"
      style={{ "--i": index } as React.CSSProperties}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--tp-muted)]">{label}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums text-[var(--tp-navy)]">{shown}</p>
    </Link>
  );
}
