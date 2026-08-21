/**
 * The single translation point between the backend wire format and the view
 * types the workbench components consume.
 *
 * Why this exists: the API says `case_id` / `transaction_profile` / `state` /
 * `risk_route` / `data_label`, while the components expect `id` / `profile` /
 * `status` / `readinessRoute` / `dataSourceLabel`. A third vocabulary lives in
 * `packages/contracts`, which ADR 001 names canonical and which neither side
 * imports.
 *
 * This module is TEMPORARY. When Abhishek and Ansh settle the canon (see
 * docs/contract-migration-plan.md), the mapping tables below collapse to
 * identity functions and this file should be deleted rather than maintained.
 *
 * One rule governs everything here: a value that cannot be mapped becomes an
 * explicit unavailable state, never a pass. Silently coercing an unknown
 * backend status into something reassuring is the exact failure the product
 * rules forbid.
 */

import type {
  CaseStatus,
  DocumentCompletenessItem,
  DocumentRequirementState,
  FindingOutcome,
  QueueCase,
  ReadinessRoute,
  TransactionProfile,
} from "@/lib/mock/types";

import type {
  ApiCaseSummary,
  ApiCheckStatus,
  ApiDocumentRequirement,
  ApiFinding,
  ApiRiskRoute,
  ApiTradeProfile,
} from "./types";

/* ------------------------------------------------------------------ profile */

const PROFILE: Record<ApiTradeProfile, TransactionProfile> = {
  INVOICE_ONLY_PRE_REVIEW: "INVOICE_ONLY_PRE_REVIEW",
  POST_SHIPMENT_DOCUMENT_REVIEW: "POST_SHIPMENT_DOCUMENT_REVIEW",
  LC_DOCUMENT_REVIEW: "LC_DOCUMENT_REVIEW",
  DOCUMENTARY_COLLECTION_REVIEW: "DOCUMENTARY_COLLECTION_REVIEW",
  ENHANCED_TRADE_HOUSE_REVIEW: "ENHANCED_TRADE_HOUSE_REVIEW",
  DOMESTIC_INDIA_GOODS_MOVEMENT: "DOMESTIC_INDIA_GOODS_MOVEMENT",
};

export function toProfile(value: ApiTradeProfile): TransactionProfile {
  return PROFILE[value] ?? "INVOICE_ONLY_PRE_REVIEW";
}

/* -------------------------------------------------------------------- route */

const ROUTE: Record<ApiRiskRoute, ReadinessRoute> = {
  READY_FOR_HUMAN_REVIEW: "READY_FOR_HUMAN_REVIEW",
  DOCUMENT_PACK_INCOMPLETE: "DOCUMENT_PACK_INCOMPLETE",
  // The view layer has no EXTRACTION_REVIEW_REQUIRED member; REVIEW_REQUIRED is
  // the nearest honest equivalent and is still a review, never a pass.
  EXTRACTION_REVIEW_REQUIRED: "REVIEW_REQUIRED",
  MAKER_REVIEW_REQUIRED: "MAKER_REVIEW_REQUIRED",
  HIGH_RISK_ESCALATION: "HIGH_RISK_ESCALATION",
  DATA_REVIEW_REQUIRED: "DATA_REVIEW_REQUIRED",
};

/** An absent or unrecognised route means we do not know -- so it needs review. */
export function toReadinessRoute(value: ApiRiskRoute | null): ReadinessRoute {
  if (!value) return "REVIEW_REQUIRED";
  return ROUTE[value] ?? "REVIEW_REQUIRED";
}

/* ------------------------------------------------------------------- status */

/**
 * Backend `state` is a lifecycle position; the view's `CaseStatus` conflates
 * lifecycle and route. Until the canon splits them properly (ADR 001 s3.1),
 * map conservatively: anything not clearly finished reads as needing review.
 */
