"use client";

import { statusLabel } from "@/lib/status-labels";
import { MismatchFlag, ToneChip } from "@/components/ui/StatusChips";
import { useCase } from "@/components/case/CaseContext";

export function CompareTab({ reconBanner }: { reconBanner: string | null }) {
  const { live } = useCase();
  if (!live) return null;

  return (
    <section className="space-y-3">
      {reconBanner ? (
        <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
          {reconBanner}
        </div>
      ) : null}
      <div className="tp-card overflow-x-auto">
        <div className="border-b border-[var(--tp-line)] px-4 py-3">
          <h2 className="text-sm font-semibold text-[var(--tp-navy)]">
            Invoice vs bill of lading
          </h2>
          <p className="mt-1 text-xs text-[var(--tp-muted)]">
            Side-by-side field compare. Mismatches need a human — they are not proof of fraud.
          </p>
        </div>
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-[var(--tp-muted)]">
            <tr>
              <th className="px-3 py-2 text-left">Field</th>
              <th className="px-3 py-2 text-left">Invoice</th>
              <th className="px-3 py-2 text-left">Bill of lading</th>
              <th className="px-3 py-2 text-left">Status</th>
              <th className="px-3 py-2 text-left">Note</th>
            </tr>
          </thead>
          <tbody>
            {live.recon.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-6 text-[var(--tp-muted)]">
                  No comparison rows yet.
                </td>
              </tr>
            ) : (
              live.recon.map((r) => (
                <tr
                  key={r.field}
                  className={
                    r.status === "MISMATCH"
                      ? "tp-row-mismatch border-t border-[var(--tp-line)]"
                      : "border-t border-[var(--tp-line)]"
                  }
                >
                  <td className="px-3 py-2.5 font-medium">{r.field}</td>
                  <td className="px-3 py-2.5">{r.invoice}</td>
                  <td className="px-3 py-2.5">{r.bol ?? "—"}</td>
                  <td className="px-3 py-2.5">
                    {r.status === "MISMATCH" ? (
                      <MismatchFlag label={statusLabel(r.status)} />
                    ) : (
                      <ToneChip
                        tone={r.status === "MATCH" ? "clear" : "info"}
                        label={statusLabel(r.status)}
                      />
                    )}
                  </td>
                  <td className="px-3 py-2.5 text-[var(--tp-muted)]">{r.note}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
