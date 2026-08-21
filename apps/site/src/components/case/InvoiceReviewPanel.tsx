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
      className="rounded border border-rule bg-paper p-4"
      aria-labelledby="invoice-review-heading"
    >
      <h2 id="invoice-review-heading" className="text-lg font-semibold text-ink">
        Invoice review & agent trace
      </h2>
      <p className="mt-1 text-sm text-slate">
        Split-screen evidence review. Trace shows claims, challenges and arbiter outcomes only —
        never private chain-of-thought. Agent consensus is not a compliance approval.
      </p>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-rule bg-paper p-3">
          <h3 className="text-sm font-medium text-slate">Document surface (mock)</h3>
          <div className="mt-3 min-h-[220px] rounded border border-dashed border-rule bg-paper p-4 text-sm text-slate">
            <p className="font-medium text-slate">Commercial Invoice · page preview</p>
            <p className="mt-2">
              Synthetic page canvas. Evidence links below point to page/source text from extraction
              results.
            </p>
          </div>
          <ul className="mt-4 space-y-3">
            {fields.map((field) => (
              <li key={field.fieldPath} className="border-t border-rule pt-3">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="text-sm text-slate">{field.label}</span>
                  <span className="font-mono text-[11px] text-slate">
                    Confidence: {field.confidence}
                  </span>
                </div>
                <p className="mt-1 font-medium text-ink">{field.value}</p>
                {field.evidence ? (
                  <p className="mt-1 text-xs text-ink/90">
                    Evidence: p.{field.evidence.page} — “{field.evidence.sourceText}”
                  </p>
                ) : (
                  <p className="mt-1 border-l-2 border-l-amber pl-2 text-xs text-ink">
                    No evidence attached — review.
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded border border-rule bg-paper p-3">
          <h3 className="text-sm font-medium text-slate">Agent trace</h3>
          <ol className="mt-3 space-y-4">
            {trace.map((round) => (
              <li key={round.round} className="rounded border border-rule p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate">
                  Round {round.round} of max 3
                </p>
                <dl className="mt-2 space-y-2 text-sm">
                  <div>
                    <dt className="text-slate">Extractor · {round.extractor.status}</dt>
                    <dd className="text-slate">
                      {round.extractor.claims.map((c) => (
                        <p key={`${round.round}-ex-${c.fieldPath}`}>
                          {c.fieldPath}: {c.proposedValue}
                          {c.hasEvidence ? " (evidence)" : " (no evidence)"} — {c.reason}
                        </p>
                      ))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate">Validator · {round.validator.status}</dt>
                    <dd className="text-slate">
                      {round.validator.claims.map((c) => (
                        <p key={`${round.round}-va-${c.fieldPath}`}>
                          {c.fieldPath}: {c.proposedValue} — {c.reason}
                        </p>
                      ))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate">Challenger · {round.challenger.status}</dt>
                    <dd className="text-slate">
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
                    <dt className="text-slate">
                      Arbiter · {round.arbiter.status} ·{" "}
                      {round.arbiter.agreement ? "Agreement" : "Disagreement"}
                    </dt>
                    <dd className="text-ink">{round.arbiter.decisionSummary}</dd>
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
