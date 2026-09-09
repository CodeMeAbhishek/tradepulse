import type {
  AuditEvent,
  CaseRecord,
  CaseSummary,
  RuleResult,
  WorkbenchSnapshot,
} from "@/lib/api/client";
import type {
  DocSlot,
  Finding,
  FindingTone,
  IdentityCard,
  Profile,
  ReconRow,
  RiskRoute,
  TradeCase,
  WorkflowState,
} from "@/lib/demo/store";
import { resolveSourceLinks } from "@/lib/sources/resolve";
import { CaseStatus, ReadinessRoute, CheckStatus } from "../../../../packages/contracts/types";
import {
  FINDING_TITLES,
  DOC_LABELS,
  FIELD_LABELS,
  IDENTITY_OUTCOMES,
  AUDIT_ACTIONS,
  AGENT_LABELS,
  statusLabel,
  policyLabel,
} from "../status-labels";

function asProfile(p: string): Profile {
  const allowed: Profile[] = [
    "INVOICE_ONLY_PRE_REVIEW",
    "POST_SHIPMENT_DOCUMENT_REVIEW",
    "LC_DOCUMENT_REVIEW",
    "ENHANCED_TRADE_HOUSE_REVIEW",
  ];
  return (allowed.includes(p as Profile) ? p : "POST_SHIPMENT_DOCUMENT_REVIEW") as Profile;
}

function asWorkflow(s: string): WorkflowState {
  const map: Record<string, WorkflowState> = {
    INGESTED: CaseStatus.INGESTED,
    PROCESSING: CaseStatus.PROCESSING,
    PENDING_MAKER_REVIEW: CaseStatus.PENDING_MAKER_REVIEW,
    MAKER_APPROVED: CaseStatus.MAKER_APPROVED,
    CHECKER_APPROVED: CaseStatus.CHECKER_APPROVED,
    CHECKER_REJECTED: CaseStatus.CHECKER_REJECTED,
    INVESTIGATION_REQUIRED: CaseStatus.INVESTIGATION_REQUIRED,
    EXTRACTION_REVIEW: CaseStatus.DRAFT,
    PROCESSING_FAILED: CaseStatus.DRAFT,
  };
  return map[s] ?? CaseStatus.PENDING_MAKER_REVIEW;
}

function asRisk(r: string | null | undefined): RiskRoute {
  if (!r) return ReadinessRoute.READY_FOR_HUMAN_REVIEW;
  const known: RiskRoute[] = [
    ReadinessRoute.READY_FOR_HUMAN_REVIEW,
    ReadinessRoute.DOCUMENT_PACK_INCOMPLETE,
    ReadinessRoute.EXTRACTION_REVIEW_REQUIRED,
    ReadinessRoute.MAKER_REVIEW_REQUIRED,
    ReadinessRoute.HIGH_RISK_ESCALATION,
    ReadinessRoute.DATA_REVIEW_REQUIRED,
  ];
  return known.includes(r as RiskRoute) ? (r as RiskRoute) : ReadinessRoute.DATA_REVIEW_REQUIRED;
}

function toneForStatus(status: string): FindingTone {
  if (status === CheckStatus.PASS) return "clear";
  if (status === CheckStatus.DATA_UNAVAILABLE || status === CheckStatus.NOT_APPLICABLE) return "info";
  if (status === CheckStatus.FAIL) return "block";
  return "review";
}


function mapFinding(f: RuleResult): Finding {
  const sources = resolveSourceLinks(f.data_sources);
  return {
    id: f.check_id,
    title: FINDING_TITLES[f.check_id] || f.check_id.replaceAll("_", " "),
    tone: toneForStatus(f.status),
    statusLabel: statusLabel(f.status),
    summary: f.reason,
    action: f.recommended_action || "Human review required when status is not Clear.",
    source:
      sources.map((s) => s.label).join(" | ") ||
      f.rule_reference ||
      f.rule_pack_version,
    sources:
      sources.length > 0
        ? sources
        : f.rule_reference
          ? [{ label: f.rule_reference, platform: null, url: null }]
          : undefined,
  };
}

