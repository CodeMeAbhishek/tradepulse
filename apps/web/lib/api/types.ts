/** Types mirrored from live /api/v1 responses (tradepulse_contracts). */

export type TradeProfile =
  | "PRE_SHIPMENT_TRADE_FINANCE"
  | "LC_ISSUANCE_AMENDMENT"
  | "POST_SHIPMENT_LC_PRESENTATION"
  | "DOCUMENTARY_COLLECTION"
  | "TRADE_CREDIT_FACTORING"
  | "TRADE_HOUSE_COMPLIANCE_REVIEW";

export type CaseState =
  | "DRAFT"
  | "SCRUTINY_IN_PROGRESS"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "SCRUTINY_COMPLETE"
  | "MAKER_REVIEW"
  | "INFORMATION_REQUESTED"
  | "MAKER_RECOMMENDED"
  | "CHECKER_REVIEW"
  | "RETURNED_TO_MAKER"
  | "CHECKER_APPROVED"
  | "ESCALATED"
  | "PROCESSING_FAILED";

export type ShipmentMode = "OCEAN" | "AIR" | "MULTIMODAL" | "UNKNOWN";

export type DocumentTypeApi =
  | "trade_finance_application"
  | "commercial_invoice"
  | "bill_of_lading"
  | "air_waybill"
  | "packing_list"
  | "lc_terms_lite"
  | "shipping_bill"
  | "certificate_of_origin"
  | "insurance_certificate"
  | "bill_of_exchange"
  | "kyc_kyb_evidence"
  | "unsupported";

export interface CaseSummary {
  case_id: string;
  transaction_profile: TradeProfile;
  state: CaseState;
  risk_route: string | null;
  assignee: string | null;
  sla_due_at: string | null;
  created_at: string;
  updated_at: string;
  data_label: string;
  document_count: number;
}

export interface CaseRecord {
  case_id: string;
  transaction_profile: TradeProfile;
  state: CaseState;
  corridor: string | null;
  risk_route: string | null;
  assignee: string | null;
  created_at: string;
  updated_at: string;
  data_label: string;
  version: number;
  identities: IdentityEvidence[];
  metadata: Record<string, unknown>;
  shipment_mode?: ShipmentMode;
  transaction_stage?: string | null;
  current_review_role?: string | null;
  last_maker_actor?: string | null;
}

export interface DocumentMeta {
  document_id: string;
  case_id: string;
  document_type: DocumentTypeApi;
  filename: string;
  content_type: string;
  byte_size: number;
  sha256: string;
  processing_state: string;
  uploaded_at: string;
}

export interface PolicyRequirement {
  document_type: string;
  state: string;
  provided: boolean;
  blocker: boolean;
  reason: string;
  rule_id: string;
}

export interface DocumentPolicyEvaluation {
  profile: string;
  pack_status: string;
  requirements: PolicyRequirement[];
  missing_blocker_types: string[];
  transport_reconciliation: string;
  reason?: string;
}

export interface InvoiceParty {
  legal_name: string | null;
  address: string | null;
  country: string | null;
  lei: string | null;
  gstin: string | null;
  iec: string | null;
}

export interface InvoiceExtraction {
  invoice_number: string | null;
  invoice_date: string | null;
  currency: string | null;
  seller: InvoiceParty | null;
  buyer: InvoiceParty | null;
  items: Array<{
    description: string | null;
    quantity: number | null;
    unit: string | null;
    unit_price: number | null;
    line_total: number | null;
    hs_code: string | null;
  }>;
  total_amount: number | null;
  port_of_loading: string | null;
  port_of_discharge: string | null;
}

export interface FieldComparison {
  field_path: string;
  invoice_value: unknown;
  bol_value: unknown;
  status: string;
  reason: string;
}

export interface ReconciliationResult {
  profile: string;
  status: string;
  comparisons: FieldComparison[];
  reason: string;
  recommended_action: string | null;
}

export interface RuleResult {
  check_id: string;
  rule_pack_version: string;
  status: string;
  severity: string;
  reason: string;
  rule_reference: string | null;
  evidence: Array<{ field?: string | null; value?: unknown; page?: number | null; note?: string | null }>;
  data_sources: Array<{ source_id: string; version?: string | null; snapshot_id?: string | null }>;
  recommended_action: string | null;
}

export interface IdentityEvidence {
  role: string;
  raw_name: string | null;
  normalized_name: string | null;
  country: string | null;
  lei: {
    lei: string | null;
    legal_name: string | null;
    source: string;
    retrieved_at: string | null;
    snapshot_id: string | null;
    is_exact_document_match: boolean;
  } | null;
  vlei: {
    status: string;
    source: string;
    data_label: string | null;
  } | null;
  registry_candidates: Array<{
    candidate_name: string;
    source: string;
    score: number | null;
  }>;
  resolution_status: string;
}

export interface AgentResponse {
  agent: string;
  round: number;
  status: string;
  claims?: Array<{ field_path: string; value?: unknown; reason?: string }>;
  challenges?: Array<{ field_path: string; challenge_type?: string; reason?: string }>;
  reason?: string | null;
}

export interface AuditEvent {
  event_id?: string;
  event_type: string;
  actor: string;
  case_id?: string | null;
  at?: string;
  created_at?: string;
  payload?: Record<string, unknown>;
}

export interface WorkbenchPayload {
  case: CaseRecord;
  documents: DocumentMeta[];
  policy: DocumentPolicyEvaluation;
  invoice_extraction: InvoiceExtraction | null;
  bol_extraction: Record<string, unknown> | null;
  agent_trace: AgentResponse[];
  debate_rounds_used: number | null;
  findings: RuleResult[];
  risk_route: string | null;
  reconciliation: ReconciliationResult | null;
  identities: IdentityEvidence[];
  audit: AuditEvent[];
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
