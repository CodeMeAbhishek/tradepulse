import type { AuditEvent, FindingCard, MakerCheckerState } from "@/lib/mock/types";
import { findingOutcomeLabel, formatTimestamp, outcomeToneClass } from "@/lib/mock/labels";

export function FindingsWorkflowPanel({
  findings,
  makerChecker,
  audit,
}: {
  findings: FindingCard[];
  makerChecker: MakerCheckerState;
  audit: AuditEvent[];
}) {
  return (
    <section className="space-y-4" aria-labelledby="findings-heading">
      <div className="rounded border border-rule bg-paper p-4">
        <h2 id="findings-heading" className="text-lg font-semibold text-ink">
          Findings — price, screening, duplicate
        </h2>
        <p className="mt-1 text-sm text-slate">
          Use outcome text labels. Potential matches are not confirmations. Unavailable data is not
          PASS. Duplicate is a signal, not proof of fraud or duplicate financing.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {findings.map((f) => (
            <article key={f.id} className="rounded border border-rule bg-paper p-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-medium text-ink">{f.title}</h3>
                <span
                  className={`text-label shrink-0 border-l-2 pl-2 text-ink ${outcomeToneClass(f.outcome)}`}
                >
                  {findingOutcomeLabel(f.outcome)}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate">{f.summary}</p>
              <p className="mt-2 text-xs text-slate">{f.detail}</p>
              <p className="mt-2 font-mono text-[11px] text-slate">
                Source: {f.sourceLabel}
                {f.snapshotId ? ` · Snapshot: ${f.snapshotId}` : ""}
                {f.ruleId ? ` · Rule: ${f.ruleId}` : ""}
              </p>
            </article>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-rule bg-paper p-4">
          <h3 className="text-base font-semibold text-ink">Maker / checker</h3>
          <p className="mt-1 text-sm text-slate">
            Human decision support only — UI does not claim AI approved or cleared the case.
          </p>
          <dl className="mt-3 space-y-2 text-sm">
            <div>
              <dt className="text-slate">Maker decision</dt>
              <dd className="text-slate">{makerChecker.makerDecision ?? "Not recorded"}</dd>
            </div>
            <div>
              <dt className="text-slate">Checker decision</dt>
              <dd className="text-slate">{makerChecker.checkerDecision ?? "Not recorded"}</dd>
            </div>
            {makerChecker.blockedReason ? (
              <div>
                <dt className="text-slate">Blocked</dt>
                <dd className="border-l-2 border-l-amber pl-2 text-ink">
                  {makerChecker.blockedReason}
                </dd>
              </div>
            ) : null}
          </dl>
          <ul className="mt-3 flex flex-wrap gap-2">
            {makerChecker.allowedActions.map((action) => (
              <li key={action} className="rounded border border-rule px-2 py-1 text-xs text-slate">
                {action}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded border border-rule bg-paper p-4">
          <h3 className="text-base font-semibold text-ink">Audit timeline</h3>
          <ol className="mt-3 space-y-3 border-l border-rule pl-4">
            {audit.map((event) => (
              <li key={event.id} className="relative text-sm">
                <span className="absolute -left-[1.28rem] top-1 h-2 w-2 rounded-full bg-ink" />
                <p className="font-mono text-[11px] text-slate">
                  {formatTimestamp(event.at)} · {event.actor}
                </p>
                <p className="text-slate">{event.action}</p>
                <p className="text-slate">{event.detail}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
