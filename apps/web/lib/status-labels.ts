/**
 * Consolidated status label mappings for the TradePulse workbench.
 *
 * All human-readable label dictionaries live here so that both the API
 * response mapper (lib/api/map.ts) and the demo store (lib/demo/store.ts)
 * share a single source of truth for status text.
 *
 * Adding a new enum value to packages/contracts/ should trigger an update
 * here — not scattered ad-hoc strings across components.
 */

import {
  TradeProfile,
  CaseStatus,
  ReadinessRoute,
  CheckStatus,
  DocumentRequirementState,
} from "../../packages/contracts/types";

/* ── Enum-to-label functions ─────────────────────────────────────── */

export function profileLabel(p: TradeProfile): string {
  const map: Record<TradeProfile, string> = {
    INVOICE_ONLY_PRE_REVIEW: "Invoice-only pre-review",
    POST_SHIPMENT_DOCUMENT_REVIEW: "Post-shipment review",
    LC_DOCUMENT_REVIEW: "LC document review",
    DOCUMENTARY_COLLECTION_REVIEW: "Documentary collection review",
    ENHANCED_TRADE_HOUSE_REVIEW: "Enhanced trade-house",
  };
  return map[p] || p.replaceAll("_", " ");
}

export function riskLabel(r: ReadinessRoute): string {
  const map: Record<ReadinessRoute, string> = {
    READY_FOR_HUMAN_REVIEW: "Ready for human review",
    DOCUMENT_PACK_INCOMPLETE: "Document pack incomplete",
    EXTRACTION_REVIEW_REQUIRED: "Extraction review required",
    MAKER_REVIEW_REQUIRED: "Maker review required",
    HIGH_RISK_ESCALATION: "High-risk escalation",
    DATA_REVIEW_REQUIRED: "Data review required",
  };
  return map[r] || r.replaceAll("_", " ");
}

export function workflowLabel(w: CaseStatus): string {
  const map: Partial<Record<CaseStatus, string>> = {
    DRAFT: "Draft",
    INGESTED: "Ingested",
    PROCESSING: "Processing",
    DOCUMENT_PACK_INCOMPLETE: "Document pack incomplete",
    EXTRACTION_REVIEW_REQUIRED: "Extraction review required",
    PENDING_MAKER_REVIEW: "Pending maker",
    MAKER_APPROVED: "Awaiting checker",
    CHECKER_APPROVED: "Checker approved",
    CHECKER_REJECTED: "Checker rejected",
    INVESTIGATION_REQUIRED: "Investigation required",
    PROCESSING_FAILED: "Processing failed",
  };
  return map[w] || w.replaceAll("_", " ");
}

export function statusLabel(s: string): string {
  const map: Record<string, string> = {
    [CheckStatus.PASS]: "Clear",
    [CheckStatus.DATA_UNAVAILABLE]: "Data unavailable",
    [CheckStatus.NOT_APPLICABLE]: "Not applicable",
    [CheckStatus.REVIEW_REQUIRED]: "Review required",
    [CheckStatus.FAIL]: "Failed",
    MATCH: "Match",
    MISMATCH: "Mismatch",
    NOT_AVAILABLE: "Not available",
  };
  return map[s] || s.replaceAll("_", " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
}

export function policyLabel(p: DocumentRequirementState): string {
  const map: Record<DocumentRequirementState, string> = {
    REQUIRED: "Required",
    CONDITIONALLY_REQUIRED: "Conditionally required",
    OPTIONAL: "Optional",
    NOT_APPLICABLE: "Not applicable",
    NOT_PROVIDED: "Not provided",
    POLICY_CONFIGURATION_REQUIRED: "Policy configuration required",
  };
  return map[p] || p;
}

/* ── Lookup dictionaries (used by API response mapper) ───────────── */

export const FINDING_TITLES: Record<string, string> = {
  "SCREEN-PARTY-001": "Counterparty screening",
  "PRICE-001": "Price plausibility",
  "DUP-001": "Duplicate submission signal",
};

export const DOC_LABELS: Record<string, string> = {
  commercial_invoice: "Commercial invoice",
  bill_of_lading: "Bill of lading",
  packing_list: "Packing list",
  lc_terms_lite: "LC terms (lite)",
  certificate_of_origin: "Certificate of origin",
  insurance_certificate: "Insurance certificate",
};

export const FIELD_LABELS: Record<string, string> = {
  "parties.seller_shipper": "Seller / shipper",
  "parties.buyer_consignee": "Buyer / consignee",
  "goods.description": "Goods description",
  "goods.quantity": "Quantity",
  "goods.unit": "Unit",
  "ports.port_of_loading": "Port of loading",
  "ports.port_of_discharge": "Port of discharge",
  "references.invoice_number": "Invoice reference",
  "dates.shipment_or_invoice": "Date",
};

export const IDENTITY_OUTCOMES: Record<string, string> = {
  IDENTITY_VERIFIED_BY_LEI: "Verified by LEI",
  IDENTITY_SUPPORTED_BY_VLEI: "Supported by vLEI",
  POTENTIAL_ENTITY_MATCH_REVIEW: "Possible match — review required",
  IDENTITY_UNRESOLVED: "Identity unresolved",
  IDENTITY_SOURCE_UNAVAILABLE: "Identity source unavailable",
  VLEI_NOT_CONFIGURED: "vLEI not configured",
};

export const AUDIT_ACTIONS: Record<string, string> = {
  CASE_CREATED: "Case created",
  DOCUMENT_UPLOADED: "Document uploaded",
  CASE_PROCESSED: "Case processed",
  CASE_STATE_TRANSITION: "Workflow updated",
  MAKER_APPROVE: "Maker submitted to checker",
  MAKER_INVESTIGATE: "Maker escalated",
  CHECKER_APPROVE: "Checker approved",
  CHECKER_REJECT: "Checker rejected",
};

export const AGENT_LABELS: Record<string, string> = {
  EXTRACTOR: "Extractor",
  VALIDATOR: "Validator",
  CHALLENGER: "Challenger",
  ARBITER: "Arbiter",
  CROSS_DOCUMENT_RECONCILER: "Cross-document reconciler",
};
