import type { AgentRoundTrace, ExtractedField } from "@/lib/mock/types";

export function InvoiceReviewPanel({
  fields,
  trace,
}: {
  fields: ExtractedField[];
  trace: AgentRoundTrace[];
}) {
  return (
    <section
      className="rounded border border-slate-700/80 bg-slate-950/40 p-4"
      aria-labelledby="invoice-review-heading"
    >
      <h2 id="invoice-review-heading" className="text-lg font-semibold text-slate-50">
        Invoice review & agent trace
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        Split-screen evidence review. Trace shows claims, challenges and arbiter outcomes only —
        never private chain-of-thought. Agent consensus is not a compliance approval.
      </p>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
          <h3 className="text-sm font-medium text-slate-200">Document surface (mock)</h3>
          <div className="mt-3 min-h-[220px] rounded border border-dashed border-slate-700 bg-slate-950/80 p-4 text-sm text-slate-400">
            <p className="font-medium text-slate-300">Commercial Invoice · page preview</p>
            <p className="mt-2">
              Synthetic page canvas. Evidence links below point to page/source text from extraction
              results.
            </p>
          </div>
          <ul className="mt-4 space-y-3">
            {fields.map((field) => (
              <li key={field.fieldPath} className="border-t border-slate-800 pt-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="text-sm text-slate-200">{field.label}</span>
                  <span className="font-mono text-[11px] text-slate-500">
                    Confidence: {field.confidence}
                  </span>
                </div>
                <p className="mt-1 font-medium text-slate-50">{field.value}</p>
                {field.evidence ? (
                  <p className="mt-1 text-xs text-sky-300/90">
                    Evidence: p.{field.evidence.page} — “{field.evidence.sourceText}”
                  </p>
                ) : (
                  <p className="mt-1 text-xs text-amber-200/90">No evidence attached — review.</p>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded border border-slate-800 bg-slate-900/50 p-3">
          <h3 className="text-sm font-medium text-slate-200">Agent trace</h3>
          <ol className="mt-3 space-y-4">
            {trace.map((round) => (
              <li key={round.round} className="rounded border border-slate-800 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Round {round.round} of max 3
                </p>
                <dl className="mt-2 space-y-2 text-sm">
                  <div>
                    <dt className="text-slate-400">Extractor · {round.extractor.status}</dt>
                    <dd className="text-slate-200">
                      {round.extractor.claims.map((c) => (
                        <p key={`${round.round}-ex-${c.fieldPath}`}>
                          {c.fieldPath}: {c.proposedValue}
                          {c.hasEvidence ? " (evidence)" : " (no evidence)"} — {c.reason}
                        </p>
                      ))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-400">Validator · {round.validator.status}</dt>
                    <dd className="text-slate-200">
                      {round.validator.claims.map((c) => (
                        <p key={`${round.round}-va-${c.fieldPath}`}>
                          {c.fieldPath}: {c.proposedValue} — {c.reason}
                        </p>
                      ))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-400">Challenger · {round.challenger.status}</dt>
                    <dd className="text-slate-200">
                      {round.challenger.challenges.length === 0
                        ? "No challenges."
                        : round.challenger.challenges.map((c) => (
                            <p key={`${round.round}-ch-${c.fieldPath}-${c.category}`}>
                              {c.category} on {c.fieldPath}: {c.reason}
                            </p>
                          ))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-400">
                      Arbiter · {round.arbiter.status} ·{" "}
                      {round.arbiter.agreement ? "Agreement" : "Disagreement"}
                    </dt>
                    <dd className="text-slate-100">{round.arbiter.decisionSummary}</dd>
                  </div>
                </dl>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
