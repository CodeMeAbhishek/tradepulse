"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useDemo } from "@/lib/demo/DemoProvider";
import { RiskChip, WorkflowChip } from "@/components/ui/StatusChips";
import { profileLabel } from "@/lib/demo/store";
import { cn } from "@/lib/cn";

type RouteFilter = "ALL" | "MAKER" | "CHECKER" | "SCRUTINY";

export default function QueuePage() {
  const { cases, ready } = useDemo();
  const [q, setQ] = useState("");
  const [route, setRoute] = useState<RouteFilter>("ALL");

  const filtered = useMemo(() => {
    let list = cases;
    if (route === "MAKER") list = list.filter((c) => c.workflow === "PENDING_MAKER");
    if (route === "CHECKER") list = list.filter((c) => c.workflow === "MAKER_APPROVED");
    if (route === "SCRUTINY") {
      list = list.filter(
        (c) =>
          c.riskRoute === "MAKER_REVIEW_REQUIRED" ||
          c.riskRoute === "REVIEW_REQUIRED" ||
          c.riskRoute === "HIGH_RISK_ESCALATION",
      );
    }
    const needle = q.trim().toLowerCase();
    if (!needle) return list;
    return list.filter(
      (c) =>
        c.reference.toLowerCase().includes(needle) ||
        c.counterparty.toLowerCase().includes(needle) ||
        c.corridor.toLowerCase().includes(needle),
    );
  }, [cases, q, route]);

  if (!ready) return <p className="text-sm text-[var(--tp-muted)]">Loading queue…</p>;

  const filters: { id: RouteFilter; label: string }[] = [
    { id: "ALL", label: "All" },
    { id: "MAKER", label: "Awaiting maker" },
    { id: "CHECKER", label: "Checker inbox" },
    { id: "SCRUTINY", label: "Needs scrutiny" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
            Compliance queue
          </h1>
          <p className="mt-1 text-sm text-[var(--tp-muted)]">
            Triage documentary cases. Status text is always shown — color alone is never the meaning
            channel.
          </p>
        </div>
        <Link href="/workbench/cases/new" className="tp-btn-primary">
          New case
        </Link>
      </div>

      <div className="flex flex-wrap gap-2" role="group" aria-label="Queue triage filters">
        {filters.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setRoute(f.id)}
            className={cn(
              "cursor-pointer rounded-md px-3 py-1.5 text-sm font-medium transition duration-200",
              route === f.id
                ? "bg-[var(--tp-navy)] text-white"
                : "border border-[var(--tp-line)] bg-white text-[var(--tp-muted)] hover:bg-slate-50",
            )}
            aria-pressed={route === f.id}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="tp-card p-3">
        <label className="block text-xs font-medium text-[var(--tp-muted)]">
          Search reference, counterparty, corridor
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2 text-sm outline-none focus:border-[var(--tp-accent)]"
            placeholder="e.g. TP-2026 or Sahara"
          />
        </label>
      </div>

      <div className="tp-card overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-[var(--tp-muted)]">
            <tr>
              <th className="px-3 py-2.5 font-medium">Case</th>
              <th className="px-3 py-2.5 font-medium">Profile</th>
              <th className="px-3 py-2.5 font-medium">Risk route</th>
              <th className="px-3 py-2.5 font-medium">Workflow</th>
              <th className="px-3 py-2.5 font-medium">Amount</th>
              <th className="px-3 py-2.5 font-medium">SLA</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id} className="border-t border-[var(--tp-line)] hover:bg-slate-50/80">
                <td className="px-3 py-3 align-top">
                  <Link
                    href={`/workbench/cases/${c.id}`}
                    className="font-medium text-[var(--tp-accent)]"
                  >
                    {c.reference}
                  </Link>
                  <p
                    className="mt-0.5 max-w-[16rem] truncate text-[var(--tp-ink)]"
                    title={c.counterparty}
                  >
                    {c.counterparty}
                  </p>
                  <p className="font-mono text-[11px] text-[var(--tp-muted)]">{c.corridor}</p>
                </td>
                <td className="px-3 py-3 align-top text-[var(--tp-muted)]">
                  {profileLabel(c.profile)}
                </td>
                <td className="px-3 py-3 align-top">
                  <RiskChip route={c.riskRoute} />
                </td>
                <td className="px-3 py-3 align-top">
                  <WorkflowChip state={c.workflow} />
                </td>
                <td className="px-3 py-3 align-top font-mono text-xs">
                  {c.currency} {c.amount}
                </td>
                <td className="px-3 py-3 align-top text-[var(--tp-muted)]">{c.slaLabel}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-[var(--tp-muted)]">No cases match.</p>
        ) : null}
      </div>
    </div>
  );
}
