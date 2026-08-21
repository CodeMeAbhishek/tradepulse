/**
 * Workbench display types — pre-computed mock payloads only.
 * No policy / identity / sanctions logic in the browser.
 */

export type TransactionProfile =
  | "INVOICE_ONLY_PRE_REVIEW"
  | "POST_SHIPMENT_DOCUMENT_REVIEW"
  | "LC_DOCUMENT_REVIEW"
  | "DOCUMENTARY_COLLECTION_REVIEW"
  | "ENHANCED_TRADE_HOUSE_REVIEW"
  | "DOMESTIC_INDIA_GOODS_MOVEMENT";

export type CaseStatus =
  | "DRAFT"
  | "READY_FOR_HUMAN_REVIEW"
  | "REVIEW_REQUIRED"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "DATA_REVIEW_REQUIRED"
  | "MAKER_REVIEW_REQUIRED"
  | "HIGH_RISK_ESCALATION";

export type ReadinessRoute =
  | "READY_FOR_HUMAN_REVIEW"
  | "REVIEW_REQUIRED"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "DATA_REVIEW_REQUIRED"
  | "MAKER_REVIEW_REQUIRED"
  | "HIGH_RISK_ESCALATION";

export type DocumentRequirementState =
  | "REQUIRED"
  | "CONDITIONALLY_REQUIRED"
  | "OPTIONAL"
  | "NOT_APPLICABLE"
  | "NOT_PROVIDED"
  | "NOT_AVAILABLE"
  | "PROVIDED"
  | "DOCUMENT_PACK_INCOMPLETE";

export interface DocumentCompletenessItem {
  documentType: string;
  state: DocumentRequirementState;
  label: string;
  blocker: boolean;
  reason: string;
}

export interface QueueCase {
  id: string;
  reference: string;
  counterparty: string;
  corridor: string;
  profile: TransactionProfile;
  status: CaseStatus;
  readinessRoute: ReadinessRoute;
  documentCompleteness: DocumentCompletenessItem[];
  updatedAt: string;
  dataSourceLabel: "SYNTHETIC_DEMO";
}

export type FindingOutcome =
  | "PASS"
  | "REVIEW_REQUIRED"
  | "DATA_UNAVAILABLE"
  | "NOT_AVAILABLE"
  | "NOT_APPLICABLE"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "POTENTIAL_MATCH";

export type IdentityOutcomeLabel =
  | "IDENTITY_VERIFIED_BY_LEI"
  | "IDENTITY_SUPPORTED_BY_VLEI"
  | "POTENTIAL_ENTITY_MATCH_REVIEW"
  | "IDENTITY_UNRESOLVED"
  | "IDENTITY_SOURCE_UNAVAILABLE"
  | "VLEI_NOT_CONFIGURED";

export type VleiStatus =
  | "VERIFIED_LIVE"
  | "VERIFIED_FIXTURE"
  | "NOT_CONFIGURED"
  | "EXPIRED"
  | "INVALID"
  | "REVOKED"
  | "DATA_UNAVAILABLE";

export interface ExtractedField {
  fieldPath: string;
  label: string;
  value: string;
  confidence: "HIGH" | "MEDIUM" | "LOW" | "REVIEW_REQUIRED";
  evidence: {
    page: number;
    sourceText: string;
  } | null;
}

export interface AgentClaim {
  fieldPath: string;
  proposedValue: string;
  reason: string;
  hasEvidence: boolean;
}

export interface AgentChallenge {
  fieldPath: string;
  category: string;
  reason: string;
}

export interface AgentRoundTrace {
  round: number;
  extractor: { status: string; claims: AgentClaim[] };
  validator: { status: string; claims: AgentClaim[] };
  challenger: { status: string; challenges: AgentChallenge[] };
  arbiter: {
    status: "COMPLETE" | "REVIEW_REQUIRED";
    decisionSummary: string;
    agreement: boolean;
  };
}

export interface ReconRow {
  field: string;
  invoiceValue: string | null;
  bolValue: string | null;
  outcome: FindingOutcome;
  note: string;
}

export interface IdentityParty {
  role: string;
  rawName: string;
  normalizedName: string;
  lei: string | null;
  leiStatus: string;
  gleifCandidates: Array<{
    lei: string;
    legalName: string;
    similarityNote: string;
    isExactDocumentMatch: boolean;
  }>;
  vleiStatus: VleiStatus;
  vleiLabel: string;
  identityOutcome: IdentityOutcomeLabel;
  source: string;
  retrievedAt: string | null;
  snapshotId: string | null;
}

export interface FindingCard {
  id: string;
  title: string;
  outcome: FindingOutcome;
  summary: string;
  sourceLabel: string;
  snapshotId: string | null;
  ruleId: string | null;
  detail: string;
}

export interface AuditEvent {
  id: string;
  at: string;
  actor: string;
  action: string;
  detail: string;
}

export interface MakerCheckerState {
  makerDecision: string | null;
  checkerDecision: string | null;
  blockedReason: string | null;
  allowedActions: string[];
}

export interface RegWatchEvent {
  id: string;
  sourceName: string;
  publisher: string;
  detectedAt: string;
  summary: string;
  proposedDiff: string;
  approvalState: "PROPOSED" | "APPROVED" | "REJECTED";
  replayAllowed: boolean;
  oldResultSummary: string;
  newResultSummary: string;
}

export interface CaseWorkbenchDetail {
  caseId: string;
  uploadedFiles: Array<{ name: string; documentType: string; sizeLabel: string }>;
  checklist: DocumentCompletenessItem[];
  invoiceFields: ExtractedField[];
  agentTrace: AgentRoundTrace[];
  reconciliation: {
    bolPresent: boolean;
    outcome: FindingOutcome;
    explanation: string;
    rows: ReconRow[];
  };
  identities: IdentityParty[];
  findings: FindingCard[];
  makerChecker: MakerCheckerState;
  audit: AuditEvent[];
}
