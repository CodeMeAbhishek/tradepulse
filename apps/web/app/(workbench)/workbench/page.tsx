"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "motion/react";
import { useDemo } from "@/lib/demo/DemoProvider";
import { RiskChip, WorkflowChip } from "@/components/ui/StatusChips";
import { profileLabel } from "@/lib/demo/store";

export default function OverviewPage() {
  const { cases, ready, mode, seedSamples, apiOnline, error } = useDemo();
  const reduce = useReducedMotion();
  if (!ready) return <p className="text-sm text-[var(--tp-muted)]">Loading workbench…</p>;

  const pending = cases.filter((c) => c.workflow === "PENDING_MAKER").length;
  const checker = cases.filter((c) => c.workflow === "MAKER_APPROVED").length;
  const review = cases.filter(
    (c) =>
      c.riskRoute === "MAKER_REVIEW_REQUIRED" ||
      c.riskRoute === "REVIEW_REQUIRED" ||
      c.riskRoute === "HIGH_RISK_ESCALATION",
  ).length;
  const attention = [...cases].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 4);

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
            Compliance overview
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-[var(--tp-muted)]">
            {mode === "api"
              ? "Live cases from the API. Review evidence, then act as maker or checker—TradePulse does not approve for you."
              : "Local demo store. Set NEXT_PUBLIC_DATA_MODE=api to use the live backend."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {mode === "api" && cases.length === 0 ? (
            <button
              type="button"
              onClick={() => void seedSamples()}
              className="tp-btn-secondary"
              disabled={apiOnline === false}
            >
              Seed sample cases
            </button>
          ) : null}
          <Link href="/workbench/cases/new" className="tp-btn-primary">
            Open new case
          </Link>
        </div>
      </section>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          Cannot reach API. Run uvicorn on port 8000, then Refresh.
        </div>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        {[
          { label: "Awaiting maker", value: pending, href: "/workbench/queue" },
          { label: "Checker inbox", value: checker, href: "/workbench/approvals" },
          { label: "Needs scrutiny", value: review, href: "/workbench/queue" },
        ].map((k) => (
          <Link
            key={k.label}
            href={k.href}
            className="tp-card p-4 transition duration-200 hover:border-slate-400"
          >
            <p className="text-xs font-medium uppercase tracking-wide text-[var(--tp-muted)]">
              {k.label}
            </p>
            <p className="mt-2 text-3xl font-semibold text-[var(--tp-navy)]">{k.value}</p>
          </Link>
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
          <p className="px-4 py-8 text-center text-sm text-[var(--tp-muted)]">
            No cases yet. Create one or seed API samples.
          </p>
        ) : (
          <ul className="divide-y divide-[var(--tp-line)]">
            {attention.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/workbench/cases/${c.id}`}
                  className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 transition hover:bg-slate-50"
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
