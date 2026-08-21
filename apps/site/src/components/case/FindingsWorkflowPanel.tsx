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
      <div className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 id="findings-heading" className="text-lg font-semibold text-slate-50">
          Findings — price, screening, duplicate
        </h2>
        <p className="mt-1 text-sm text-slate-400">
          Use outcome text labels. Potential matches are not confirmations. Unavailable data is not
          PASS. Duplicate is a signal, not proof of fraud or duplicate financing.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {findings.map((f) => (
            <article key={f.id} className="rounded border border-slate-800 bg-slate-900/50 p-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-medium text-slate-100">{f.title}</h3>
                <span
                  className={`shrink-0 rounded border px-2 py-0.5 text-[11px] font-medium ${outcomeToneClass(f.outcome)}`}
                >
                  {findingOutcomeLabel(f.outcome)}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-300">{f.summary}</p>
              <p className="mt-2 text-xs text-slate-500">{f.detail}</p>
              <p className="mt-2 font-mono text-[11px] text-slate-500">
                Source: {f.sourceLabel}
                {f.snapshotId ? ` · Snapshot: ${f.snapshotId}` : ""}
                {f.ruleId ? ` · Rule: ${f.ruleId}` : ""}
              </p>
            </article>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
          <h3 className="text-base font-semibold text-slate-50">Maker / checker</h3>
          <p className="mt-1 text-sm text-slate-400">
            Human decision support only — UI does not claim AI approved or cleared the case.
          </p>
          <dl className="mt-3 space-y-2 text-sm">
            <div>
              <dt className="text-slate-500">Maker decision</dt>
              <dd className="text-slate-200">{makerChecker.makerDecision ?? "Not recorded"}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Checker decision</dt>
              <dd className="text-slate-200">{makerChecker.checkerDecision ?? "Not recorded"}</dd>
            </div>
            {makerChecker.blockedReason ? (
              <div>
                <dt className="text-slate-500">Blocked</dt>
                <dd className="text-amber-100">{makerChecker.blockedReason}</dd>
              </div>
            ) : null}
          </dl>
          <ul className="mt-3 flex flex-wrap gap-2">
            {makerChecker.allowedActions.map((action) => (
              <li
                key={action}
                className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-300"
              >
                {action}
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
          <h3 className="text-base font-semibold text-slate-50">Audit timeline</h3>
          <ol className="mt-3 space-y-3 border-l border-slate-700 pl-4">
            {audit.map((event) => (
              <li key={event.id} className="relative text-sm">
                <span className="absolute -left-[1.28rem] top-1 h-2 w-2 rounded-full bg-sky-400" />
                <p className="font-mono text-[11px] text-slate-500">
                  {formatTimestamp(event.at)} · {event.actor}
                </p>
                <p className="text-slate-200">{event.action}</p>
                <p className="text-slate-400">{event.detail}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
