import type { RegWatchEvent } from "@/lib/mock/types";
import { formatTimestamp } from "@/lib/mock/labels";

export function RegWatchPanel({ events }: { events: RegWatchEvent[] }) {
  return (
    <section
      className="rounded border border-slate-700/80 bg-slate-950/40 p-4"
      aria-labelledby="regwatch-heading"
    >
      <h2 id="regwatch-heading" className="text-lg font-semibold text-slate-50">
        RegWatch — source registry & replay gate
      </h2>
      <p className="mt-1 text-sm text-slate-400">
        LLM/system output may propose diffs only. Human approval is required before a rule/data
        version becomes active or replay runs. Prior result versions are preserved.
      </p>

      <ul className="mt-4 space-y-4">
        {events.map((event) => (
          <li key={event.id} className="rounded border border-slate-800 bg-slate-900/50 p-4">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-slate-100">{event.sourceName}</p>
                <p className="font-mono text-[11px] text-slate-500">
                  {event.publisher} · detected {formatTimestamp(event.detectedAt)}
                </p>
              </div>
              <span className="rounded border border-slate-600 px-2 py-0.5 text-xs text-slate-200">
                Approval: {event.approvalState}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-300">{event.summary}</p>
            <pre className="mt-3 overflow-x-auto rounded bg-slate-950 p-3 text-xs text-slate-300">
              {event.proposedDiff}
            </pre>
            <div className="mt-3 grid gap-3 text-sm md:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Old result version</p>
                <p className="text-slate-300">{event.oldResultSummary}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">New / proposed</p>
                <p className="text-slate-300">{event.newResultSummary}</p>
              </div>
            </div>
            <p className="mt-3 text-sm text-amber-100/90">
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
