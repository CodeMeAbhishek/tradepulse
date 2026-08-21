"use client";

import Link from "next/link";
import { useDemo } from "@/lib/demo/DemoProvider";
import { RiskChip, WorkflowChip } from "@/components/ui/StatusChips";

export default function ApprovalsPage() {
  const { cases, ready } = useDemo();
  if (!ready) return <p className="text-sm text-[var(--tp-muted)]">Loading…</p>;

  const inbox = cases.filter((c) => c.workflow === "MAKER_APPROVED");
  const decided = cases.filter(
    (c) => c.workflow === "CHECKER_APPROVED" || c.workflow === "CHECKER_REJECTED",
  );

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold text-[var(--tp-navy)]">Approvals inbox</h1>
        <p className="mt-1 text-sm text-[var(--tp-muted)]">
          Checker queue — dual control. Items appear only after maker submission (
          <a
            className="text-[var(--tp-accent)] underline"
            href="https://www.opcito.com/blogs/maker-checker-implementation-guide-for-secure-fintech-systems"
            target="_blank"
            rel="noreferrer"
          >
            maker-checker pattern
          </a>
          ).
        </p>
      </div>

      <section className="tp-card overflow-hidden">
        <div className="border-b border-[var(--tp-line)] px-4 py-3 text-sm font-semibold">
          Pending checker ({inbox.length})
        </div>
        {inbox.length === 0 ? (
          <p className="px-4 py-8 text-center text-sm text-[var(--tp-muted)]">
            No items. Open a case and use Maker: submit to checker.
          </p>
        ) : (
          <ul className="divide-y divide-[var(--tp-line)]">
            {inbox.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/cases/${c.id}`}
                  className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 hover:bg-slate-50"
                >
                  <div>
                    <p className="font-medium text-[var(--tp-navy)]">{c.reference}</p>
                    <p className="text-sm text-[var(--tp-muted)]">
                      {c.counterparty} · Maker note: {c.makerNote || "—"}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <RiskChip route={c.riskRoute} />
                    <WorkflowChip state={c.workflow} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="tp-card overflow-hidden">
        <div className="border-b border-[var(--tp-line)] px-4 py-3 text-sm font-semibold">
          Recent checker decisions
        </div>
        {decided.length === 0 ? (
          <p className="px-4 py-6 text-sm text-[var(--tp-muted)]">No checker decisions yet.</p>
        ) : (
          <ul className="divide-y divide-[var(--tp-line)]">
            {decided.map((c) => (
              <li key={c.id} className="flex flex-wrap justify-between gap-2 px-4 py-3 text-sm">
                <Link href={`/cases/${c.id}`} className="font-medium text-[var(--tp-accent)]">
                  {c.reference}
                </Link>
                <WorkflowChip state={c.workflow} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
