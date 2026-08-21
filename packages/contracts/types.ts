/**
 * Mirrored canonical TradePulse enums for frontend consumption.
 * Source of truth: packages/contracts/enums.py
 * Do not invent additional literals here without updating enums.py + tests.
 */

export const TradeProfile = {
  PRE_SHIPMENT_TRADE_FINANCE: "PRE_SHIPMENT_TRADE_FINANCE",
  LC_ISSUANCE_AMENDMENT: "LC_ISSUANCE_AMENDMENT",
  POST_SHIPMENT_LC_PRESENTATION: "POST_SHIPMENT_LC_PRESENTATION",
  DOCUMENTARY_COLLECTION: "DOCUMENTARY_COLLECTION",
  TRADE_CREDIT_FACTORING: "TRADE_CREDIT_FACTORING",
  TRADE_HOUSE_COMPLIANCE_REVIEW: "TRADE_HOUSE_COMPLIANCE_REVIEW",
} as const;
export type TradeProfile = (typeof TradeProfile)[keyof typeof TradeProfile];

export const ShipmentMode = {
  OCEAN: "OCEAN",
  AIR: "AIR",
  MULTIMODAL: "MULTIMODAL",
  UNKNOWN: "UNKNOWN",
} as const;
export type ShipmentMode = (typeof ShipmentMode)[keyof typeof ShipmentMode];

export const TransactionStage = {
  BEFORE_SHIPMENT: "BEFORE_SHIPMENT",
  AFTER_SHIPMENT_LOADING: "AFTER_SHIPMENT_LOADING",
  POST_SHIPMENT_DOCUMENT_PRESENTATION: "POST_SHIPMENT_DOCUMENT_PRESENTATION",
} as const;
export type TransactionStage =
  (typeof TransactionStage)[keyof typeof TransactionStage];

/** Human review roles. SYSTEM is machine-only (see enums.py). */
export const ReviewRole = {
  SCRUTINY: "SCRUTINY",
  MAKER: "MAKER",
  CHECKER: "CHECKER",
  SYSTEM: "SYSTEM",
} as const;
export type ReviewRole = (typeof ReviewRole)[keyof typeof ReviewRole];

export const CaseWorkflowAction = {
  SCRUTINY_COMPLETE: "scrutiny_complete",
  MAKER_RECOMMEND: "maker_recommend",
  MAKER_REQUEST_INFO: "maker_request_info",
  CHECKER_APPROVE: "checker_approve",
  CHECKER_RETURN: "checker_return",
  CHECKER_ESCALATE: "checker_escalate",
} as const;
export type CaseWorkflowAction =
  (typeof CaseWorkflowAction)[keyof typeof CaseWorkflowAction];

export const CaseStatus = {
  DRAFT: "DRAFT",
  SCRUTINY_IN_PROGRESS: "SCRUTINY_IN_PROGRESS",
  DOCUMENT_PACK_INCOMPLETE: "DOCUMENT_PACK_INCOMPLETE",
  SCRUTINY_COMPLETE: "SCRUTINY_COMPLETE",
  MAKER_REVIEW: "MAKER_REVIEW",
  INFORMATION_REQUESTED: "INFORMATION_REQUESTED",
  MAKER_RECOMMENDED: "MAKER_RECOMMENDED",
  CHECKER_REVIEW: "CHECKER_REVIEW",
  RETURNED_TO_MAKER: "RETURNED_TO_MAKER",
  CHECKER_APPROVED: "CHECKER_APPROVED",
  ESCALATED: "ESCALATED",
  PROCESSING_FAILED: "PROCESSING_FAILED",
} as const;
export type CaseStatus = (typeof CaseStatus)[keyof typeof CaseStatus];

export const ReadinessRoute = {
  READY_FOR_HUMAN_REVIEW: "READY_FOR_HUMAN_REVIEW",
  DOCUMENT_PACK_INCOMPLETE: "DOCUMENT_PACK_INCOMPLETE",
  EXTRACTION_REVIEW_REQUIRED: "EXTRACTION_REVIEW_REQUIRED",
  MAKER_REVIEW_REQUIRED: "MAKER_REVIEW_REQUIRED",
  CHECKER_REVIEW_REQUIRED: "CHECKER_REVIEW_REQUIRED",
  HIGH_RISK_ESCALATION: "HIGH_RISK_ESCALATION",
  DATA_REVIEW_REQUIRED: "DATA_REVIEW_REQUIRED",
} as const;
export type ReadinessRoute = (typeof ReadinessRoute)[keyof typeof ReadinessRoute];

