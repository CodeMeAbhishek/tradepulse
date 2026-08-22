"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { policyLabel, statusLabel } from "@/lib/api/map";
import { useDemo } from "@/lib/demo/DemoProvider";
import { InvestigationCanvas } from "@/components/case/InvestigationCanvas";
import { RiskChip, ToneChip, WorkflowChip } from "@/components/ui/StatusChips";
import { profileLabel } from "@/lib/demo/store";

const TABS = [
  "Investigate",
  "Summary",
  "Documents",
  "Reconciliation",
  "Identity",
  "Agent trace",
  "Decision",
] as const;

export function CaseWorkbench({ caseId }: { caseId: string }) {
  const [tab, setTab] = useState<(typeof TABS)[number]>("Investigate");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState<Record<string, boolean>>({});
  const { ready, maker, checker, cases, loadCase, mode } = useDemo();

  useEffect(() => {
    if (mode !== "api") return;
    let cancelled = false;
    void loadCase(caseId).catch((e: unknown) => {
      if (!cancelled) setErr(e instanceof Error ? e.message : "Failed to load case");
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- loadCase identity changes with cases
  }, [caseId, mode]);

  const live = cases.find((x) => x.id === caseId);

  const reconBanner = useMemo(() => {
    if (!live?.recon.length) return null;
    const allNa = live.recon.every((r) => r.status === "NOT_AVAILABLE");
    const bolEmpty = live.recon.every((r) => !r.bol || r.bol === "—");
    const bolUploaded = live.docs.some((d) => d.type.includes("bill_of_lading") && d.provided);
    if (allNa && bolUploaded && bolEmpty) {
      return "Bill of lading is on the case, but structured fields could not be compared yet. Re-process after a labeled BoL upload, or review the PDF manually.";
    }
    if (allNa && !bolUploaded) {
      return "Transport reconciliation is not available for this packet (no Bill of lading, or invoice-only profile). This is not a pass.";
    }
    return null;
  }, [live]);

  if (!ready) {
    return <p className="text-sm text-[var(--tp-muted)]">Loading case…</p>;
  }
  if (!live) {
    return (
      <div className="tp-card p-8 text-center">
        <h1 className="text-lg font-semibold text-[var(--tp-navy)]">Case not found</h1>
        {err ? <p className="mt-2 text-sm text-rose-700">{err}</p> : null}
        <Link href="/queue" className="mt-3 inline-block text-sm text-[var(--tp-accent)]">
          Back to queue
        </Link>
      </div>
    );
  }

  const mismatch = live.recon.find((r) => r.status === "MISMATCH");

  const run = async (fn: () => Promise<void>) => {
    setBusy(true);
    setErr(null);
    try {
      await fn();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <p>
        <Link href="/queue" className="text-sm font-medium text-[var(--tp-accent)]">
          ← Queue
        </Link>
      </p>

      <header className="tp-card p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--tp-muted)]">
              Case workbench {mode === "api" ? "· live API" : "· local demo"}
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-[var(--tp-navy)]">{live.reference}</h1>
            <p className="mt-1 text-[var(--tp-ink)]">{live.counterparty}</p>
            <p className="mt-1 text-sm text-[var(--tp-muted)]">
              {live.corridor} · {profileLabel(live.profile)} · {live.currency} {live.amount}
            </p>
          </div>
          <div className="flex flex-col items-start gap-2 sm:items-end">
            <RiskChip route={live.riskRoute} />
            <WorkflowChip state={live.workflow} />
            <span className="text-xs text-[var(--tp-muted)]">{live.slaLabel}</span>
          </div>
        </div>

        {mismatch ? (
          <div className="mt-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3">
            <p className="text-sm font-semibold text-amber-950">
              Document discrepancy — human review required
            </p>
            <p className="mt-1 text-sm text-amber-900">
              Invoice: <strong>{mismatch.invoice}</strong> · Bill of lading:{" "}
              <strong>{mismatch.bol}</strong>
            </p>
            <p className="mt-2 text-sm text-amber-900/90">{mismatch.note}</p>
          </div>
        ) : null}
        {busy ? <ProcessingRail /> : null}
        {err ? <p className="mt-3 text-sm text-rose-700">{err}</p> : null}
      </header>

      <div className="flex flex-wrap gap-1 border-b border-[var(--tp-line)] pb-2">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={
              tab === t
                ? "rounded-md bg-[var(--tp-navy)] px-3 py-1.5 text-sm font-medium text-white"
                : "rounded-md px-3 py-1.5 text-sm text-[var(--tp-muted)] hover:bg-white"
            }
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Investigate" ? <InvestigationCanvas tradeCase={live} /> : null}

      {tab === "Summary" ? (
        <section className="grid gap-3 md:grid-cols-3">
          {live.findings.length === 0 ? (
            <p className="text-sm text-[var(--tp-muted)] md:col-span-3">
              No findings yet. Process the case after uploading documents.
            </p>
          ) : (
            live.findings.map((f, i) => (
              <article
                key={f.id}
                className="tp-card tp-reveal flex flex-col p-4"
                style={{ "--i": i } as React.CSSProperties}
              >
                <div className="flex items-start justify-between gap-2">
                  <h2 className="text-sm font-semibold text-[var(--tp-navy)]">{f.title}</h2>
                  <ToneChip tone={f.tone} label={f.statusLabel} />
                </div>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-[var(--tp-ink)]">{f.summary}</p>
                <p className="mt-3 text-sm font-medium text-[var(--tp-teal)]">
                  Next: {f.action}
                </p>
                <button
                  type="button"
                  className="mt-3 self-start text-xs font-medium text-[var(--tp-muted)] underline-offset-2 hover:underline"
                  onClick={() =>
                    setShowEvidence((prev) => ({ ...prev, [f.id]: !prev[f.id] }))
                  }
                >
                  {showEvidence[f.id] ? "Hide evidence source" : "Show evidence source"}
                </button>
                {showEvidence[f.id] ? (
                  <p className="mt-1 font-mono text-[11px] text-[var(--tp-muted)]">{f.source}</p>
                ) : null}
              </article>
            ))
          )}
        </section>
      ) : null}

      {tab === "Documents" ? (
        <section className="tp-card overflow-hidden">
          <div className="border-b border-[var(--tp-line)] px-4 py-3">
            <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Document checklist</h2>
            <p className="mt-1 text-xs text-[var(--tp-muted)]">
              Required items block completeness when missing. Optional items never block a case.
            </p>
          </div>
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-[var(--tp-muted)]">
              <tr>
                <th className="px-3 py-2 text-left">Document</th>
                <th className="px-3 py-2 text-left">Requirement</th>
                <th className="px-3 py-2 text-left">Provided</th>
                <th className="px-3 py-2 text-left">Blocks if missing</th>
              </tr>
            </thead>
            <tbody>
              {live.docs.map((d) => (
                <tr key={d.type} className="border-t border-[var(--tp-line)]">
                  <td className="px-3 py-2.5 font-medium capitalize">{d.label}</td>
                  <td className="px-3 py-2.5">{policyLabel(d.policy)}</td>
                  <td className="px-3 py-2.5">{d.provided ? "Yes" : "No"}</td>
                  <td className="px-3 py-2.5">{d.blocker ? "Yes" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      {tab === "Reconciliation" ? (
        <section className="space-y-3">
          {reconBanner ? (
            <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-950">
              {reconBanner}
            </div>
          ) : null}
          <div className="tp-card overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-[var(--tp-muted)]">
                <tr>
                  <th className="px-3 py-2 text-left">Field</th>
                  <th className="px-3 py-2 text-left">Invoice</th>
                  <th className="px-3 py-2 text-left">Bill of lading</th>
                  <th className="px-3 py-2 text-left">Status</th>
                  <th className="px-3 py-2 text-left">Note</th>
                </tr>
              </thead>
              <tbody>
                {live.recon.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-[var(--tp-muted)]">
                      No reconciliation rows yet.
                    </td>
                  </tr>
                ) : (
                  live.recon.map((r) => (
                    <tr key={r.field} className="border-t border-[var(--tp-line)]">
                      <td className="px-3 py-2.5 font-medium">{r.field}</td>
                      <td className="px-3 py-2.5">{r.invoice}</td>
                      <td className="px-3 py-2.5">{r.bol ?? "—"}</td>
                      <td className="px-3 py-2.5">
                        <ToneChip
                          tone={
                            r.status === "MATCH"
                              ? "clear"
                              : r.status === "MISMATCH"
                                ? "review"
                                : "info"
                          }
                          label={statusLabel(r.status)}
                        />
                      </td>
                      <td className="px-3 py-2.5 text-[var(--tp-muted)]">{r.note}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {tab === "Identity" ? (
        <section className="tp-card grid gap-6 p-5 md:grid-cols-2">
          <div>
            <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Document party</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  Name on document
                </dt>
                <dd className="mt-0.5 font-medium">{live.identity.rawName}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  LEI on document
                </dt>
                <dd className="mt-0.5 font-mono text-xs">
                  {live.identity.leiOnDocument ?? "Not provided"}
                </dd>
              </div>
              {live.identity.candidateName ? (
                <div>
                  <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                    Registry legal name
                  </dt>
                  <dd className="mt-0.5">{live.identity.candidateName}</dd>
                </div>
              ) : null}
            </dl>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Identity outcome</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">Status</dt>
                <dd className="mt-0.5 text-base font-semibold text-[var(--tp-navy)]">
                  {live.identity.outcome}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  What this means
                </dt>
                <dd className="mt-0.5 leading-relaxed">{live.identity.action}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">vLEI</dt>
                <dd className="mt-0.5 text-[var(--tp-muted)]">{live.identity.vlei}</dd>
              </div>
            </dl>
          </div>
        </section>
      ) : null}

      {tab === "Agent trace" ? (
        <section className="tp-card p-5">
          <p className="mb-4 text-sm text-[var(--tp-muted)]">
            Bounded document-intelligence steps (max 3 rounds). Claims and challenges are stored —
            private chain-of-thought is not. Agent consensus is never a compliance approval.
          </p>
          <ol className="space-y-3">
            {live.agentTrace.map((step, idx) => (
              <li
                key={`${step.agent}-${idx}`}
                className="rounded-lg border border-[var(--tp-line)] bg-slate-50 px-3 py-2.5"
              >
                <div className="flex justify-between gap-2">
                  <span className="text-sm font-semibold text-[var(--tp-navy)]">{step.agent}</span>
                  <span className="text-[11px] font-medium uppercase tracking-wide text-[var(--tp-muted)]">
                    {step.status}
                  </span>
                </div>
                <p className="mt-1 text-sm leading-relaxed">{step.summary}</p>
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      {tab === "Decision" ? (
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
                disabled={busy || live.workflow !== "PENDING_MAKER"}
                onClick={() => void run(() => maker(live.id, "approve", note))}
                className="rounded-lg bg-[var(--tp-navy)] px-3 py-2 text-sm font-medium text-white disabled:opacity-40"
              >
                Maker: submit to checker
              </button>
              <button
                type="button"
                disabled={busy || live.workflow !== "PENDING_MAKER"}
                onClick={() => void run(() => maker(live.id, "investigate", note))}
                className="rounded-lg border border-amber-400 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-950 disabled:opacity-40"
              >
                Maker: escalate
              </button>
              <button
                type="button"
                disabled={busy || live.workflow !== "MAKER_APPROVED"}
                onClick={() => void run(() => checker(live.id, "approve", note))}
                className="rounded-lg bg-teal-700 px-3 py-2 text-sm font-medium text-white disabled:opacity-40"
              >
                Checker: approve
              </button>
              <button
                type="button"
                disabled={busy || live.workflow !== "MAKER_APPROVED"}
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
      ) : null}
    </div>
  );
}

/**
 * Shown only while a case is processing.
 *
 * The bar is indeterminate because the backend reports no progress figure —
 * a percentage here would be invented. The stage list names the agents the
 * orchestrator actually runs, so what is on screen matches what is happening.
 */
function ProcessingRail() {
  const stages = ["Extracting", "Validating", "Challenging", "Arbitrating", "Reconciling"];
  return (
    <div className="mt-4" role="status" aria-live="polite">
      <div className="tp-rail" />
      <p className="mt-2 text-xs text-[var(--tp-muted)]">
        Processing — {stages.join(" · ")}
      </p>
    </div>
  );
}
