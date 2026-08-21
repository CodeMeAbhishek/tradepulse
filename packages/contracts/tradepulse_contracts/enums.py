"""Shared enums for TradePulse domain contracts."""

from __future__ import annotations

from enum import StrEnum


class CaseState(StrEnum):
    """Aligned with canonical CaseStatus (Scrutiny → Maker → Checker)."""

    DRAFT = "DRAFT"
    SCRUTINY_IN_PROGRESS = "SCRUTINY_IN_PROGRESS"
    DOCUMENT_PACK_INCOMPLETE = "DOCUMENT_PACK_INCOMPLETE"
    SCRUTINY_COMPLETE = "SCRUTINY_COMPLETE"
    MAKER_REVIEW = "MAKER_REVIEW"
    INFORMATION_REQUESTED = "INFORMATION_REQUESTED"
    MAKER_RECOMMENDED = "MAKER_RECOMMENDED"
    CHECKER_REVIEW = "CHECKER_REVIEW"
    RETURNED_TO_MAKER = "RETURNED_TO_MAKER"
    CHECKER_APPROVED = "CHECKER_APPROVED"
    ESCALATED = "ESCALATED"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class TradeProfile(StrEnum):
    """Application-led profiles. No parallel hackathon literals."""

    PRE_SHIPMENT_TRADE_FINANCE = "PRE_SHIPMENT_TRADE_FINANCE"
    LC_ISSUANCE_AMENDMENT = "LC_ISSUANCE_AMENDMENT"
    POST_SHIPMENT_LC_PRESENTATION = "POST_SHIPMENT_LC_PRESENTATION"
    DOCUMENTARY_COLLECTION = "DOCUMENTARY_COLLECTION"
    TRADE_CREDIT_FACTORING = "TRADE_CREDIT_FACTORING"
    TRADE_HOUSE_COMPLIANCE_REVIEW = "TRADE_HOUSE_COMPLIANCE_REVIEW"


class ShipmentMode(StrEnum):
    OCEAN = "OCEAN"
    AIR = "AIR"
    MULTIMODAL = "MULTIMODAL"
    UNKNOWN = "UNKNOWN"


class TransactionStage(StrEnum):
    BEFORE_SHIPMENT = "BEFORE_SHIPMENT"
    AFTER_SHIPMENT_LOADING = "AFTER_SHIPMENT_LOADING"
    POST_SHIPMENT_DOCUMENT_PRESENTATION = "POST_SHIPMENT_DOCUMENT_PRESENTATION"


class ReviewRole(StrEnum):
    SCRUTINY = "SCRUTINY"
    MAKER = "MAKER"
    CHECKER = "CHECKER"
    SYSTEM = "SYSTEM"


class IdentityPartyRole(StrEnum):
    SELLER = "SELLER"
    BUYER = "BUYER"
    SHIPPER = "SHIPPER"
    CONSIGNEE = "CONSIGNEE"
    NOTIFY_PARTY = "NOTIFY_PARTY"
    VESSEL = "VESSEL"
    SIGNATORY = "SIGNATORY"


class IdentityResolutionStatus(StrEnum):
    """Permitted identity outcomes. Fuzzy name similarity alone never verifies identity."""

    IDENTITY_VERIFIED_BY_LEI = "IDENTITY_VERIFIED_BY_LEI"
    IDENTITY_SUPPORTED_BY_VLEI = "IDENTITY_SUPPORTED_BY_VLEI"
    POTENTIAL_ENTITY_MATCH_REVIEW = "POTENTIAL_ENTITY_MATCH_REVIEW"
    IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"
    IDENTITY_SOURCE_UNAVAILABLE = "IDENTITY_SOURCE_UNAVAILABLE"
    VLEI_NOT_CONFIGURED = "VLEI_NOT_CONFIGURED"


class LEIEvidenceSource(StrEnum):
    GLEIF = "GLEIF"
    DOCUMENT = "DOCUMENT"
    FIXTURE = "FIXTURE"


class VLEIVerificationStatus(StrEnum):
    """Fixture verifier may only emit VERIFIED_FIXTURE, never VERIFIED_LIVE."""

    VERIFIED_LIVE = "VERIFIED_LIVE"
    VERIFIED_FIXTURE = "VERIFIED_FIXTURE"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"


class DocumentType(StrEnum):
    """API upload vocabulary (snake_case). Map to canonical UPPER_SNAKE in policies/UI.

    LETTER_OF_CREDIT ↔ lc_terms_lite for demo LC-terms uploads.
    """

    TRADE_FINANCE_APPLICATION = "trade_finance_application"
    COMMERCIAL_INVOICE = "commercial_invoice"
    BILL_OF_LADING = "bill_of_lading"
    AIR_WAYBILL = "air_waybill"
    PACKING_LIST = "packing_list"
    LC_TERMS_LITE = "lc_terms_lite"
    SHIPPING_BILL = "shipping_bill"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    BILL_OF_EXCHANGE = "bill_of_exchange"
    KYC_KYB_EVIDENCE = "kyc_kyb_evidence"
    UNSUPPORTED = "unsupported"


class DocumentProcessingState(StrEnum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    VALIDATED = "VALIDATED"
    EXTRACTION_REVIEW = "EXTRACTION_REVIEW"
    FAILED = "FAILED"


class CheckStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"


class Severity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExtractionValidationStatus(StrEnum):
    PASS = "PASS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INVALID = "INVALID"


class AgentName(StrEnum):
    EXTRACTOR = "extractor"
    VALIDATOR = "validator"
    CHALLENGER = "challenger"
    ARBITER = "arbiter"
    CROSS_DOCUMENT_CHECKER = "cross_document_checker"


class AgentRunStatus(StrEnum):
    COMPLETE = "COMPLETE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAILED = "FAILED"


class ChallengeType(StrEnum):
    CROSS_DOCUMENT_CONFLICT = "CROSS_DOCUMENT_CONFLICT"
    SOURCE_AMBIGUITY = "SOURCE_AMBIGUITY"
    ARITHMETIC_CONFLICT = "ARITHMETIC_CONFLICT"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"


class FieldResolutionStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


class SourceAccessType(StrEnum):
    API = "API"
    RSS = "RSS"
    DOWNLOAD = "DOWNLOAD"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class SourceRegistryStatus(StrEnum):
    LIVE = "LIVE"
    CACHED = "CACHED"
    DEGRADED = "DEGRADED"
    PLANNED = "PLANNED"


class FreshnessLabel(StrEnum):
    """User-visible data freshness labels. Never invent live status without evidence."""

    LIVE = "live"
    CACHED = "cached"
    STALE = "stale"
    SYNTHETIC = "synthetic"
    UNAVAILABLE = "unavailable"
    PLANNED = "planned"


class DataLabel(StrEnum):
    SYNTHETIC = "synthetic"
    REFERENCE = "reference"
    CACHED = "cached"
    LIVE = "live"
