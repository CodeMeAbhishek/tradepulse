"""Shared enums for TradePulse domain contracts."""

from __future__ import annotations

from enum import StrEnum


class CaseState(StrEnum):
    INGESTED = "INGESTED"
    PROCESSING = "PROCESSING"
    EXTRACTION_REVIEW = "EXTRACTION_REVIEW"
    PENDING_MAKER = "PENDING_MAKER"
    INVESTIGATION_REQUIRED = "INVESTIGATION_REQUIRED"
    MAKER_APPROVED = "MAKER_APPROVED"
    CHECKER_APPROVED = "CHECKER_APPROVED"
    CHECKER_REJECTED = "CHECKER_REJECTED"
    PROCESSING_FAILED = "PROCESSING_FAILED"


class TradeProfile(StrEnum):
    """Canonical transaction profiles from system design. Document policy is data-driven."""

    INVOICE_ONLY_PRE_REVIEW = "INVOICE_ONLY_PRE_REVIEW"
    POST_SHIPMENT_DOCUMENT_REVIEW = "POST_SHIPMENT_DOCUMENT_REVIEW"
    LC_DOCUMENT_REVIEW = "LC_DOCUMENT_REVIEW"
    DOCUMENTARY_COLLECTION_REVIEW = "DOCUMENTARY_COLLECTION_REVIEW"
    ENHANCED_TRADE_HOUSE_REVIEW = "ENHANCED_TRADE_HOUSE_REVIEW"
    DOMESTIC_INDIA_GOODS_MOVEMENT = "DOMESTIC_INDIA_GOODS_MOVEMENT"
    MERCHANT_SHIPMENT_READINESS = "MERCHANT_SHIPMENT_READINESS"


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
    COMMERCIAL_INVOICE = "commercial_invoice"
    BILL_OF_LADING = "bill_of_lading"
    PACKING_LIST = "packing_list"
    LC_TERMS_LITE = "lc_terms_lite"
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
