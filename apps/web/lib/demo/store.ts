/**
 * In-browser live demo store for a sellable TradePulse workbench UX.
 * No LLM/GLEIF/sanctions calls from the browser — fixtures only.
 * Persist to localStorage so the product feels stateful for demos.
 */

export type Profile =
  | "INVOICE_ONLY_PRE_REVIEW"
  | "POST_SHIPMENT_DOCUMENT_REVIEW"
  | "LC_DOCUMENT_REVIEW"
  | "ENHANCED_TRADE_HOUSE_REVIEW";

export type RiskRoute =
  | "READY_FOR_HUMAN_REVIEW"
  | "REVIEW_REQUIRED"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "MAKER_REVIEW_REQUIRED"
  | "HIGH_RISK_ESCALATION"
  | "DATA_REVIEW_REQUIRED";

export type WorkflowState =
  | "DRAFT"
  | "INGESTED"
  | "PROCESSING"
  | "PENDING_MAKER"
  | "MAKER_APPROVED"
  | "CHECKER_APPROVED"
  | "CHECKER_REJECTED"
  | "INVESTIGATION_REQUIRED";

export type FindingTone = "clear" | "review" | "block" | "info";

export interface DocSlot {
  type: string;
  label: string;
  policy: "REQUIRED" | "CONDITIONALLY_REQUIRED" | "OPTIONAL" | "NOT_APPLICABLE";
  provided: boolean;
  blocker: boolean;
}

export interface ReconRow {
  field: string;
  invoice: string;
  bol: string | null;
  status: "MATCH" | "MISMATCH" | "NOT_AVAILABLE";
  note: string;
}

export interface Finding {
  id: string;
  title: string;
  tone: FindingTone;
  statusLabel: string;
  summary: string;
  action: string;
  source: string;
}

export interface IdentityCard {
  rawName: string;
  normalizedName: string;
  leiOnDocument: string | null;
  candidateName: string | null;
  candidateLei: string | null;
  nameSimilarity: number | null;
  /** Machine status code when known (API); used for identity ladder. */
  resolutionStatus: string | null;
  outcome: string;
  action: string;
  vlei: string;
}

export interface AgentStep {
  agent: string;
  status: string;
  summary: string;
}

export interface AuditEvent {
  id: string;
  at: string;
  actor: string;
  action: string;
  detail: string;
}

export interface TradeCase {
  id: string;
  reference: string;
  counterparty: string;
  corridor: string;
  profile: Profile;
  workflow: WorkflowState;
  riskRoute: RiskRoute;
  amount: string;
  currency: string;
  slaLabel: string;
  updatedAt: string;
  scenario: "clean" | "mismatch" | "duplicate" | "incomplete" | "custom";
  docs: DocSlot[];
  recon: ReconRow[];
  findings: Finding[];
  identity: IdentityCard;
  agentTrace: AgentStep[];
  audit: AuditEvent[];
  makerNote: string | null;
  checkerNote: string | null;
}

const STORAGE_KEY = "tradepulse.demo.v1";

function nowIso() {
  return new Date().toISOString();
}

