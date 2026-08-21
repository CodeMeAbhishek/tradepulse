import type {
  DocumentRequirementState,
  FindingOutcome,
  IdentityOutcomeLabel,
  ReadinessRoute,
  TransactionProfile,
  VleiStatus,
} from "@/lib/mock/types";

const PROFILE_LABELS: Record<TransactionProfile, string> = {
  INVOICE_ONLY_PRE_REVIEW: "Invoice-only pre-review",
  POST_SHIPMENT_DOCUMENT_REVIEW: "Post-shipment review",
  LC_DOCUMENT_REVIEW: "LC document review",
  DOCUMENTARY_COLLECTION_REVIEW: "Documentary collection",
  ENHANCED_TRADE_HOUSE_REVIEW: "Enhanced trade-house",
  DOMESTIC_INDIA_GOODS_MOVEMENT: "Domestic India goods",
};

const ROUTE_LABELS: Record<ReadinessRoute, string> = {
  READY_FOR_HUMAN_REVIEW: "Ready for human review",
  REVIEW_REQUIRED: "Review required",
  DOCUMENT_PACK_INCOMPLETE: "Document pack incomplete",
  DATA_REVIEW_REQUIRED: "Data review required",
  MAKER_REVIEW_REQUIRED: "Maker review required",
  HIGH_RISK_ESCALATION: "High-risk escalation",
};

const IDENTITY_LABELS: Record<IdentityOutcomeLabel, string> = {
  IDENTITY_VERIFIED_BY_LEI: "Identity verified by LEI",
  IDENTITY_SUPPORTED_BY_VLEI: "Identity supported by VLEI",
  POTENTIAL_ENTITY_MATCH_REVIEW: "Potential entity match — review",
  IDENTITY_UNRESOLVED: "Identity unresolved",
  IDENTITY_SOURCE_UNAVAILABLE: "Identity source unavailable",
  VLEI_NOT_CONFIGURED: "VLEI not configured",
};

export function profileLabel(profile: TransactionProfile): string {
  return PROFILE_LABELS[profile];
}

export function readinessLabel(route: ReadinessRoute): string {
  return ROUTE_LABELS[route];
}

export function documentStateLabel(state: DocumentRequirementState): string {
  return state.replaceAll("_", " ");
}

export function findingOutcomeLabel(outcome: FindingOutcome): string {
  return outcome.replaceAll("_", " ");
}

export function identityOutcomeLabel(code: IdentityOutcomeLabel): string {
  return IDENTITY_LABELS[code];
}

export function vleiStatusLabel(status: VleiStatus): string {
  return status.replaceAll("_", " ");
}

export function formatTimestamp(iso: string): string {
  try {
    return new Intl.DateTimeFormat("en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "UTC",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export function outcomeToneClass(outcome: FindingOutcome | string): string {
  // Severity on the left rule; the label itself stays ink so it is always
  // readable and the wording, not the colour, carries the meaning.
  switch (outcome) {
    case "PASS":
      return "border-l-verified";
    case "REVIEW_REQUIRED":
    case "POTENTIAL_MATCH":
    case "MAKER_REVIEW_REQUIRED":
      return "border-l-amber";
    case "FAIL":
    case "HIGH_RISK_ESCALATION":
      return "border-l-stamp";
    case "DOCUMENT_PACK_INCOMPLETE":
    case "DATA_UNAVAILABLE":
    case "NOT_AVAILABLE":
    case "NOT_APPLICABLE":
    default:
      return "border-l-rule";
  }
}
