"use client";

import { CaseStatus } from "../../../../../packages/contracts/types";
import { useCase } from "@/components/case/CaseContext";

export function DecideTab({
  note,
  setNote,
}: {
  note: string;
  setNote: (v: string) => void;
}) {
  const { live, busy, maker, checker, run } = useCase();
  if (!live) return null;

  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <div className="tp-card p-5">
        <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Maker / checker</h2>
        <p className="mt-1 text-xs text-[var(--tp-muted)]">
          Dual control: checker actions unlock only after maker submission.
        </p>
        <label className="mt-3 block text-sm">
          Decision note
          <textarea
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            rows={3}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Optional note for the audit trail"
          />
        </label>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy || live.workflow !== CaseStatus.PENDING_MAKER_REVIEW}
            onClick={() => void run(() => maker(live.id, "approve", note))}
            className="rounded-lg bg-[var(--tp-navy)] px-3 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            Maker: submit to checker
          </button>
          <button
            type="button"
            disabled={busy || live.workflow !== CaseStatus.PENDING_MAKER_REVIEW}
            onClick={() => void run(() => maker(live.id, "investigate", note))}
            className="rounded-lg border border-amber-400 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-950 disabled:opacity-40"
          >
            Maker: escalate
          </button>
          <button
            type="button"
            disabled={busy || live.workflow !== CaseStatus.MAKER_APPROVED}
            onClick={() => void run(() => checker(live.id, "approve", note))}
            className="rounded-lg bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            Checker: approve
          </button>
          <button
            type="button"
            disabled={busy || live.workflow !== CaseStatus.MAKER_APPROVED}
            onClick={() => void run(() => checker(live.id, "reject", note))}
            className="rounded-lg border border-rose-300 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-900 disabled:opacity-40"
          >
            Checker: reject
          </button>
        </div>
      </div>
      <div className="tp-card p-5">
        <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Audit timeline</h2>
        <ol className="mt-3 space-y-3 border-l border-[var(--tp-line)] pl-4">
          {[...live.audit].reverse().map((e) => (
            <li key={e.id} className="relative text-sm">
              <span className="absolute -left-[1.28rem] top-1.5 h-2 w-2 rounded-full bg-teal-600" />
              <p className="text-[11px] text-[var(--tp-muted)]">
                {new Date(e.at).toLocaleString()} · {e.actor}
              </p>
              <p className="font-medium text-[var(--tp-navy)]">{e.action}</p>
              {e.detail ? <p className="text-[var(--tp-muted)]">{e.detail}</p> : null}
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
