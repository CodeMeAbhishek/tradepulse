import type { QueueCase } from "./types";
import { getChecklistForProfile } from "./profiles";

/**
 * Local synthetic queue fixtures for the workbench shell.
 * Not live bank/trade data. Not identity or sanctions verification.
 */
export const MOCK_QUEUE_CASES: QueueCase[] = [
  {
    id: "case-inv-001",
    reference: "TP-2026-0142",
    counterparty: "Gulf Precision Trading LLC",
    corridor: "IN-AE",
    profile: "INVOICE_ONLY_PRE_REVIEW",
    status: "READY_FOR_HUMAN_REVIEW",
    readinessRoute: "READY_FOR_HUMAN_REVIEW",
    documentCompleteness: [
      {
        documentType: "COMMERCIAL_INVOICE",
        state: "PROVIDED",
        label: "Commercial Invoice",
        blocker: false,
        reason: "Uploaded for this case.",
      },
      {
        documentType: "BILL_OF_LADING_OR_AWB",
        state: "NOT_AVAILABLE",
        label: "BoL / AWB",
        blocker: false,
        reason: "Invoice-only profile — transport recon NOT_AVAILABLE.",
      },
      {
        documentType: "PACKING_LIST",
        state: "OPTIONAL",
        label: "Packing List",
        blocker: false,
        reason: "Optional — does not block.",
      },
    ],
    updatedAt: "2026-08-21T10:15:00Z",
    dataSourceLabel: "SYNTHETIC_DEMO",
  },
  {
    id: "case-post-002",
    reference: "TP-2026-0148",
    counterparty: "Meridian Industrial Supplies Pte Ltd",
    corridor: "IN-SG",
    profile: "POST_SHIPMENT_DOCUMENT_REVIEW",
    status: "DOCUMENT_PACK_INCOMPLETE",
    readinessRoute: "DOCUMENT_PACK_INCOMPLETE",
    documentCompleteness: [
      {
        documentType: "COMMERCIAL_INVOICE",
        state: "PROVIDED",
        label: "Commercial Invoice",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "BILL_OF_LADING_OR_AWB",
        state: "NOT_PROVIDED",
        label: "BoL / AWB",
        blocker: true,
        reason: "Required for post-shipment — pack incomplete.",
      },
      {
        documentType: "PACKING_LIST",
        state: "CONDITIONALLY_REQUIRED",
        label: "Packing List",
        blocker: false,
        reason: "Conditional — not claimed as universal legal mandatory.",
      },
    ],
    updatedAt: "2026-08-21T11:02:00Z",
    dataSourceLabel: "SYNTHETIC_DEMO",
  },
  {
    id: "case-lc-003",
    reference: "TP-2026-0151",
    counterparty: "Nordic Agro Commodities AS",
    corridor: "IN-NO",
    profile: "LC_DOCUMENT_REVIEW",
    status: "DOCUMENT_PACK_INCOMPLETE",
    readinessRoute: "DOCUMENT_PACK_INCOMPLETE",
    documentCompleteness: [
      {
        documentType: "COMMERCIAL_INVOICE",
        state: "PROVIDED",
        label: "Commercial Invoice",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "LETTER_OF_CREDIT",
        state: "NOT_PROVIDED",
        label: "Letter of Credit",
        blocker: true,
        reason: "Required for LC profile only.",
      },
      {
        documentType: "BILL_OF_LADING_OR_AWB",
        state: "CONDITIONALLY_REQUIRED",
        label: "BoL / AWB",
        blocker: false,
        reason: "Conditional in this fixture.",
      },
    ],
    updatedAt: "2026-08-21T12:40:00Z",
    dataSourceLabel: "SYNTHETIC_DEMO",
  },
  {
    id: "case-recon-004",
    reference: "TP-2026-0155",
    counterparty: "Sahara Metals FZE",
    corridor: "IN-AE",
    profile: "POST_SHIPMENT_DOCUMENT_REVIEW",
    status: "REVIEW_REQUIRED",
    readinessRoute: "REVIEW_REQUIRED",
    documentCompleteness: [
      {
        documentType: "COMMERCIAL_INVOICE",
        state: "PROVIDED",
        label: "Commercial Invoice",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "BILL_OF_LADING_OR_AWB",
        state: "PROVIDED",
        label: "BoL / AWB",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "PACKING_LIST",
        state: "OPTIONAL",
        label: "Packing List",
        blocker: false,
        reason: "Optional — does not block.",
      },
    ],
    updatedAt: "2026-08-21T13:18:00Z",
    dataSourceLabel: "SYNTHETIC_DEMO",
  },
  {
    id: "case-screen-005",
    reference: "TP-2026-0160",
    counterparty: "Eastern Horizon Logistics Co.",
    corridor: "IN-GB",
    profile: "ENHANCED_TRADE_HOUSE_REVIEW",
    status: "MAKER_REVIEW_REQUIRED",
    readinessRoute: "MAKER_REVIEW_REQUIRED",
    documentCompleteness: [
      {
        documentType: "COMMERCIAL_INVOICE",
        state: "PROVIDED",
        label: "Commercial Invoice",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "BILL_OF_LADING_OR_AWB",
        state: "PROVIDED",
        label: "BoL / AWB",
        blocker: false,
        reason: "Uploaded.",
      },
      {
        documentType: "CERTIFICATE_OF_ORIGIN",
        state: "CONDITIONALLY_REQUIRED",
        label: "Certificate of Origin",
        blocker: false,
        reason: "Conditional supporting — missing optional/conditional does not auto-block UI claim.",
      },
    ],
    updatedAt: "2026-08-21T14:05:00Z",
    dataSourceLabel: "SYNTHETIC_DEMO",
  },
];

export function getMockQueueCases(): QueueCase[] {
  return [...MOCK_QUEUE_CASES];
}

export function getMockQueueCase(id: string): QueueCase | undefined {
  return MOCK_QUEUE_CASES.find((c) => c.id === id);
}

export function getCaseProfileChecklist(id: string) {
  const c = getMockQueueCase(id);
  if (!c) return [];
  return getChecklistForProfile(c.profile);
}
