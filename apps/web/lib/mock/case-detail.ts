import type { CaseWorkbenchDetail } from "./types";
import { getCaseProfileChecklist, getMockQueueCase } from "./queue";

function baseInvoiceFields(): CaseWorkbenchDetail["invoiceFields"] {
  return [
    {
      fieldPath: "seller.name",
      label: "Seller name",
      value: "Sahara Metals FZE",
      confidence: "HIGH",
      evidence: { page: 1, sourceText: "Seller: Sahara Metals FZE" },
    },
    {
      fieldPath: "buyer.name",
      label: "Buyer name",
      value: "Indicore Trading Pvt Ltd",
      confidence: "HIGH",
      evidence: { page: 1, sourceText: "Buyer: Indicore Trading Pvt Ltd" },
    },
    {
      fieldPath: "goods.description",
      label: "Goods",
      value: "Copper cathodes, Grade A",
      confidence: "MEDIUM",
      evidence: { page: 1, sourceText: "Copper cathodes Grade A" },
    },
    {
      fieldPath: "goods.quantity",
      label: "Quantity",
      value: "250 MT",
      confidence: "REVIEW_REQUIRED",
      evidence: { page: 1, sourceText: "Qty: 250 MT" },
    },
    {
      fieldPath: "shipment.port_of_loading",
      label: "Port of loading",
      value: "Jebel Ali, AE",
      confidence: "HIGH",
      evidence: { page: 1, sourceText: "POL: Jebel Ali" },
    },
    {
      fieldPath: "references.invoice_number",
      label: "Invoice number",
      value: "INV-SM-88421",
      confidence: "HIGH",
      evidence: { page: 1, sourceText: "Invoice No. INV-SM-88421" },
    },
  ];
}

function agentTraceAgreement(): CaseWorkbenchDetail["agentTrace"] {
  return [
    {
      round: 1,
      extractor: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "seller.name",
            proposedValue: "Sahara Metals FZE",
            reason: "Matched seller line on page 1",
            hasEvidence: true,
          },
        ],
      },
      validator: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "seller.name",
            proposedValue: "Sahara Metals FZE",
            reason: "Independent read agrees",
            hasEvidence: true,
          },
        ],
      },
      challenger: { status: "COMPLETE", challenges: [] },
      arbiter: {
        status: "COMPLETE",
        decisionSummary: "Agreement on seller.name with evidence.",
        agreement: true,
      },
    },
  ];
}

function agentTraceDisagreement(): CaseWorkbenchDetail["agentTrace"] {
  return [
    {
      round: 1,
      extractor: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "250 MT",
            reason: "Header quantity line",
            hasEvidence: true,
          },
        ],
      },
      validator: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "245 MT",
            reason: "Line-item sum differs from header",
            hasEvidence: true,
          },
        ],
      },
      challenger: {
        status: "COMPLETE",
        challenges: [
          {
            fieldPath: "goods.quantity",
            category: "ARITHMETIC_CONFLICT",
            reason: "Header 250 MT vs line sum 245 MT",
          },
        ],
      },
      arbiter: {
        status: "REVIEW_REQUIRED",
        decisionSummary: "Unresolved quantity conflict — routed to human review.",
        agreement: false,
      },
    },
    {
      round: 2,
      extractor: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "250 MT",
            reason: "Re-stated header value",
            hasEvidence: true,
          },
        ],
      },
      validator: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "245 MT",
            reason: "Line items unchanged",
            hasEvidence: true,
          },
        ],
      },
      challenger: {
        status: "COMPLETE",
        challenges: [
          {
            fieldPath: "goods.quantity",
            category: "ARITHMETIC_CONFLICT",
            reason: "Conflict persists after round 2",
          },
        ],
      },
      arbiter: {
        status: "REVIEW_REQUIRED",
        decisionSummary: "Still unresolved after round 2.",
        agreement: false,
      },
    },
    {
      round: 3,
      extractor: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "250 MT",
            reason: "No new evidence",
            hasEvidence: true,
          },
        ],
      },
      validator: {
        status: "COMPLETE",
        claims: [
          {
            fieldPath: "goods.quantity",
            proposedValue: "245 MT",
            reason: "No new evidence",
            hasEvidence: true,
          },
        ],
      },
      challenger: {
        status: "COMPLETE",
        challenges: [
          {
            fieldPath: "goods.quantity",
            category: "ARITHMETIC_CONFLICT",
            reason: "Max rounds reached without evidence-backed single value",
          },
        ],
      },
      arbiter: {
        status: "REVIEW_REQUIRED",
        decisionSummary:
          "Max 3 rounds reached. Outcome REVIEW_REQUIRED — consensus is not a compliance conclusion.",
        agreement: false,
      },
    },
  ];
}

