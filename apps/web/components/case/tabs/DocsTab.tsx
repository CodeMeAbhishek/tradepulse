"use client";

import { policyLabel } from "@/lib/status-labels";
import { useCase } from "@/components/case/CaseContext";

export function DocsTab() {
  const { live } = useCase();
  if (!live) return null;

  return (
    <section className="tp-card overflow-hidden">
      <div className="border-b border-[var(--tp-line)] px-4 py-3">
        <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Document checklist</h2>
        <p className="mt-1 text-xs text-[var(--tp-muted)]">
          Required items block completeness when missing. Optional items never block a case.
        </p>
      </div>
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-[var(--tp-muted)]">
          <tr>
            <th className="px-3 py-2 text-left">Document</th>
            <th className="px-3 py-2 text-left">Requirement</th>
            <th className="px-3 py-2 text-left">Provided</th>
            <th className="px-3 py-2 text-left">Blocks if missing</th>
          </tr>
        </thead>
        <tbody>
          {live.docs.map((d) => (
            <tr key={d.type} className="border-t border-[var(--tp-line)]">
              <td className="px-3 py-2.5 font-medium capitalize">{d.label}</td>
              <td className="px-3 py-2.5">{policyLabel(d.policy)}</td>
              <td className="px-3 py-2.5">{d.provided ? "Yes" : "No"}</td>
              <td className="px-3 py-2.5">{d.blocker ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
