import type { RegWatchEvent } from "@/lib/mock/types";
import { formatTimestamp } from "@/lib/mock/labels";

export function RegWatchPanel({ events }: { events: RegWatchEvent[] }) {
  return (
    <section className="rounded border border-rule bg-paper p-4" aria-labelledby="regwatch-heading">
      <h2 id="regwatch-heading" className="text-lg font-semibold text-ink">
        RegWatch — source registry & replay gate
      </h2>
      <p className="mt-1 text-sm text-slate">
        LLM/system output may propose diffs only. Human approval is required before a rule/data
        version becomes active or replay runs. Prior result versions are preserved.
      </p>

      <ul className="mt-4 space-y-4">
        {events.map((event) => (
          <li key={event.id} className="rounded border border-rule bg-paper p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-ink">{event.sourceName}</p>
                <p className="font-mono text-[11px] text-slate">
                  {event.publisher} · detected {formatTimestamp(event.detectedAt)}
                </p>
              </div>
              <span className="rounded border border-rule px-2 py-0.5 text-xs text-slate">
                Approval: {event.approvalState}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate">{event.summary}</p>
            <pre className="mt-3 overflow-x-auto rounded bg-paper p-3 text-xs text-slate">
              {event.proposedDiff}
            </pre>
            <div className="mt-3 grid gap-3 text-sm md:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate">Old result version</p>
                <p className="text-slate">{event.oldResultSummary}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate">New / proposed</p>
                <p className="text-slate">{event.newResultSummary}</p>
              </div>
            </div>
            <p className="mt-3 border-l-2 border-l-amber pl-2 text-sm text-ink">
              {event.replayAllowed
                ? "Replay permitted only because this change is APPROVED — still creates a new result version."
                : "Replay blocked until human approval. Proposed changes are not active."}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