const DETAILS: Record<string, Omit<CaseWorkbenchDetail, "caseId" | "checklist">> = {
  "case-inv-001": {
    uploadedFiles: [
      { name: "invoice_gulf_precision.pdf", documentType: "COMMERCIAL_INVOICE", sizeLabel: "246 KB" },
    ],
    invoiceFields: baseInvoiceFields().map((f) =>
      f.fieldPath === "seller.name"
        ? { ...f, value: "Gulf Precision Trading LLC", evidence: { page: 1, sourceText: "Seller: Gulf Precision Trading LLC" } }
        : f.fieldPath === "goods.quantity"
          ? { ...f, value: "100 MT", confidence: "HIGH", evidence: { page: 1, sourceText: "Qty: 100 MT" } }
          : f,
    ),
    agentTrace: agentTraceAgreement(),
    reconciliation: {
      bolPresent: false,
      outcome: "NOT_AVAILABLE",
      explanation:
        "BoL/AWB is not present under the invoice-only profile. Transport reconciliation is NOT_AVAILABLE — this is not a passing check.",
      rows: [],
    },
    identities: [
      {
        role: "SELLER",
        rawName: "Gulf Precision Trading L.L.C.",
        normalizedName: "Gulf Precision Trading LLC",
        lei: null,
        leiStatus: "NOT_FOUND_ON_DOCUMENT",
        gleifCandidates: [
          {
            lei: "5493001KJTIIGC8Y1R12",
            legalName: "Gulf Precision Trading LLC",
            similarityNote: "High name similarity — candidate only",
            isExactDocumentMatch: false,
          },
        ],
        vleiStatus: "NOT_CONFIGURED",
        vleiLabel: "VLEI not configured",
        identityOutcome: "POTENTIAL_ENTITY_MATCH_REVIEW",
        source: "GLEIF_NAME_SEARCH_FIXTURE",
        retrievedAt: "2026-08-21T09:00:00Z",
        snapshotId: "gleif-snap-demo-01",
      },
    ],
    findings: [
      {
        id: "price-1",
        title: "Price plausibility",
        outcome: "NOT_APPLICABLE",
        summary: "No benchmark mapping for this HS/corridor fixture.",
        sourceLabel: "STATIC_DEMO_PRICE_REF",
        snapshotId: null,
        ruleId: "PRICE-MAP-MISS",
        detail: "DATA_UNAVAILABLE / NOT_APPLICABLE — not treated as PASS.",
      },
      {
        id: "screen-1",
        title: "Screening indicator",
        outcome: "PASS",
        summary: "No potential match against configured demo snapshot.",
        sourceLabel: "DEMO_MOCK_WATCHLIST",
        snapshotId: "screen-snap-demo-01",
        ruleId: "SCREEN-DEMO",
        detail: "Demo/mock source only.",
      },
      {
        id: "dup-1",
        title: "Duplicate submission signal",
        outcome: "PASS",
        summary: "No prior local hash collision in demo store.",
        sourceLabel: "LOCAL_HASH_DEMO",
        snapshotId: null,
        ruleId: "DUP-LOCAL",
        detail: "Signal only — not proof of duplicate financing.",
      },
    ],
    makerChecker: {
      makerDecision: null,
      checkerDecision: null,
      blockedReason: null,
      allowedActions: ["Request documents", "Continue review", "Escalate"],
    },
    audit: [
      {
        id: "a1",
        at: "2026-08-21T10:10:00Z",
        actor: "system",
        action: "CASE_CREATED",
        detail: "Synthetic case opened",
      },
      {
        id: "a2",
        at: "2026-08-21T10:12:00Z",
        actor: "officer.demo",
        action: "DOCUMENT_UPLOADED",
        detail: "Commercial Invoice received",
      },
    ],
  },
  "case-post-002": {
    uploadedFiles: [
      { name: "invoice_meridian.pdf", documentType: "COMMERCIAL_INVOICE", sizeLabel: "198 KB" },
    ],
    invoiceFields: baseInvoiceFields(),
    agentTrace: agentTraceAgreement(),
    reconciliation: {
      bolPresent: false,
      outcome: "DOCUMENT_PACK_INCOMPLETE",
      explanation:
        "Post-shipment profile requires BoL/AWB. Document pack is incomplete — transport comparison cannot pass.",
      rows: [],
    },
    identities: [
      {
        role: "SELLER",
        rawName: "Meridian Industrial Supplies Pte Ltd",
        normalizedName: "Meridian Industrial Supplies Pte. Ltd.",
        lei: null,
        leiStatus: "UNKNOWN",
        gleifCandidates: [],
        vleiStatus: "NOT_CONFIGURED",
        vleiLabel: "VLEI not configured",
        identityOutcome: "IDENTITY_UNRESOLVED",
        source: "DOCUMENT_ONLY",
        retrievedAt: null,
        snapshotId: null,
      },
    ],
    findings: [
      {
        id: "pack-1",
        title: "Document pack",
        outcome: "DOCUMENT_PACK_INCOMPLETE",
        summary: "Required BoL/AWB not provided for post-shipment profile.",
        sourceLabel: "POLICY_FIXTURE",
        snapshotId: null,
        ruleId: "DOC-POST-BOL",
        detail: "Missing required transport document.",
      },
    ],
    makerChecker: {
      makerDecision: null,
      checkerDecision: null,
      blockedReason: "Document pack incomplete — maker clear action disabled in UI.",
      allowedActions: ["Request documents"],
    },
    audit: [
      {
        id: "b1",
        at: "2026-08-21T11:00:00Z",
        actor: "system",
        action: "CASE_CREATED",
        detail: "Synthetic post-shipment case",
      },
    ],
  },
  "case-lc-003": {
    uploadedFiles: [
      { name: "invoice_nordic.pdf", documentType: "COMMERCIAL_INVOICE", sizeLabel: "210 KB" },
    ],
    invoiceFields: baseInvoiceFields(),
    agentTrace: agentTraceAgreement(),
    reconciliation: {
      bolPresent: false,
      outcome: "NOT_AVAILABLE",
      explanation: "BoL not uploaded; LC pack incomplete. Reconciliation not run as a pass.",
      rows: [],
    },
    identities: [
      {
        role: "SELLER",
        rawName: "Nordic Agro Commodities AS",
        normalizedName: "Nordic Agro Commodities AS",
        lei: "549300ABCDEF12345678",
        leiStatus: "ISSUED",
        gleifCandidates: [
          {
            lei: "549300ABCDEF12345678",
            legalName: "Nordic Agro Commodities AS",
            similarityNote: "Exact document LEI match",
            isExactDocumentMatch: true,
          },
        ],
        vleiStatus: "NOT_CONFIGURED",
        vleiLabel: "VLEI not configured",
        identityOutcome: "IDENTITY_VERIFIED_BY_LEI",
        source: "GLEIF_FIXTURE",
        retrievedAt: "2026-08-21T12:00:00Z",
        snapshotId: "gleif-snap-demo-02",
      },
    ],
    findings: [
      {
        id: "lc-miss",
        title: "Document pack",
        outcome: "DOCUMENT_PACK_INCOMPLETE",
        summary: "Letter of Credit required for LC profile and not provided.",
        sourceLabel: "POLICY_FIXTURE",
        snapshotId: null,
        ruleId: "DOC-LC-REQ",
        detail: "LC missing — pack incomplete.",
      },
    ],
    makerChecker: {
      makerDecision: null,
      checkerDecision: null,
      blockedReason: "LC document missing.",
      allowedActions: ["Request documents"],
    },
    audit: [
      {
        id: "c1",
        at: "2026-08-21T12:35:00Z",
        actor: "system",
        action: "CASE_CREATED",
        detail: "LC profile synthetic case",
      },
    ],
  },
  "case-recon-004": {
    uploadedFiles: [
      { name: "invoice_sahara.pdf", documentType: "COMMERCIAL_INVOICE", sizeLabel: "261 KB" },
      { name: "bol_sahara.pdf", documentType: "BILL_OF_LADING_OR_AWB", sizeLabel: "188 KB" },
    ],
    invoiceFields: baseInvoiceFields(),
    agentTrace: agentTraceDisagreement(),
    reconciliation: {
      bolPresent: true,
      outcome: "REVIEW_REQUIRED",
      explanation: "Invoice and BoL disagree on quantity — human review required.",
      rows: [
        {
          field: "Seller / Shipper",
          invoiceValue: "Sahara Metals FZE",
          bolValue: "Sahara Metals FZE",
          outcome: "PASS",
          note: "Names align on documents.",
        },
        {
          field: "Goods",
          invoiceValue: "Copper cathodes, Grade A",
          bolValue: "Copper cathodes Grade A",
          outcome: "PASS",
          note: "Description compatible.",
        },
        {
          field: "Quantity",
          invoiceValue: "250 MT",
          bolValue: "245 MT",
          outcome: "REVIEW_REQUIRED",
          note: "Cross-document quantity mismatch.",
        },
        {
          field: "Port of loading",
          invoiceValue: "Jebel Ali, AE",
          bolValue: "Jebel Ali",
          outcome: "PASS",
          note: "Compatible port references.",
        },
        {
          field: "Reference",
          invoiceValue: "INV-SM-88421",
          bolValue: "BL-SM-44109",
          outcome: "PASS",
          note: "Distinct document references — expected.",
        },
      ],
    },
    identities: [
      {
        role: "SELLER",
        rawName: "Sahara Metals FZE",
        normalizedName: "Sahara Metals FZE",
        lei: "984500SAHARA00000012",
        leiStatus: "ISSUED",
        gleifCandidates: [
          {
            lei: "984500SAHARA00000012",
            legalName: "Sahara Metals FZE",
            similarityNote: "Exact document LEI + compatible GLEIF record",
            isExactDocumentMatch: true,
          },
        ],
        vleiStatus: "VERIFIED_FIXTURE",
        vleiLabel: "VLEI fixture verified · SYNTHETIC_DEMO_CREDENTIAL",
        identityOutcome: "IDENTITY_SUPPORTED_BY_VLEI",
        source: "VLEI_FIXTURE_ADAPTER",
        retrievedAt: "2026-08-21T13:00:00Z",
        snapshotId: "vlei-fix-demo-01",
      },
    ],
    findings: [
      {
        id: "recon-qty",
        title: "Cross-document quantity",
        outcome: "REVIEW_REQUIRED",
        summary: "Invoice 250 MT vs BoL 245 MT.",
        sourceLabel: "RECONCILER_FIXTURE",
        snapshotId: null,
        ruleId: "RECON-QTY",
        detail: "Evidence retained on both documents.",
      },
      {
        id: "price-2",
        title: "Price plausibility",
        outcome: "REVIEW_REQUIRED",
        summary: "Unit price variance vs static demo benchmark exceeds threshold.",
        sourceLabel: "STATIC_DEMO_PRICE_REF",
        snapshotId: "price-snap-demo-01",
        ruleId: "PRICE-VAR",
        detail: "Risk indicator only — not a fraud conclusion.",
      },
    ],
    makerChecker: {
      makerDecision: null,
      checkerDecision: null,
      blockedReason: null,
      allowedActions: ["Continue review", "Request explanation", "Escalate"],
    },
    audit: [
      {
        id: "d1",
        at: "2026-08-21T13:10:00Z",
        actor: "system",
        action: "RECONCILIATION_COMPLETE",
        detail: "Quantity mismatch flagged REVIEW_REQUIRED",
      },
    ],
  },
  "case-screen-005": {
    uploadedFiles: [
      { name: "invoice_eastern.pdf", documentType: "COMMERCIAL_INVOICE", sizeLabel: "233 KB" },
      { name: "bol_eastern.pdf", documentType: "BILL_OF_LADING_OR_AWB", sizeLabel: "171 KB" },
    ],
    invoiceFields: baseInvoiceFields().map((f) =>
      f.fieldPath === "seller.name"
        ? {
            ...f,
            value: "Eastern Horizon Logistics Co.",
            evidence: { page: 1, sourceText: "Seller: Eastern Horizon Logistics Co." },
          }
        : f,
    ),
    agentTrace: agentTraceAgreement(),
    reconciliation: {
      bolPresent: true,
      outcome: "PASS",
      explanation: "Core party/goods/quantity/port fields align on the demo packet.",
      rows: [
        {
          field: "Seller / Shipper",
          invoiceValue: "Eastern Horizon Logistics Co.",
          bolValue: "Eastern Horizon Logistics Co.",
          outcome: "PASS",
          note: "Aligned.",
        },
        {
          field: "Goods",
          invoiceValue: "Copper cathodes, Grade A",
          bolValue: "Copper cathodes, Grade A",
          outcome: "PASS",
          note: "Aligned.",
        },
        {
          field: "Quantity",
          invoiceValue: "250 MT",
          bolValue: "250 MT",
          outcome: "PASS",
          note: "Aligned.",
        },
        {
          field: "Port of loading",
          invoiceValue: "Jebel Ali, AE",
          bolValue: "Jebel Ali, AE",
          outcome: "PASS",
          note: "Aligned.",
        },
        {
          field: "Reference",
          invoiceValue: "INV-EH-2201",
          bolValue: "BL-EH-9901",
          outcome: "PASS",
          note: "Distinct references.",
        },
      ],
    },
    identities: [
      {
        role: "SELLER",
        rawName: "Eastern Horizon Logistics Co",
        normalizedName: "Eastern Horizon Logistics Co.",
        lei: null,
        leiStatus: "NOT_ON_DOCUMENT",
        gleifCandidates: [
          {
            lei: "549300EASTHORIZ00001",
            legalName: "Eastern Horizon Logistics Limited",
            similarityNote: "Fuzzy name candidate — not identity proof",
            isExactDocumentMatch: false,
          },
        ],
        vleiStatus: "NOT_CONFIGURED",
        vleiLabel: "VLEI not configured",
        identityOutcome: "POTENTIAL_ENTITY_MATCH_REVIEW",
        source: "GLEIF_NAME_SEARCH_FIXTURE",
        retrievedAt: "2026-08-21T14:00:00Z",
        snapshotId: "gleif-snap-demo-03",
      },
    ],
    findings: [
      {
        id: "screen-pot",
        title: "Screening indicator",
        outcome: "POTENTIAL_MATCH",
        summary: "Potential name match against DEMO/MOCK watchlist snapshot.",
        sourceLabel: "DEMO_MOCK_WATCHLIST",
        snapshotId: "screen-snap-demo-02",
        ruleId: "SCREEN-FUZZY",
        detail:
          "Potential match only — not confirmed sanctioned. Requires human review against authoritative source.",
      },
      {
        id: "dup-2",
        title: "Duplicate submission signal",
        outcome: "REVIEW_REQUIRED",
        summary: "Local hash overlaps prior case TP-2026-0099.",
        sourceLabel: "LOCAL_HASH_DEMO",
        snapshotId: null,
        ruleId: "DUP-LOCAL",
        detail: "Indicator with prior case reference — not proven duplicate financing.",
      },
      {
        id: "price-3",
        title: "Price plausibility",
        outcome: "DATA_UNAVAILABLE",
        summary: "Benchmark source marked degraded in fixture.",
        sourceLabel: "STATIC_DEMO_PRICE_REF",
        snapshotId: "price-snap-degraded",
        ruleId: "PRICE-SRC",
        detail: "DATA_UNAVAILABLE retained — not mapped to PASS.",
      },
    ],
    makerChecker: {
      makerDecision: "Escalate for enhanced review",
      checkerDecision: null,
      blockedReason: "Checker action blocked until maker decision is recorded (demo rule).",
      allowedActions: ["Checker: confirm escalate", "Checker: return to maker"],
    },
    audit: [
      {
        id: "e1",
        at: "2026-08-21T14:01:00Z",
        actor: "system",
        action: "SCREENING_POTENTIAL_MATCH",
        detail: "Demo watchlist potential match flagged",
      },
      {
        id: "e2",
        at: "2026-08-21T14:04:00Z",
        actor: "maker.demo",
        action: "MAKER_DECISION",
        detail: "Escalate for enhanced review",
      },
    ],
  },
};

export function getCaseWorkbenchDetail(caseId: string): CaseWorkbenchDetail | null {
  const queue = getMockQueueCase(caseId);
  const detail = DETAILS[caseId];
  if (!queue || !detail) return null;
  return {
    caseId,
    checklist: getCaseProfileChecklist(caseId),
    ...detail,
  };
}