function mapRecon(wb: WorkbenchSnapshot | undefined): ReconRow[] {
  const comps = wb?.reconciliation?.comparisons;
  if (!comps?.length) {
    if (wb?.reconciliation?.status === "NOT_AVAILABLE") {
      return [
        {
          field: "Transport reconciliation",
          invoice: "Invoice present",
          bol: null,
          status: "NOT_AVAILABLE",
          note: wb.reconciliation.reason,
        },
      ];
    }
    return [];
  }
  return comps.map((c) => ({
    field: FIELD_LABELS[c.field_path] || c.field_path.replaceAll(".", " · ").replaceAll("_", " "),
    invoice: c.invoice_value == null ? "—" : String(c.invoice_value),
    bol: c.bol_value == null ? null : String(c.bol_value),
    status:
      c.status === "PASS"
        ? "MATCH"
        : c.status === "NOT_AVAILABLE" || c.status === "NOT_APPLICABLE"
          ? "NOT_AVAILABLE"
          : "MISMATCH",
    note: c.reason,
  }));
}

function mapDocs(wb: WorkbenchSnapshot | undefined, profile: Profile): DocSlot[] {
  const reqs = wb?.policy?.requirements as
    | Array<{
        document_type: string;
        state?: string;
        requirement?: string;
        provided: boolean;
        blocker?: boolean;
        blocks_completeness?: boolean;
      }>
    | undefined;
  if (reqs?.length) {
    return reqs.map((r) => {
      const raw = (r.state || r.requirement || "OPTIONAL").toUpperCase();
      const policy = (
        raw === "REQUIRED"
          ? "REQUIRED"
          : raw === "OPTIONAL"
            ? "OPTIONAL"
            : raw === "NOT_APPLICABLE"
              ? "NOT_APPLICABLE"
              : "CONDITIONALLY_REQUIRED"
      ) as DocSlot["policy"];
      return {
        type: r.document_type,
        label: DOC_LABELS[r.document_type] || r.document_type.replaceAll("_", " "),
        policy,
        provided: r.provided,
        blocker: Boolean(r.blocker ?? r.blocks_completeness),
      };
    });
  }
  const uploaded = new Set((wb?.documents || []).map((d) => d.document_type));
  return [
    {
      type: "commercial_invoice",
      label: "Commercial invoice",
      policy: "REQUIRED",
      provided: uploaded.has("commercial_invoice"),
      blocker: true,
    },
    {
      type: "bill_of_lading",
      label: "Bill of lading",
      policy:
        profile === "INVOICE_ONLY_PRE_REVIEW"
          ? "NOT_APPLICABLE"
          : profile === "POST_SHIPMENT_DOCUMENT_REVIEW" ||
              profile === "ENHANCED_TRADE_HOUSE_REVIEW"
            ? "REQUIRED"
            : "CONDITIONALLY_REQUIRED",
      provided: uploaded.has("bill_of_lading"),
      blocker: profile !== "INVOICE_ONLY_PRE_REVIEW",
    },
  ];
}

