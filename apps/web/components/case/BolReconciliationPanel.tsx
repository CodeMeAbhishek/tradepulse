import type { CaseWorkbenchDetail } from "@/lib/mock/types";
import { findingOutcomeLabel, outcomeToneClass } from "@/lib/mock/labels";

export function BolReconciliationPanel({
  reconciliation,
}: {
  reconciliation: CaseWorkbenchDetail["reconciliation"];
}) {
  return (
    <section
      className="rounded border border-slate-700/80 bg-slate-950/40 p-4"
      aria-labelledby="recon-heading"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="recon-heading" className="text-lg font-semibold text-slate-50">
            Cross-document reconciliation (Invoice ↔ BoL)
          </h2>
          <p className="mt-1 text-sm text-slate-400">{reconciliation.explanation}</p>
        </div>
        <span
          className={`inline-flex rounded border px-2 py-0.5 text-xs font-medium ${outcomeToneClass(reconciliation.outcome)}`}
        >
          {findingOutcomeLabel(reconciliation.outcome)}
        </span>
      </div>

      {!reconciliation.bolPresent ? (
        <p className="mt-4 rounded border border-sky-800/60 bg-sky-950/30 px-3 py-3 text-sm text-sky-100">
          BoL/AWB absent — outcome is explicitly{" "}
          <strong>{findingOutcomeLabel(reconciliation.outcome)}</strong>, never PASS.
        </p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="py-2 pr-3">Field</th>
                <th className="py-2 pr-3">Invoice</th>
                <th className="py-2 pr-3">BoL / AWB</th>
                <th className="py-2 pr-3">Outcome</th>
                <th className="py-2">Note</th>
              </tr>
            </thead>
            <tbody>
              {reconciliation.rows.map((row) => (
                <tr key={row.field} className="border-t border-slate-800 align-top">
                  <td className="py-2.5 pr-3 text-slate-200">{row.field}</td>
                  <td className="py-2.5 pr-3 text-slate-300">{row.invoiceValue ?? "—"}</td>
                  <td className="py-2.5 pr-3 text-slate-300">{row.bolValue ?? "—"}</td>
                  <td className="py-2.5 pr-3">
                    <span
                      className={`inline-flex rounded border px-2 py-0.5 text-[11px] font-medium ${outcomeToneClass(row.outcome)}`}
                    >
                      {findingOutcomeLabel(row.outcome)}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate-400">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
