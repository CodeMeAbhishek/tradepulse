import type { CaseWorkbenchDetail } from "@/lib/mock/types";
import { findingOutcomeLabel, outcomeToneClass } from "@/lib/mock/labels";

export function BolReconciliationPanel({
  reconciliation,
}: {
  reconciliation: CaseWorkbenchDetail["reconciliation"];
}) {
  return (
    <section className="rounded border border-rule bg-paper p-4" aria-labelledby="recon-heading">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="recon-heading" className="text-lg font-semibold text-ink">
            Cross-document reconciliation (Invoice ↔ BoL)
          </h2>
          <p className="mt-1 text-sm text-slate">{reconciliation.explanation}</p>
        </div>
        <span
          className={`text-label inline-flex border-l-2 pl-2 text-ink ${outcomeToneClass(reconciliation.outcome)}`}
        >
          {findingOutcomeLabel(reconciliation.outcome)}
        </span>
      </div>

      {!reconciliation.bolPresent ? (
        <p className="mt-4 rounded border border-rule bg-bench px-3 py-3 text-sm text-ink">
          BoL/AWB absent — outcome is explicitly{" "}
          <strong>{findingOutcomeLabel(reconciliation.outcome)}</strong>, never PASS.
        </p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-slate">
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
                <tr key={row.field} className="border-t border-rule align-top">
                  <td className="py-2.5 pr-3 text-slate">{row.field}</td>
                  <td className="py-2.5 pr-3 text-slate">{row.invoiceValue ?? "—"}</td>
                  <td className="py-2.5 pr-3 text-slate">{row.bolValue ?? "—"}</td>
                  <td className="py-2.5 pr-3">
                    <span
                      className={`text-label inline-flex border-l-2 pl-2 text-ink ${outcomeToneClass(row.outcome)}`}
                    >
                      {findingOutcomeLabel(row.outcome)}
                    </span>
                  </td>
                  <td className="py-2.5 text-slate">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
