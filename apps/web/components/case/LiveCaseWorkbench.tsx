"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  SAMPLE_APPLICATION_TXT,
  SAMPLE_AWB_TXT,
  SAMPLE_BOL_MATCH_TXT,
  SAMPLE_BOL_MISMATCH_TXT,
  SAMPLE_INVOICE_TXT,
  SAMPLE_LC_TXT,
  SAMPLE_SHIPPING_BILL_TXT,
  api,
} from "@/lib/api/client";
import type { DocumentTypeApi, WorkbenchPayload } from "@/lib/api/types";
import { apiBaseUrl } from "@/lib/api/config";

function Chip({ children, tone = "slate" }: { children: React.ReactNode; tone?: string }) {
  const tones: Record<string, string> = {
    slate: "border-slate-600 bg-slate-900 text-slate-200",
    green: "border-emerald-700/60 bg-emerald-950/40 text-emerald-100",
    amber: "border-amber-700/60 bg-amber-950/40 text-amber-100",
    sky: "border-sky-700/60 bg-sky-950/40 text-sky-100",
    rose: "border-rose-700/60 bg-rose-950/40 text-rose-100",
  };
  return (
    <span className={`inline-flex rounded border px-2 py-0.5 text-xs font-medium ${tones[tone] ?? tones.slate}`}>
      {children}
    </span>
  );
}

function toneForStatus(status: string | null | undefined): string {
  if (!status) return "slate";
  if (status.includes("PASS") || (status.includes("COMPLETE") && !status.includes("INCOMPLETE")))
    return "green";
  if (
    status.includes("NOT_AVAILABLE") ||
    status.includes("DATA_UNAVAILABLE") ||
    status.includes("INCOMPLETE")
  )
    return "sky";
  if (status.includes("REVIEW") || status.includes("POTENTIAL") || status.includes("WARN"))
    return "amber";
  if (status.includes("FAIL") || status.includes("REJECT") || status.includes("ESCALAT"))
    return "rose";
  return "slate";
}

function stageChip(state: string): { label: string; tone: string } {
  if (state.includes("SCRUTINY") || state === "DRAFT" || state === "DOCUMENT_PACK_INCOMPLETE")
    return { label: "Scrutiny", tone: "sky" };
  if (
    state.includes("MAKER") ||
    state === "INFORMATION_REQUESTED" ||
    state === "RETURNED_TO_MAKER"
  )
    return { label: "Maker", tone: "amber" };
  if (state.includes("CHECKER") || state === "ESCALATED") return { label: "Checker", tone: "green" };
  return { label: state, tone: "slate" };
}

