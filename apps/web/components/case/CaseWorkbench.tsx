"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api/client";
import { useDemo } from "@/lib/demo/DemoProvider";
import { InvestigationCanvas } from "@/components/case/InvestigationCanvas";
import {
  ladderFromStatus,
  type IdentityLadderModel,
} from "@/components/case/IdentityLadder";
import { RiskChip, WorkflowChip } from "@/components/ui/StatusChips";
import { profileLabel, type TradeCase } from "@/lib/demo/store";
import { CaseStatus } from "../../../../packages/contracts/types";
import {
  ChecksTab,
  DocsTab,
  CompareTab,
  PartyTab,
  HowCheckedTab,
  DecideTab,
} from "@/components/case/tabs";
import { CaseProvider } from "@/components/case/CaseContext";

const TABS = [
  { id: "investigate", label: "Investigate" },
  { id: "checks", label: "Checks" },
  { id: "docs", label: "Docs" },
  { id: "compare", label: "Compare" },
  { id: "party", label: "Party" },
  { id: "how-checked", label: "How we checked" },
  { id: "decide", label: "Decide" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function buildBrief(live: TradeCase): { bullets: string[]; cta: string } {
  const bullets: string[] = [];
  const mismatch = live.recon.find((r) => r.status === "MISMATCH");
  if (mismatch) {
    bullets.push(
      `Document mismatch: invoice ${mismatch.invoice} vs bill of lading ${mismatch.bol ?? "—"}.`,
    );
  }
  const price = live.findings.find((f) => /price/i.test(f.title));
  if (price && price.tone !== "clear") {
    bullets.push(`Price check needs review (${price.statusLabel}).`);
  } else if (price) {
    bullets.push("Price check is within tolerance of the market reference.");
  }
  const screening = live.findings.find((f) => /screen/i.test(f.title));
  if (screening?.tone === "clear") {
    bullets.push("Screening: no potential match on the configured list.");
  } else if (screening) {
    bullets.push(`Screening: ${screening.statusLabel} — review required.`);
  }
  const idUpper = live.identity.outcome.toUpperCase();
  if (idUpper.includes("VERIFIED") || idUpper.includes("SUPPORTED")) {
    bullets.push(`Party identity: ${live.identity.outcome}.`);
  } else {
    bullets.push(`Party identity needs attention: ${live.identity.outcome}.`);
  }
  while (bullets.length > 3) bullets.pop();
  if (bullets.length === 0) {
    bullets.push("No open alerts yet — review the packet, then decide.");
  }

  let cta = "Open Decide when you are ready to act as maker or checker.";
  if (mismatch && price && price.tone !== "clear") {
    cta = "Resolve the quantity mismatch, then review price plausibility on Decide.";
  } else if (mismatch) {
    cta = "Resolve the document mismatch on Compare, then continue to Decide.";
  } else if (price && price.tone !== "clear") {
    cta = "Review price plausibility, then continue to Decide.";
  } else if (live.workflow === CaseStatus.PENDING_MAKER_REVIEW) {
    cta = "Packet is ready for maker action on Decide.";
  }

  return { bullets, cta };
}

function buildDemoExaminerPack(live: TradeCase) {
  const ladder = ladderFromStatus(live.identity.resolutionStatus);
  return {
    pack_version: "1.0.0",
    generated_at: new Date().toISOString(),
    disclaimer:
      "Examiner case pack for human review. Not a Customs filing, payment instruction, or autonomous compliance decision.",
    safety_notes: [
      "TradePulse is decision-support software. It does not approve, reject, clear, sanction, or find fraud.",
      "Fuzzy name matching is never identity proof.",
      "If information is missing or not applicable, that must never be treated as a pass.",
      "Automated agreement on extracted fields is a confidence signal only — never a compliance conclusion.",
      "Checker approval cannot precede maker approval.",
    ],
    case: {
      case_id: live.id,
      reference: live.reference,
      state: live.workflow,
      corridor: live.corridor,
      risk_route: live.riskRoute,
      profile: live.profile,
      data_label: "synthetic",
    },
    documents: live.docs.map((d) => ({
      document_type: d.type,
      label: d.label,
      provided: d.provided,
      requirement: d.policy,
    })),
    identity_ladders: [
      {
        ...ladder,
        role: "SELLER",
        party_name: live.identity.normalizedName,
      },
    ],
    findings: live.findings.map((f) => ({
      check_id: f.id,
      title: f.title,
      status: f.statusLabel,
      reason: f.summary,
      recommended_action: f.action,
      source: f.source,
    })),
    reconciliation: live.recon,
    agent_trace_summary: live.agentTrace,
    audit_trail: live.audit,
  };
}

function downloadJson(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function CaseWorkbench({ caseId }: { caseId: string }) {
  const [tab, setTab] = useState<TabId>("investigate");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState<Record<string, boolean>>({});
  const [ladder, setLadder] = useState<IdentityLadderModel | null>(null);
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

  useEffect(() => {
    if (!live) {
      setLadder(null);
      return;
    }
    if (mode !== "api") {
      setLadder(ladderFromStatus(live.identity.resolutionStatus));
      return;
    }
    let cancelled = false;
    void api
      .identityLadder(caseId)
      .then((rows) => {
        if (cancelled) return;
        if (rows[0]) {
          setLadder({
            role: rows[0].role,
            party_name: rows[0].party_name,
            resolution_status: rows[0].resolution_status,
            current_rung_id: rows[0].current_rung_id,
            side_state: rows[0].side_state,
            safety_note: rows[0].safety_note,
            steps: rows[0].steps,
          });
        } else {
          setLadder(ladderFromStatus(live.identity.resolutionStatus));
        }
      })
      .catch(() => {
        if (!cancelled) setLadder(ladderFromStatus(live.identity.resolutionStatus));
      });
    return () => {
      cancelled = true;
    };
  }, [caseId, live, mode, live?.identity.resolutionStatus, live?.updatedAt]);

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

  const brief = useMemo(() => (live ? buildBrief(live) : null), [live]);

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

  const downloadExaminerPack = () =>
    void run(async () => {
      if (mode === "api") {
        const pack = await api.examinerPack(caseId);
        downloadJson(`${caseId}-examiner-pack.json`, pack);
        return;
      }
      downloadJson(`${caseId}-examiner-pack.json`, buildDemoExaminerPack(live));
    });

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
              Case review {mode === "api" ? "· connected" : "· demo"}
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
            <button
              type="button"
              disabled={busy}
              onClick={downloadExaminerPack}
              className="rounded-lg border border-[var(--tp-line)] bg-white px-3 py-1.5 text-xs font-medium text-[var(--tp-navy)] hover:bg-slate-50 disabled:opacity-40"
            >
              Download examiner pack
            </button>
          </div>
        </div>

        {mismatch ? (
          <div className="tp-banner-mismatch mt-4 rounded-lg px-4 py-3">
            <p className="text-sm font-semibold tracking-wide">
              Flagged — document discrepancy · human review required
            </p>
            <p className="mt-1 text-sm text-white/95">
              Invoice: <strong>{mismatch.invoice}</strong> · Bill of lading:{" "}
              <strong>{mismatch.bol}</strong>
            </p>
            <p className="mt-2 text-sm text-white/90">{mismatch.note}</p>
          </div>
        ) : null}

        {brief ? (
          <div className="mt-4 flex flex-col gap-3 rounded-lg border border-[var(--tp-line)] bg-[var(--tp-bg)] px-4 py-3 sm:flex-row sm:items-end sm:justify-between">
            <div className="min-w-0">
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--tp-muted)]">
                Case brief
              </p>
              <ul className="mt-2 space-y-1.5 text-sm text-[var(--tp-ink)]">
                {brief.bullets.map((b) => (
                  <li key={b} className="flex gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--tp-navy)]" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-sm font-medium text-[var(--tp-teal)]">{brief.cta}</p>
            </div>
            <button
              type="button"
              onClick={() => setTab("decide")}
              className="shrink-0 rounded-lg bg-[var(--tp-navy)] px-4 py-2 text-sm font-medium text-white"
            >
              Go to Decide
            </button>
          </div>
        ) : null}

        {busy ? <ProcessingRail /> : null}
        {err ? <p className="mt-3 text-sm text-rose-700">{err}</p> : null}
      </header>

      <CaseProvider
        value={{
          live,
          mode,
          busy,
          err,
          ladder,
          maker,
          checker,
          run,
        }}
      >
        <div className="flex flex-wrap gap-1 border-b border-[var(--tp-line)] pb-2">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTab(t.id)}
              className={
                tab === t.id
                  ? "rounded-md bg-[var(--tp-navy)] px-3 py-1.5 text-sm font-medium text-white"
                  : "rounded-md px-3 py-1.5 text-sm text-[var(--tp-muted)] hover:bg-white"
              }
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "investigate" ? <InvestigationCanvas tradeCase={live} /> : null}

        {tab === "checks" ? (
          <ChecksTab
            findings={live.findings}
            showEvidence={showEvidence}
            setShowEvidence={setShowEvidence}
          />
        ) : null}

        {tab === "docs" ? <DocsTab /> : null}

        {tab === "compare" ? <CompareTab reconBanner={reconBanner} /> : null}

        {tab === "party" ? <PartyTab /> : null}

        {tab === "how-checked" ? <HowCheckedTab /> : null}

        {tab === "decide" ? (
          <DecideTab note={note} setNote={setNote} />
        ) : null}
      </CaseProvider>
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
