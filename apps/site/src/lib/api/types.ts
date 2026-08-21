/**
 * Wire types for the TradePulse FastAPI backend.
 *
 * These mirror what `/api/v1` actually returns today, captured against a running
 * server -- not the canonical contract in `packages/contracts`, and not the view
 * types the workbench components consume. Three vocabularies currently exist and
 * they do not agree; `adapters.ts` is the single place that translates.
 *
 * Do not "tidy" these names to match the UI. They are the wire, and the wire is
 * owned by the backend.
 */

/** Case lifecycle position. Backend calls this `state`, not `status`. */
export type ApiCaseState =
  | "INGESTED"
  | "PROCESSING"
  | "EXTRACTION_REVIEW"
  | "PENDING_MAKER"
  | "INVESTIGATION_REQUIRED"
  | "MAKER_APPROVED"
  | "CHECKER_APPROVED"
  | "CHECKER_REJECTED"
  | "PROCESSING_FAILED";

/** What happens next. Separate from state, and must stay separate. */
export type ApiRiskRoute =
  | "READY_FOR_HUMAN_REVIEW"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "EXTRACTION_REVIEW_REQUIRED"
  | "MAKER_REVIEW_REQUIRED"
  | "HIGH_RISK_ESCALATION"
  | "DATA_REVIEW_REQUIRED";

export type ApiTradeProfile =
  | "INVOICE_ONLY_PRE_REVIEW"
  | "POST_SHIPMENT_DOCUMENT_REVIEW"
  | "LC_DOCUMENT_REVIEW"
  | "DOCUMENTARY_COLLECTION_REVIEW"
  | "ENHANCED_TRADE_HOUSE_REVIEW"
  | "DOMESTIC_INDIA_GOODS_MOVEMENT";

/**
 * Check outcomes. NOT_AVAILABLE / DATA_UNAVAILABLE are first-class and must
 * never be collapsed into PASS anywhere in the UI.
 */
export type ApiCheckStatus =
  | "PASS"
  | "WARN"
  | "REVIEW_REQUIRED"
  | "FAIL"
  | "NOT_APPLICABLE"
  | "NOT_AVAILABLE"
  | "DATA_UNAVAILABLE";

export type ApiDocumentRequirementState =
  | "REQUIRED"
  | "CONDITIONALLY_REQUIRED"
  | "OPTIONAL"
  | "NOT_APPLICABLE"
  | "NOT_PROVIDED"
  | "POLICY_CONFIGURATION_REQUIRED";

export type ApiDataLabel = "synthetic" | "reference" | "cached" | "live";

export interface ApiVleiEvidence {
  credential_id: string | null;
  subject_lei: string | null;
  issuer: string | null;
  signer_role: string | null;
  status:
    | "VERIFIED_LIVE"
    | "VERIFIED_FIXTURE"
    | "NOT_CONFIGURED"
    | "INVALID"
    | "EXPIRED"
    | "REVOKED"
    | "DATA_UNAVAILABLE";
  issued_at: string | null;
  expires_at: string | null;
  evidence_hash: string | null;
  source: string;
  data_label: ApiDataLabel | null;
}

export interface ApiIdentity {
  role: string;
  raw_name: string | null;
  normalized_name: string | null;
  country: string | null;
  address: string | null;
  gstin: string | null;
  pan: string | null;
  cin_llpin: string | null;
  iec: string | null;
  lei: unknown | null;
  vlei: ApiVleiEvidence | null;
  registry_candidates: Array<{
    lei?: string | null;
    legal_name?: string | null;
    similarity?: number | null;
    is_exact_document_match?: boolean;
  }>;
  resolution_status: string;
}

export interface ApiCaseSummary {
  case_id: string;
  transaction_profile: ApiTradeProfile;
  state: ApiCaseState;
  risk_route: ApiRiskRoute | null;
  assignee: string | null;
  sla_due_at: string | null;
  created_at: string;
  updated_at: string;
  data_label: ApiDataLabel;
  document_count: number;
}

export interface ApiCaseRecord extends Omit<ApiCaseSummary, "document_count"> {
  corridor: string | null;
  version: number;
  identities: ApiIdentity[];
  metadata: Record<string, unknown>;
}

export interface ApiDocumentRequirement {
  document_type: string;
  state: ApiDocumentRequirementState;
  blocker: boolean;
  rule_id: string;
  reason: string;
  provided: boolean;
}

export interface ApiPolicy {
  profile: ApiTradeProfile;
  requirements: ApiDocumentRequirement[];
}

export interface ApiFinding {
  check_id: string;
  rule_pack_version: string;
  status: ApiCheckStatus;
  severity: "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  score_contribution: number;
  reason: string;
  rule_reference?: string | null;
  source_label?: string | null;
}

export interface ApiReconciliation {
  profile: ApiTradeProfile;
  status: ApiCheckStatus;
  comparisons: Array<{
    field?: string;
    invoice_value?: string | null;
    transport_value?: string | null;
    status?: ApiCheckStatus;
    reason?: string;
  }>;
  rule_pack_version: string;
  reason: string;
  recommended_action: string;
}

/** Envelope returned by POST /cases/{id}/process. */
export interface ApiProcessResult {
  case: ApiCaseRecord;
  policy: ApiPolicy;
  findings: ApiFinding[];
  risk_route: ApiRiskRoute;
  reconciliation: ApiReconciliation;
  identities: ApiIdentity[];
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    correlation_id?: string;
    retryable?: boolean;
  };
}