function uid(prefix: string) {
  return `${prefix}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
}

function seedCases(): TradeCase[] {
  const t = nowIso();
  return [
    {
      id: "case-clean-001",
      reference: "TP-2026-2201",
      counterparty: "Gulf Precision Trading LLC",
      corridor: "IN → AE",
      profile: "POST_SHIPMENT_DOCUMENT_REVIEW",
      workflow: "PENDING_MAKER",
      riskRoute: "READY_FOR_HUMAN_REVIEW",
      amount: "1,250,000",
      currency: "USD",
      slaLabel: "Due in 6h",
      updatedAt: t,
      scenario: "clean",
      docs: [
        { type: "INVOICE", label: "Commercial Invoice", policy: "REQUIRED", provided: true, blocker: true },
        { type: "BOL", label: "Bill of Lading", policy: "REQUIRED", provided: true, blocker: true },
        { type: "PL", label: "Packing List", policy: "OPTIONAL", provided: false, blocker: false },
      ],
      recon: [
        { field: "Quantity", invoice: "500 MT", bol: "500 MT", status: "MATCH", note: "Aligned" },
        { field: "Seller / Shipper", invoice: "Gulf Precision Trading LLC", bol: "Gulf Precision Trading LLC", status: "MATCH", note: "Aligned" },
        { field: "Port of loading", invoice: "Mundra, IN", bol: "Mundra, IN", status: "MATCH", note: "Aligned" },
        { field: "Goods", invoice: "Copper cathodes Grade A", bol: "Copper cathodes Grade A", status: "MATCH", note: "Aligned" },
      ],
      findings: [
        {
          id: "f1",
          title: "Screening",
          tone: "clear",
          statusLabel: "No potential match",
          summary: "Demo watchlist snapshot — no candidate hit for seller.",
          action: "Proceed with standard human review.",
          source: "DEMO_MOCK_WATCHLIST · snap-demo-01",
        },
        {
          id: "f2",
          title: "Price plausibility",
          tone: "info",
          statusLabel: "Within band",
          summary: "Unit price within static demo benchmark band for HS fixture.",
          action: "No price escalation required.",
          source: "STATIC_DEMO_PRICE_REF",
        },
        {
          id: "f3",
          title: "Duplicate signal",
          tone: "clear",
          statusLabel: "No prior hit",
          summary: "Local hash index has no matching invoice+BoL fingerprint.",
          action: "Continue.",
          source: "LOCAL_HASH_DEMO",
        },
      ],
      identity: {
        rawName: "Gulf Precision Trading L.L.C.",
        normalizedName: "Gulf Precision Trading LLC",
        leiOnDocument: "984500GULFPRE000001",
        candidateName: "Gulf Precision Trading LLC",
        candidateLei: "984500GULFPRE000001",
        nameSimilarity: 99,
        resolutionStatus: "IDENTITY_VERIFIED_BY_LEI",
        outcome: "Identity verified by LEI",
        action: "Exact document LEI matches GLEIF fixture record.",
        vlei: "VLEI verification: Not configured in prototype",
      },
      agentTrace: [
        { agent: "Extractor", status: "COMPLETE", summary: "Invoice fields extracted with page evidence." },
        { agent: "Validator", status: "COMPLETE", summary: "Independent validation agrees on critical fields." },
        { agent: "Challenger", status: "COMPLETE", summary: "No material challenges." },
        { agent: "Arbiter", status: "COMPLETE", summary: "Agreement accepted — extraction confidence only." },
        { agent: "Cross-document reconciler", status: "COMPLETE", summary: "Invoice ↔ BoL fields align." },
      ],
      audit: [
        { id: "a1", at: t, actor: "system", action: "CASE_SEEDED", detail: "Clean golden case loaded" },
        { id: "a2", at: t, actor: "system", action: "CASE_PROCESSED", detail: "Findings generated from fixtures" },
      ],
      makerNote: null,
      checkerNote: null,
    },
    {
      id: "case-mismatch-002",
      reference: "TP-2026-2208",
      counterparty: "Sahara Metals FZE",
      corridor: "IN → AE",
      profile: "POST_SHIPMENT_DOCUMENT_REVIEW",
      workflow: "PENDING_MAKER",
      riskRoute: "MAKER_REVIEW_REQUIRED",
      amount: "890,400",
      currency: "USD",
      slaLabel: "Due in 2h",
      updatedAt: t,
      scenario: "mismatch",
      docs: [
        { type: "INVOICE", label: "Commercial Invoice", policy: "REQUIRED", provided: true, blocker: true },
        { type: "BOL", label: "Bill of Lading", policy: "REQUIRED", provided: true, blocker: true },
        { type: "PL", label: "Packing List", policy: "OPTIONAL", provided: false, blocker: false },
      ],
      recon: [
        {
          field: "Quantity",
          invoice: "500 cartons",
          bol: "350 cartons",
          status: "MISMATCH",
          note: "Cross-document quantity discrepancy — review required",
        },
        { field: "Seller / Shipper", invoice: "Sahara Metals FZE", bol: "Sahara Metals FZE", status: "MATCH", note: "Aligned" },
        { field: "Port of loading", invoice: "Jebel Ali, AE", bol: "Jebel Ali", status: "MATCH", note: "Compatible" },
        { field: "Goods", invoice: "Copper cathodes Grade A", bol: "Copper cathodes Grade A", status: "MATCH", note: "Aligned" },
      ],
      findings: [
        {
          id: "m1",
          title: "Document discrepancy",
          tone: "review",
          statusLabel: "Review required",
          summary: "Invoice quantity 500 cartons (p.1) vs Bill of Lading 350 cartons (p.1).",
          action:
            "Request clarification, corrected document, or partial-shipment explanation before presentation.",
          source: "RECONCILER_FIXTURE · dual-document evidence",
        },
        {
          id: "m2",
          title: "Screening",
          tone: "clear",
          statusLabel: "No potential match",
          summary: "No demo watchlist candidate for seller.",
          action: "Continue after quantity discrepancy is resolved.",
          source: "DEMO_MOCK_WATCHLIST",
        },
      ],
      identity: {
        rawName: "Sahara Metals FZE",
        normalizedName: "Sahara Metals FZE",
        leiOnDocument: "984500SAHARA00000012",
        candidateName: "Sahara Metals FZE",
        candidateLei: "984500SAHARA00000012",
        nameSimilarity: 100,
        resolutionStatus: "IDENTITY_VERIFIED_BY_LEI",
        outcome: "Identity verified by LEI",
        action: "Exact LEI match on fixture. Quantity issue is separate from identity.",
        vlei: "VLEI verification: Not configured in prototype",
      },
      agentTrace: [
        { agent: "Extractor", status: "COMPLETE", summary: "Invoice qty 500 cartons (p.1)." },
        { agent: "Validator", status: "COMPLETE", summary: "Confirms invoice qty 500 cartons." },
        { agent: "Challenger", status: "COMPLETE", summary: "CROSS_DOCUMENT_CONFLICT on quantity vs BoL 350." },
        { agent: "Arbiter", status: "REVIEW_REQUIRED", summary: "Cannot reconcile without evidence of correction — human review." },
        { agent: "Cross-document reconciler", status: "REVIEW_REQUIRED", summary: "Quantity mismatch retained with dual evidence." },
      ],
      audit: [
        { id: "b1", at: t, actor: "system", action: "CASE_SEEDED", detail: "Mismatch golden case" },
        { id: "b2", at: t, actor: "system", action: "RECON_MISMATCH", detail: "500 vs 350 cartons" },
      ],
      makerNote: null,
      checkerNote: null,
    },
    {
      id: "case-dup-003",
      reference: "TP-2026-2215",
      counterparty: "Eastern Horizon Logistics Co.",
      corridor: "IN → GB",
      profile: "ENHANCED_TRADE_HOUSE_REVIEW",
      workflow: "PENDING_MAKER",
      riskRoute: "MAKER_REVIEW_REQUIRED",
      amount: "412,750",
      currency: "USD",
      slaLabel: "Due today",
      updatedAt: t,
      scenario: "duplicate",
      docs: [
        { type: "INVOICE", label: "Commercial Invoice", policy: "REQUIRED", provided: true, blocker: true },
        { type: "BOL", label: "Bill of Lading", policy: "REQUIRED", provided: true, blocker: true },
        { type: "COO", label: "Certificate of Origin", policy: "CONDITIONALLY_REQUIRED", provided: false, blocker: false },
      ],
      recon: [
        { field: "Quantity", invoice: "120 MT", bol: "120 MT", status: "MATCH", note: "Aligned" },
        { field: "Seller / Shipper", invoice: "Eastern Horizon Logistics Co.", bol: "Eastern Horizon Logistics Co.", status: "MATCH", note: "Aligned" },
        { field: "Port of loading", invoice: "Nhava Sheva, IN", bol: "Nhava Sheva, IN", status: "MATCH", note: "Aligned" },
      ],
      findings: [
        {
          id: "d1",
          title: "Duplicate submission signal",
          tone: "review",
          statusLabel: "Prior case referenced",
          summary:
            "This invoice/transport-reference combination was previously submitted in Case TP-2026-0099.",
          action: "This is a review signal, not proof of duplicate financing.",
          source: "LOCAL_HASH_DEMO · prior TP-2026-0099",
        },
        {
          id: "d2",
          title: "Price plausibility",
          tone: "review",
          statusLabel: "Variance indicator",
          summary: "Unit price variance vs static demo benchmark exceeds configured band.",
          action: "Treat as TBML risk indicator — not a fraud conclusion.",
          source: "STATIC_DEMO_PRICE_REF · price-snap-demo-01",
        },
        {
          id: "d3",
          title: "Screening",
          tone: "review",
          statusLabel: "Potential match",
          summary: "Fuzzy name candidate against DEMO/MOCK watchlist — not confirmed.",
          action: "Human review against authoritative source before any escalation language.",
          source: "DEMO_MOCK_WATCHLIST · potential match only",
        },
      ],
      identity: {
        rawName: "Eastern Horizon Logistics Co",
        normalizedName: "Eastern Horizon Logistics Co.",
        leiOnDocument: null,
        candidateName: "Eastern Horizon Logistics Limited",
        candidateLei: "549300EASTHORIZ00001",
        nameSimilarity: 92,
        resolutionStatus: "POTENTIAL_ENTITY_MATCH_REVIEW",
        outcome: "Potential entity match — review required",
        action: "Request LEI, CIN, or official company-registration evidence.",
        vlei: "VLEI verification: Not configured in prototype",
      },
      agentTrace: [
        { agent: "Extractor", status: "COMPLETE", summary: "Packet extracted." },
        { agent: "Validator", status: "COMPLETE", summary: "Critical fields validated." },
        { agent: "Challenger", status: "COMPLETE", summary: "No arithmetic conflict on this packet." },
        { agent: "Arbiter", status: "COMPLETE", summary: "Extraction accepted." },
        { agent: "Cross-document reconciler", status: "COMPLETE", summary: "Core fields align; compliance signals separate." },
      ],
      audit: [
        { id: "c1", at: t, actor: "system", action: "CASE_SEEDED", detail: "Duplicate/price golden case" },
        { id: "c2", at: t, actor: "system", action: "DUP_SIGNAL", detail: "Matched prior TP-2026-0099" },
      ],
      makerNote: null,
      checkerNote: null,
    },
  ];
}

export function loadCases(): TradeCase[] {
  if (typeof window === "undefined") return seedCases();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      const seeded = seedCases();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded));
      return seeded;
    }
    return JSON.parse(raw) as TradeCase[];
  } catch {
    return seedCases();
  }
}

export function saveCases(cases: TradeCase[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cases));
}

export function resetDemoData(): TradeCase[] {
  const seeded = seedCases();
  saveCases(seeded);
  return seeded;
}

export function profileLabel(p: Profile): string {
  const map: Record<Profile, string> = {
    INVOICE_ONLY_PRE_REVIEW: "Invoice-only pre-review",
    POST_SHIPMENT_DOCUMENT_REVIEW: "Post-shipment review",
    LC_DOCUMENT_REVIEW: "LC document review",
    ENHANCED_TRADE_HOUSE_REVIEW: "Enhanced trade-house",
  };
  return map[p];
}

export function riskLabel(r: RiskRoute): string {
  const map: Record<RiskRoute, string> = {
    READY_FOR_HUMAN_REVIEW: "Ready for human review",
    REVIEW_REQUIRED: "Review required",
    DOCUMENT_PACK_INCOMPLETE: "Document pack incomplete",
    MAKER_REVIEW_REQUIRED: "Maker review required",
    HIGH_RISK_ESCALATION: "High-risk escalation",
    DATA_REVIEW_REQUIRED: "Data review required",
  };
  return map[r] || r.replaceAll("_", " ");
}

export function workflowLabel(w: WorkflowState): string {
  const map: Partial<Record<WorkflowState, string>> = {
    DRAFT: "Draft",
    INGESTED: "Ingested",
    PROCESSING: "Processing",
    PENDING_MAKER: "Pending maker",
    MAKER_APPROVED: "Awaiting checker",
    CHECKER_APPROVED: "Checker approved",
    CHECKER_REJECTED: "Checker rejected",
    INVESTIGATION_REQUIRED: "Investigation required",
  };
  return map[w] || w.replaceAll("_", " ");
}

export function createCase(input: {
  counterparty: string;
  corridor: string;
  profile: Profile;
  includeBol: boolean;
}): TradeCase {
  const id = uid("CASE");
  const reference = `TP-2026-${Math.floor(1000 + Math.random() * 8000)}`;
  const t = nowIso();
  const bolRequired =
    input.profile === "POST_SHIPMENT_DOCUMENT_REVIEW" ||
    input.profile === "ENHANCED_TRADE_HOUSE_REVIEW";
  const bolProvided = input.includeBol;
  const packIncomplete = bolRequired && !bolProvided;

  const docs: DocSlot[] = [
    { type: "INVOICE", label: "Commercial Invoice", policy: "REQUIRED", provided: true, blocker: true },
    {
      type: "BOL",
      label: "Bill of Lading",
      policy: bolRequired ? "REQUIRED" : input.profile === "INVOICE_ONLY_PRE_REVIEW" ? "NOT_APPLICABLE" : "CONDITIONALLY_REQUIRED",
      provided: bolProvided,
      blocker: bolRequired,
    },
  ];
  if (input.profile === "LC_DOCUMENT_REVIEW") {
    docs.push({
      type: "LC",
      label: "Letter of Credit",
      policy: "REQUIRED",
      provided: false,
      blocker: true,
    });
  }

  const incomplete =
    packIncomplete ||
    (input.profile === "LC_DOCUMENT_REVIEW" && !docs.find((d) => d.type === "LC")?.provided);

  return {
    id,
    reference,
    counterparty: input.counterparty || "New counterparty",
    corridor: input.corridor || "IN → AE",
    profile: input.profile,
    workflow: incomplete ? "INGESTED" : "PENDING_MAKER",
    riskRoute: incomplete
      ? "DOCUMENT_PACK_INCOMPLETE"
      : input.profile === "INVOICE_ONLY_PRE_REVIEW" && !bolProvided
        ? "READY_FOR_HUMAN_REVIEW"
        : "READY_FOR_HUMAN_REVIEW",
    amount: "—",
    currency: "USD",
    slaLabel: "New",
    updatedAt: t,
    scenario: incomplete ? "incomplete" : "custom",
    docs,
    recon:
      !bolProvided
        ? [
            {
              field: "Transport reconciliation",
              invoice: "Invoice present",
              bol: null,
              status: "NOT_AVAILABLE",
              note:
                input.profile === "INVOICE_ONLY_PRE_REVIEW"
                  ? "Invoice-only profile — BoL reconciliation is NOT_AVAILABLE (not a pass)."
                  : "BoL missing — pack incomplete; transport check cannot pass.",
            },
          ]
        : [
            { field: "Quantity", invoice: "Pending extract", bol: "Pending extract", status: "MATCH", note: "Demo stub" },
          ],
    findings: incomplete
      ? [
          {
            id: uid("F"),
            title: "Document pack",
            tone: "block",
            statusLabel: "Document pack incomplete",
            summary: "Required document(s) missing for selected profile.",
            action: "Upload required documents before maker clear path.",
            source: "POLICY_FIXTURE",
          },
        ]
      : [
          {
            id: uid("F"),
            title: "Intake complete",
            tone: "info",
            statusLabel: "Ready for human review",
            summary: "Case created in demo store. Deep extraction integrations come later.",
            action: "Open workbench and run maker review.",
            source: "DEMO_STORE",
          },
        ],
    identity: {
      rawName: input.counterparty,
      normalizedName: input.counterparty,
      leiOnDocument: null,
      candidateName: null,
      candidateLei: null,
      nameSimilarity: null,
      resolutionStatus: "IDENTITY_UNRESOLVED",
      outcome: "Identity unresolved",
      action: "Provide LEI or registry evidence when available.",
      vlei: "VLEI verification: Not configured in prototype",
    },
    agentTrace: [
      { agent: "Extractor", status: "QUEUED", summary: "Awaiting deep integration — demo intake only." },
    ],
    audit: [
      { id: uid("A"), at: t, actor: "officer.demo", action: "CASE_CREATED", detail: `Profile ${input.profile}` },
    ],
    makerNote: null,
    checkerNote: null,
  };
}

export function applyMaker(
  cases: TradeCase[],
  caseId: string,
  decision: "approve" | "investigate",
  note: string,
): TradeCase[] {
  return cases.map((c) => {
    if (c.id !== caseId) return c;
    const t = nowIso();
    if (decision === "approve") {
      return {
        ...c,
        workflow: "MAKER_APPROVED",
        makerNote: note,
        updatedAt: t,
        audit: [
          ...c.audit,
          { id: uid("A"), at: t, actor: "maker.demo", action: "MAKER_APPROVE", detail: note || "Submitted to checker" },
        ],
      };
    }
    return {
      ...c,
      workflow: "INVESTIGATION_REQUIRED",
      riskRoute: "HIGH_RISK_ESCALATION",
      makerNote: note,
      updatedAt: t,
      audit: [
        ...c.audit,
        { id: uid("A"), at: t, actor: "maker.demo", action: "MAKER_INVESTIGATE", detail: note || "Escalated" },
      ],
    };
  });
}

export function applyChecker(
  cases: TradeCase[],
  caseId: string,
  decision: "approve" | "reject",
  note: string,
): TradeCase[] {
  return cases.map((c) => {
    if (c.id !== caseId) return c;
    if (c.workflow !== "MAKER_APPROVED") return c;
    const t = nowIso();
    if (decision === "approve") {
      return {
        ...c,
        workflow: "CHECKER_APPROVED",
        checkerNote: note,
        updatedAt: t,
        audit: [
          ...c.audit,
          { id: uid("A"), at: t, actor: "checker.demo", action: "CHECKER_APPROVE", detail: note || "Dual control complete" },
        ],
      };
    }
    return {
      ...c,
      workflow: "CHECKER_REJECTED",
      checkerNote: note,
      updatedAt: t,
      audit: [
        ...c.audit,
        { id: uid("A"), at: t, actor: "checker.demo", action: "CHECKER_REJECT", detail: note || "Returned" },
      ],
    };
  });
}