export const DocumentType = {
  TRADE_FINANCE_APPLICATION: "TRADE_FINANCE_APPLICATION",
  COMMERCIAL_INVOICE: "COMMERCIAL_INVOICE",
  BILL_OF_LADING: "BILL_OF_LADING",
  AIR_WAYBILL: "AIR_WAYBILL",
  PACKING_LIST: "PACKING_LIST",
  CERTIFICATE_OF_ORIGIN: "CERTIFICATE_OF_ORIGIN",
  LETTER_OF_CREDIT: "LETTER_OF_CREDIT",
  BILL_OF_EXCHANGE: "BILL_OF_EXCHANGE",
  INSURANCE_CERTIFICATE: "INSURANCE_CERTIFICATE",
  KYC_KYB_EVIDENCE: "KYC_KYB_EVIDENCE",
  SHIPPING_BILL: "SHIPPING_BILL",
  BILL_OF_ENTRY: "BILL_OF_ENTRY",
  INSPECTION_CERTIFICATE: "INSPECTION_CERTIFICATE",
  OTHER: "OTHER",
} as const;
export type DocumentType = (typeof DocumentType)[keyof typeof DocumentType];

export const DocumentRequirementState = {
  REQUIRED: "REQUIRED",
  CONDITIONALLY_REQUIRED: "CONDITIONALLY_REQUIRED",
  OPTIONAL: "OPTIONAL",
  NOT_APPLICABLE: "NOT_APPLICABLE",
  NOT_PROVIDED: "NOT_PROVIDED",
  POLICY_CONFIGURATION_REQUIRED: "POLICY_CONFIGURATION_REQUIRED",
} as const;
export type DocumentRequirementState =
  (typeof DocumentRequirementState)[keyof typeof DocumentRequirementState];

export const CheckStatus = {
  PASS: "PASS",
  WARN: "WARN",
  REVIEW_REQUIRED: "REVIEW_REQUIRED",
  FAIL: "FAIL",
  NOT_APPLICABLE: "NOT_APPLICABLE",
  NOT_AVAILABLE: "NOT_AVAILABLE",
  DATA_UNAVAILABLE: "DATA_UNAVAILABLE",
} as const;
export type CheckStatus = (typeof CheckStatus)[keyof typeof CheckStatus];

export const AgentName = {
  EXTRACTOR: "EXTRACTOR",
  VALIDATOR: "VALIDATOR",
  CHALLENGER: "CHALLENGER",
  ARBITER: "ARBITER",
  CROSS_DOCUMENT_RECONCILER: "CROSS_DOCUMENT_RECONCILER",
} as const;
export type AgentName = (typeof AgentName)[keyof typeof AgentName];

export const VLEIVerificationStatus = {
  VERIFIED_LIVE: "VERIFIED_LIVE",
  VERIFIED_FIXTURE: "VERIFIED_FIXTURE",
  INVALID: "INVALID",
  EXPIRED: "EXPIRED",
  REVOKED: "REVOKED",
  NOT_CONFIGURED: "NOT_CONFIGURED",
  DATA_UNAVAILABLE: "DATA_UNAVAILABLE",
} as const;
export type VLEIVerificationStatus =
  (typeof VLEIVerificationStatus)[keyof typeof VLEIVerificationStatus];

export const IdentityResolutionStatus = {
  IDENTITY_VERIFIED_BY_LEI: "IDENTITY_VERIFIED_BY_LEI",
  IDENTITY_SUPPORTED_BY_VLEI: "IDENTITY_SUPPORTED_BY_VLEI",
  POTENTIAL_ENTITY_MATCH_REVIEW: "POTENTIAL_ENTITY_MATCH_REVIEW",
  IDENTITY_UNRESOLVED: "IDENTITY_UNRESOLVED",
  IDENTITY_SOURCE_UNAVAILABLE: "IDENTITY_SOURCE_UNAVAILABLE",
} as const;
export type IdentityResolutionStatus =
  (typeof IdentityResolutionStatus)[keyof typeof IdentityResolutionStatus];

export const SourceMode = {
  OFFICIAL_LIVE: "OFFICIAL_LIVE",
  OFFICIAL_CACHED: "OFFICIAL_CACHED",
  CREDIBLE_AGGREGATOR: "CREDIBLE_AGGREGATOR",
  SYNTHETIC_DEMO: "SYNTHETIC_DEMO",
  NOT_CONFIGURED: "NOT_CONFIGURED",
  DATA_UNAVAILABLE: "DATA_UNAVAILABLE",
} as const;
export type SourceMode = (typeof SourceMode)[keyof typeof SourceMode];

/**
 * Runtime API upload DocumentType uses snake_case in tradepulse_contracts.
 * Map canonical UPPER_SNAKE → API form value when posting multipart uploads.
 */
export const DocumentTypeApiUpload: Record<DocumentType, string> = {
  TRADE_FINANCE_APPLICATION: "trade_finance_application",
  COMMERCIAL_INVOICE: "commercial_invoice",
  BILL_OF_LADING: "bill_of_lading",
  AIR_WAYBILL: "air_waybill",
  PACKING_LIST: "packing_list",
  CERTIFICATE_OF_ORIGIN: "certificate_of_origin",
  LETTER_OF_CREDIT: "lc_terms_lite",
  BILL_OF_EXCHANGE: "bill_of_exchange",
  INSURANCE_CERTIFICATE: "insurance_certificate",
  KYC_KYB_EVIDENCE: "kyc_kyb_evidence",
  SHIPPING_BILL: "shipping_bill",
  BILL_OF_ENTRY: "bill_of_entry",
  INSPECTION_CERTIFICATE: "inspection_certificate",
  OTHER: "unsupported",
};