function mapIdentity(record: CaseRecord, wb: WorkbenchSnapshot | undefined): IdentityCard {
  const id = (wb?.identities || record.identities || [])[0];
  if (!id) {
    return {
      rawName: wb?.seller_name || "—",
      normalizedName: wb?.seller_name || "—",
      leiOnDocument: null,
      candidateName: null,
      candidateLei: null,
      nameSimilarity: null,
      resolutionStatus: "IDENTITY_UNRESOLVED",
      outcome: "Identity unresolved",
      action: "Process the case after uploading an invoice to resolve identity.",
      vlei: "vLEI check not enabled for this prototype",
    };
  }
  const cand = id.registry_candidates[0];
  const leiFromEvidence = id.lei?.lei ?? null;
  return {
    rawName: id.raw_name || "—",
    normalizedName: id.normalized_name || id.raw_name || "—",
    leiOnDocument: leiFromEvidence,
    candidateName: id.lei?.legal_name || cand?.candidate_name || null,
    candidateLei: id.lei?.lei || cand?.stable_identifier || null,
    nameSimilarity: cand?.score != null ? Math.round(cand.score * 100) : null,
    resolutionStatus: id.resolution_status || null,
    outcome: IDENTITY_OUTCOMES[id.resolution_status] || id.resolution_status.replaceAll("_", " "),
    action:
      id.resolution_status === "IDENTITY_VERIFIED_BY_LEI"
        ? "Document LEI matches the GLEIF registry record."
        : id.resolution_status === "POTENTIAL_ENTITY_MATCH_REVIEW"
          ? "Request an LEI or other stable identifier — name similarity alone is not proof."
          : "Provide an LEI or registry evidence when available.",
    vlei: id.vlei
      ? id.vlei.status === "NOT_CONFIGURED"
        ? "vLEI check not enabled for this prototype"
        : `vLEI status: ${id.vlei.status.replaceAll("_", " ").toLowerCase()}${
            id.vlei.data_label ? ` · ${id.vlei.data_label}` : ""
          }`
      : "vLEI check not enabled for this prototype",
  };
}

function humanAuditDetail(eventType: string, payload?: Record<string, unknown>): string {
  if (!payload || Object.keys(payload).length === 0) return "";
  if (eventType === "DOCUMENT_UPLOADED") {
    const type = String(payload.document_type || "document").replaceAll("_", " ");
    const name = payload.filename ? String(payload.filename) : null;
    const stored = payload.storage_uri ? "Stored securely." : "";
    return [name ? `${type}: ${name}` : type, stored].filter(Boolean).join(" · ");
  }
  if (eventType === "CASE_PROCESSED") {
    const route = payload.risk_route
      ? String(payload.risk_route).replaceAll("_", " ").toLowerCase()
      : null;
    const count = payload.finding_count != null ? `${payload.finding_count} findings` : null;
    return [route, count].filter(Boolean).join(" · ");
  }
  if (eventType === "CASE_STATE_TRANSITION") {
    const from = payload.from_state ? String(payload.from_state).replaceAll("_", " ") : "?";
    const to = payload.to_state ? String(payload.to_state).replaceAll("_", " ") : "?";
    return `${from} → ${to}`;
  }
  if (eventType === "CASE_CREATED") {
    const profile = payload.transaction_profile
      ? String(payload.transaction_profile).replaceAll("_", " ").toLowerCase()
      : null;
    return profile ? `Profile: ${profile}` : "";
  }
  // Avoid dumping raw JSON to officers.
  const keys = Object.keys(payload).slice(0, 3);
  return keys.map((k) => `${k.replaceAll("_", " ")}: ${String(payload[k])}`).join(" · ");
}

function mapAudit(events: AuditEvent[]): TradeCase["audit"] {
  return events.map((e, i) => ({
    id: e.event_id || `a-${i}`,
    at:
      (e as { occurred_at?: string }).occurred_at ||
      e.timestamp ||
      e.created_at ||
      new Date().toISOString(),
    actor: e.actor === "system" ? "System" : e.actor,
    action: AUDIT_ACTIONS[e.event_type] || e.event_type.replaceAll("_", " "),
    detail: humanAuditDetail(e.event_type, e.payload),
  }));
}

type AgentTraceRaw = {
  agent_name?: string;
  status?: string;
  round?: number;
  notes?: string | null;
  claims?: unknown[];
  challenges?: unknown[];
};

