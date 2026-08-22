"use client";

export default function RegWatchPage() {
  const events = [
    {
      id: "rw-1",
      source: "IFSCA circular snapshot (demo)",
      state: "PROPOSED",
      summary: "Proposed documentary checklist wording update for enhanced reviews.",
      diff: "+ CoO required when ENHANCED_ORIGIN=true\n- CoO optional on baseline post-shipment",
      gate: "Replay blocked until human approval. Proposed changes are not active.",
      old: "Active pack v0.4 — CoO conditional.",
      next: "Proposed v0.4.1 — inactive until approved.",
    },
    {
      id: "rw-2",
      source: "Demo sanctions publisher checksum",
      state: "APPROVED",
      summary: "Snapshot checksum change on demo list.",
      diff: "~ Replace screen-snap-demo-01 → screen-snap-demo-02",
      gate: "Approved — selective replay may create a new result version; prior versions preserved.",
      old: "Cases on snap-01 retained as prior versions.",
      next: "New evaluations reference snap-02.",
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">
          Regulation watch
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-[var(--tp-muted)]">
          Proposed checklist or list updates need an officer’s approval before they go live. A
          proposal is never the same as activation. Earlier case results stay on record.
        </p>
      </div>

      <ul className="space-y-3">
        {events.map((e) => (
          <li key={e.id} className="tp-card p-5">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <h2 className="text-sm font-semibold text-[var(--tp-navy)]">{e.source}</h2>
              <span
                className={
                  e.state === "PROPOSED" ? "tp-chip tp-chip-review" : "tp-chip tp-chip-ok"
                }
              >
                Approval: {e.state}
              </span>
            </div>
            <p className="mt-2 text-sm text-[var(--tp-ink)]">{e.summary}</p>
            <pre className="mt-3 overflow-x-auto rounded-lg border border-[var(--tp-line)] bg-slate-50 p-3 font-mono text-xs text-[var(--tp-ink)]">
              {e.diff}
            </pre>
            <div className="mt-3 grid gap-3 text-sm md:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  Old result version
                </p>
                <p>{e.old}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  New / proposed
                </p>
                <p>{e.next}</p>
              </div>
            </div>
            <p className="mt-3 text-sm font-medium text-amber-900">{e.gate}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