export function toCaseStatus(state: string, route: ApiRiskRoute | null): CaseStatus {
  switch (state) {
    case "INGESTED":
    case "PROCESSING":
      return "DRAFT";
    case "MAKER_APPROVED":
    case "CHECKER_APPROVED":
      return "READY_FOR_HUMAN_REVIEW";
    case "PENDING_MAKER":
      return route === "DOCUMENT_PACK_INCOMPLETE"
        ? "DOCUMENT_PACK_INCOMPLETE"
        : "MAKER_REVIEW_REQUIRED";
    case "INVESTIGATION_REQUIRED":
      return "HIGH_RISK_ESCALATION";
    case "EXTRACTION_REVIEW":
    case "CHECKER_REJECTED":
    case "PROCESSING_FAILED":
    default:
      return "REVIEW_REQUIRED";
  }
}

/* ------------------------------------------------------------------ outcome */

const OUTCOME: Record<ApiCheckStatus, FindingOutcome> = {
  PASS: "PASS",
  WARN: "REVIEW_REQUIRED",
  REVIEW_REQUIRED: "REVIEW_REQUIRED",
  FAIL: "REVIEW_REQUIRED",
  NOT_APPLICABLE: "NOT_APPLICABLE",
  NOT_AVAILABLE: "NOT_AVAILABLE",
  DATA_UNAVAILABLE: "DATA_UNAVAILABLE",
};

/**
 * Unknown statuses resolve to DATA_UNAVAILABLE, never PASS. If the backend
 * grows a status this build has not seen, the officer is told the check could
 * not be read -- which is true -- rather than being shown a green tick.
 */
export function toFindingOutcome(status: ApiCheckStatus): FindingOutcome {
  return OUTCOME[status] ?? "DATA_UNAVAILABLE";
}

/* --------------------------------------------------------- document policy */

const DOC_STATE: Record<ApiDocumentRequirement["state"], DocumentRequirementState> = {
  REQUIRED: "REQUIRED",
  CONDITIONALLY_REQUIRED: "CONDITIONALLY_REQUIRED",
  OPTIONAL: "OPTIONAL",
  NOT_APPLICABLE: "NOT_APPLICABLE",
  NOT_PROVIDED: "NOT_PROVIDED",
  // The view has no POLICY_CONFIGURATION_REQUIRED member. NOT_APPLICABLE would
  // read as "nothing to do", which is wrong -- someone must configure policy.
  POLICY_CONFIGURATION_REQUIRED: "NOT_PROVIDED",
};

/** Turn a backend document_type into something a human reads. */
export function documentLabel(documentType: string): string {
  return documentType
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export function toCompletenessItem(req: ApiDocumentRequirement): DocumentCompletenessItem {
  return {
    documentType: req.document_type,
    state: req.provided && req.state === "REQUIRED" ? "PROVIDED" : DOC_STATE[req.state],
    label: documentLabel(req.document_type),
    blocker: req.blocker,
    reason: req.reason,
  };
}

/* --------------------------------------------------------------- case shape */

/**
 * Build the queue row a component renders.
 *
 * `dataSourceLabel` is pinned to SYNTHETIC_DEMO because the view type admits
 * nothing else today. The backend's own `data_label` is carried through as
 * `apiDataLabel` so the UI can stop lying the moment that type is widened --
 * a case the backend marks `live` must not be captioned as synthetic.
 */
export function toQueueCase(
  summary: ApiCaseSummary,
  completeness: DocumentCompletenessItem[] = [],
): QueueCase & { apiDataLabel: string } {
  return {
    id: summary.case_id,
    reference: summary.case_id,
    counterparty: summary.assignee ?? "Unassigned",
    corridor: "—",
    profile: toProfile(summary.transaction_profile),
    status: toCaseStatus(summary.state, summary.risk_route),
    readinessRoute: toReadinessRoute(summary.risk_route),
    documentCompleteness: completeness,
    updatedAt: summary.updated_at,
    dataSourceLabel: "SYNTHETIC_DEMO",
    apiDataLabel: summary.data_label,
  };
}

/** Title for a finding card. The backend sends reasons, not titles. */
export function findingTitle(finding: ApiFinding): string {
  const [family] = finding.check_id.split("-");
  const named: Record<string, string> = {
    SCREEN: "Counterparty screening",
    PRICE: "Price plausibility",
    DUP: "Duplicate submission signal",
    RECON: "Cross-document reconciliation",
    DOC: "Document policy",
    ID: "Identity evidence",
  };
  return named[family ?? ""] ?? finding.check_id;
}