function mapAgentTrace(wb: WorkbenchSnapshot | undefined): TradeCase["agentTrace"] {
  const raw = (wb as { agent_trace?: AgentTraceRaw[] } | undefined)?.agent_trace;
  const provider = (wb as { extraction_provider?: string } | undefined)?.extraction_provider;
  const model = (wb as { extraction_model?: string } | undefined)?.extraction_model;
  if (!raw?.length) {
    return [
      {
        agent: "Document intelligence",
        status: "Pending",
        summary:
          "No agent run recorded yet. Process the case after uploading an invoice. Agent consensus is never a compliance approval.",
      },
    ];
  }
  const steps = raw.map((step) => {
    const name = AGENT_LABELS[step.agent_name || ""] || step.agent_name || "Agent";
    const claims = Array.isArray(step.claims) ? step.claims.length : 0;
    const challenges = Array.isArray(step.challenges) ? step.challenges.length : 0;
    const bits = [
      step.round != null ? `Round ${step.round}` : null,
      claims ? `${claims} claim(s)` : null,
      challenges ? `${challenges} challenge(s)` : null,
      step.notes || null,
    ].filter(Boolean);
    return {
      agent: name,
      status: statusLabel(step.status || "COMPLETE"),
      summary: bits.join(" · ") || "Step recorded. No private chain-of-thought is stored.",
    };
  });
  if (provider || model) {
    steps.push({
      agent: "Extraction source",
      status: "Info",
      summary: [provider, model].filter(Boolean).join(" · ") +
        ". Structured output is validated before use. Agent consensus ≠ compliance approval.",
    });
  }
  return steps;
}

export function summaryToTradeCase(s: CaseSummary): TradeCase {
  return {
    id: s.case_id,
    reference: s.case_id,
    counterparty: s.assignee || "—",
    corridor: "—",
    profile: asProfile(s.transaction_profile),
    workflow: asWorkflow(s.state),
    riskRoute: asRisk(s.risk_route),
    amount: "—",
    currency: "USD",
    slaLabel: `${s.document_count} docs`,
    updatedAt: s.updated_at,
    scenario: "custom",
    docs: [],
    recon: [],
    findings: [],
    identity: {
      rawName: "—",
      normalizedName: "—",
      leiOnDocument: null,
      candidateName: null,
      candidateLei: null,
      nameSimilarity: null,
      resolutionStatus: "IDENTITY_UNRESOLVED",
      outcome: "Identity unresolved",
      action: "Open case for details",
      vlei: "vLEI check not enabled for this prototype",
    },
    agentTrace: [{ agent: "API", status: "List", summary: "Loaded from case queue" }],
    audit: [],
    makerNote: null,
    checkerNote: null,
  };
}

export function recordToTradeCase(
  record: CaseRecord,
  audit: AuditEvent[] = [],
  policy?: WorkbenchSnapshot["policy"],
): TradeCase {
  const wb = (record.metadata?.last_workbench as WorkbenchSnapshot | undefined) || {
    identities: record.identities,
    risk_route: record.risk_route,
    policy,
  };
  const amount =
    wb.total_amount != null ? Number(wb.total_amount).toLocaleString("en-US") : "—";

  return {
    id: record.case_id,
    reference: record.case_id,
    counterparty: wb.seller_name || record.assignee || "—",
    corridor: record.corridor || "—",
    profile: asProfile(record.transaction_profile),
    workflow: asWorkflow(record.state),
    riskRoute: asRisk(wb.risk_route || record.risk_route),
    amount,
    currency: wb.currency || "USD",
    slaLabel: `v${record.version}`,
    updatedAt: record.updated_at,
    scenario: "custom",
    docs: mapDocs(wb, asProfile(record.transaction_profile)),
    recon: mapRecon(wb),
    findings: (wb.findings || []).map(mapFinding),
    identity: mapIdentity(record, wb),
    agentTrace: mapAgentTrace(wb),
    audit: mapAudit(audit),
    makerNote: null,
    checkerNote: null,
  };
}