export function LiveCaseWorkbench({ caseId }: { caseId: string }) {
  const [data, setData] = useState<WorkbenchPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const wb = await api.getWorkbench(caseId);
      setData(wb);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load workbench");
    }
  }, [caseId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function run(label: string, fn: () => Promise<void>) {
    setBusy(label);
    setError(null);
    try {
      await fn();
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : label + " failed");
    } finally {
      setBusy(null);
    }
  }

  async function uploadSample(
    kind:
      | "application"
      | "invoice"
      | "bol-match"
      | "bol-mismatch"
      | "awb"
      | "lc"
      | "shipping-bill",
  ) {
    const map: Record<
      typeof kind,
      { text: string; docType: DocumentTypeApi; name: string }
    > = {
      application: {
        text: SAMPLE_APPLICATION_TXT,
        docType: "trade_finance_application",
        name: "sample-application.txt",
      },
      invoice: {
        text: SAMPLE_INVOICE_TXT,
        docType: "commercial_invoice",
        name: "sample-invoice.txt",
      },
      "bol-match": {
        text: SAMPLE_BOL_MATCH_TXT,
        docType: "bill_of_lading",
        name: "sample-bol-match.txt",
      },
      "bol-mismatch": {
        text: SAMPLE_BOL_MISMATCH_TXT,
        docType: "bill_of_lading",
        name: "sample-bol-mismatch.txt",
      },
      awb: {
        text: SAMPLE_AWB_TXT,
        docType: "air_waybill",
        name: "sample-awb.txt",
      },
      lc: {
        text: SAMPLE_LC_TXT,
        docType: "lc_terms_lite",
        name: "sample-lc.txt",
      },
      "shipping-bill": {
        text: SAMPLE_SHIPPING_BILL_TXT,
        docType: "shipping_bill",
        name: "sample-shipping-bill.txt",
      },
    };
    const item = map[kind];
    const blob = new Blob([item.text], { type: "text/plain" });
    await api.uploadDocument(caseId, blob, item.docType, item.name);
  }

  if (!data && !error) {
    return <p className="px-4 py-8 text-sm text-slate-400">Loading workbench…</p>;
  }

  if (error && !data) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-16">
        <p className="text-rose-200">{error}</p>
        <p className="mt-2 text-sm text-slate-400">API: {apiBaseUrl()}</p>
        <Link href="/" className="mt-4 inline-block text-sky-300 hover:underline">
          ← Queue
        </Link>
      </main>
    );
  }

  if (!data) return null;

  const {
    case: c,
    policy,
    documents,
    invoice_extraction,
    agent_trace,
    findings,
    reconciliation,
    identities,
    audit,
  } = data;
  const stage = stageChip(c.state);
  const isAir = c.shipment_mode === "AIR";

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <p>
        <Link href="/" className="text-sm text-sky-300 hover:underline">
          ← Compliance queue
        </Link>
      </p>

      <header className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Live case workbench</p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-50">{c.case_id}</h1>
          <p className="mt-1 text-sm text-slate-400">
            {c.corridor ?? "—"} · {c.data_label} · v{c.version} · mode {c.shipment_mode ?? "UNKNOWN"}{" "}
            · {apiBaseUrl()}
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 sm:items-end">
          <Chip>{c.transaction_profile}</Chip>
          <Chip tone={stage.tone}>Stage: {stage.label}</Chip>
          <Chip tone={toneForStatus(c.state)}>{c.state}</Chip>
          <Chip tone={toneForStatus(c.risk_route)}>{c.risk_route ?? "No risk route yet"}</Chip>
        </div>
      </header>

      {error ? (
        <p className="rounded border border-rose-800/60 bg-rose-950/40 px-3 py-2 text-sm text-rose-100">
          {error}
        </p>
      ) : null}

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Documents</h2>
        <p className="mt-1 text-sm text-slate-400">
          Upload application-led fixtures, then process. AWB ≠ BoL — use AWB when mode is AIR.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {(
            [
              ["application", "Upload application"],
              ["invoice", "Upload invoice"],
              ["lc", "Upload LC terms"],
              ["bol-match", "Upload matching BoL"],
              ["bol-mismatch", "Upload mismatch BoL"],
              ["awb", "Upload AWB"],
              ["shipping-bill", "Upload shipping bill"],
            ] as const
          ).map(([kind, label]) => (
            <button
              key={kind}
              type="button"
              disabled={!!busy}
              className="rounded bg-slate-800 px-3 py-1.5 text-sm text-slate-100 hover:bg-slate-700 disabled:opacity-50"
              onClick={() => void run(`upload-${kind}`, () => uploadSample(kind))}
            >
              {label}
            </button>
          ))}
          <button
            type="button"
            disabled={!!busy}
            className="rounded bg-sky-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-600 disabled:opacity-50"
            onClick={() =>
              void run("process", async () => {
                const wb = await api.processCase(caseId);
                setData(wb);
              })
            }
          >
            {busy === "process" ? "Processing…" : "Process case"}
          </button>
        </div>
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Workflow actions</h2>
        <p className="mt-1 text-sm text-slate-400">
          Four-eyes: Scrutiny cannot clear · Maker cannot self-check · Checker needs maker
          recommendation. AI never approves.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-slate-600 px-3 py-1.5 text-sm text-slate-200"
            onClick={() =>
              void run("scrutiny", async () => {
                await api.caseAction(caseId, {
                  action: "scrutiny_complete",
                  actor: "scrutiny.demo",
                  actor_role: "scrutiny",
                });
              })
            }
          >
            Scrutiny complete
          </button>
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-slate-600 px-3 py-1.5 text-sm text-slate-200"
            onClick={() =>
              void run("maker-rec", async () => {
                await api.caseAction(caseId, {
                  action: "maker_recommend",
                  actor: "maker.demo",
                  actor_role: "maker",
                  note: "Recommend for checker review",
                });
              })
            }
          >
            Maker recommend
          </button>
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-amber-700/60 px-3 py-1.5 text-sm text-amber-100"
            onClick={() =>
              void run("maker-info", async () => {
                await api.caseAction(caseId, {
                  action: "maker_request_info",
                  actor: "maker.demo",
                  actor_role: "maker",
                  note: "Clarification needed",
                });
              })
            }
          >
            Maker request info
          </button>
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-emerald-700/60 px-3 py-1.5 text-sm text-emerald-100"
            onClick={() =>
              void run("checker-ok", async () => {
                await api.caseAction(caseId, {
                  action: "checker_approve",
                  actor: "checker.demo",
                  actor_role: "checker",
                });
              })
            }
          >
            Checker approve
          </button>
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-slate-600 px-3 py-1.5 text-sm text-slate-200"
            onClick={() =>
              void run("checker-ret", async () => {
                await api.caseAction(caseId, {
                  action: "checker_return",
                  actor: "checker.demo",
                  actor_role: "checker",
                });
              })
            }
          >
            Checker return
          </button>
          <button
            type="button"
            disabled={!!busy}
            className="rounded border border-rose-700/60 px-3 py-1.5 text-sm text-rose-100"
            onClick={() =>
              void run("checker-esc", async () => {
                await api.caseAction(caseId, {
                  action: "checker_escalate",
                  actor: "checker.demo",
                  actor_role: "checker",
                });
              })
            }
          >
            Checker escalate
          </button>
        </div>
        {busy ? <p className="mt-2 text-xs text-slate-500">Working: {busy}</p> : null}
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Document policy</h2>
        <p className="mt-1 text-sm text-slate-400">
          Transport recon: {policy.transport_reconciliation}
          {isAir ? " · AIR mode expects AWB" : " · ocean/default expects BoL"}
          {policy.missing_blocker_types?.length
            ? ` · missing blockers: ${policy.missing_blocker_types.join(", ")}`
            : ""}
        </p>
        <div className="mt-2">
          <Chip tone={toneForStatus(policy.pack_status)}>Pack: {policy.pack_status}</Chip>
        </div>
        <ul className="mt-3 space-y-1 text-sm text-slate-300">
          {policy.requirements?.map((r) => (
            <li key={r.document_type}>
              <span className="text-slate-400">{r.document_type}:</span> {r.state} ·{" "}
              {r.provided ? "provided" : "not provided"}
              {r.blocker ? " · blocker if missing" : ""}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-slate-500">
          Uploaded:{" "}
          {documents.length
            ? documents.map((d) => `${d.filename} (${d.document_type})`).join(", ")
            : "none"}
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
          <h2 className="text-lg font-semibold text-slate-50">Invoice extraction</h2>
          {!invoice_extraction ? (
            <p className="mt-2 text-sm text-slate-500">Process after uploading an invoice.</p>
          ) : (
            <dl className="mt-3 space-y-2 text-sm">
              <div>
                <dt className="text-slate-500">Invoice #</dt>
                <dd>{invoice_extraction.invoice_number}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Seller</dt>
                <dd>
                  {invoice_extraction.seller?.legal_name}
                  {invoice_extraction.seller?.lei
                    ? ` · LEI ${invoice_extraction.seller.lei}`
                    : " · LEI not on document"}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Quantity</dt>
                <dd>
                  {invoice_extraction.items[0]?.quantity} {invoice_extraction.items[0]?.unit}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Ports / airports</dt>
                <dd>
                  {invoice_extraction.port_of_loading} → {invoice_extraction.port_of_discharge}
                </dd>
              </div>
            </dl>
          )}
        </div>

        <div className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
          <h2 className="text-lg font-semibold text-slate-50">Agent trace</h2>
          <p className="mt-1 text-xs text-slate-500">
            Structured stages only — no chain-of-thought. Rounds used:{" "}
            {data.debate_rounds_used ?? "—"}
          </p>
          {agent_trace.length === 0 ? (
            <p className="mt-2 text-sm text-slate-500">No trace yet.</p>
          ) : (
            <ol className="mt-3 space-y-2 text-sm">
              {agent_trace.map((step, i) => (
                <li key={`${step.agent}-${step.round}-${i}`} className="rounded border border-slate-800 p-2">
                  <p className="font-medium text-slate-200">
                    {String(step.agent).toUpperCase()} · round {step.round} · {step.status}
                  </p>
                  {step.reason ? <p className="text-slate-400">{step.reason}</p> : null}
                </li>
              ))}
            </ol>
          )}
        </div>
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold text-slate-50">
            Invoice ↔ {isAir ? "AWB" : "BoL/AWB"} reconciliation
          </h2>
          <Chip tone={toneForStatus(reconciliation?.status ?? null)}>
            {reconciliation?.status ?? "NOT_RUN"}
          </Chip>
        </div>
        <p className="mt-2 text-sm text-slate-400">
          {reconciliation?.reason ?? "Process the case to run reconciliation."}
        </p>
        {reconciliation?.recommended_action ? (
          <p className="mt-2 text-sm text-amber-100">
            Recommended action: {reconciliation.recommended_action}
          </p>
        ) : null}
        {reconciliation?.comparisons?.length ? (
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="py-1 pr-3">Field</th>
                  <th className="py-1 pr-3">Invoice</th>
                  <th className="py-1 pr-3">Transport</th>
                  <th className="py-1 pr-3">Status</th>
                  <th className="py-1">Reason</th>
                </tr>
              </thead>
              <tbody>
                {reconciliation.comparisons.map((row) => (
                  <tr key={row.field_path} className="border-t border-slate-800 align-top">
                    <td className="py-2 pr-3 text-slate-300">{row.field_path}</td>
                    <td className="py-2 pr-3">{String(row.invoice_value ?? "—")}</td>
                    <td className="py-2 pr-3">{String(row.bol_value ?? "—")}</td>
                    <td className="py-2 pr-3">
                      <Chip tone={toneForStatus(row.status)}>{row.status}</Chip>
                    </td>
                    <td className="py-2 text-slate-400">{row.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Identity evidence</h2>
        {identities.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">No identity resolution yet.</p>
        ) : (
          identities.map((id, idx) => (
            <div key={idx} className="mt-3 rounded border border-slate-800 p-3 text-sm">
              <p className="font-medium text-slate-100">
                {id.role}: {id.normalized_name ?? id.raw_name}
              </p>
              <p className="text-amber-100/90">{id.resolution_status}</p>
            </div>
          ))
        )}
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Findings</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-3">
          {findings.length === 0 ? (
            <p className="text-sm text-slate-500">No findings yet — process the case.</p>
          ) : (
            findings.map((f) => (
              <article key={f.check_id} className="rounded border border-slate-800 p-3">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-sm font-medium text-slate-100">{f.check_id}</h3>
                  <Chip tone={toneForStatus(f.status)}>{f.status}</Chip>
                </div>
                <p className="mt-2 text-sm text-slate-300">{f.reason}</p>
              </article>
            ))
          )}
        </div>
      </section>

      <section className="rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-lg font-semibold text-slate-50">Audit timeline</h2>
        <ol className="mt-3 space-y-2 border-l border-slate-700 pl-4 text-sm">
          {audit.map((ev, i) => (
            <li key={i}>
              <p className="font-mono text-[11px] text-slate-500">
                {ev.created_at ?? ev.at ?? ""} · {ev.actor}
              </p>
              <p className="text-slate-200">{ev.event_type}</p>
            </li>
          ))}
        </ol>
      </section>
    </main>
  );
}
