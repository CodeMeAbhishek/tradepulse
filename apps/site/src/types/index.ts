// Handoff contract. A Python FastAPI service returns exactly these shapes.

export interface ExtractionResult {
  item: string;
  quantity: string;
  unit_price: string;
  currency: string;
  buyer: string;
  seller: string;
  invoice_date: string;
  shipment_terms: string;
}

export interface VerificationResult {
  entity: string;
  match_status: "clear" | "potential_match" | "confirmed_match";
  matched_name: string | null;
  confidence: number;
  source_list: string;
}

export interface PriceAuditResult {
  item: string;
  declared_price: number;
  benchmark_price: number;
  deviation_pct: number;
  flagged: boolean;
  threshold_pct: number;
}

export type Severity = "critical" | "review" | "passed";

export type DocumentKind =
  "invoice" | "billOfLading" | "packingList" | "certificateOfOrigin" | "mt700";

export type AgentName = "extraction" | "consistency" | "price" | "sanctions";

/** Normalised fractions of the document plane, 0–1. Never pixels. */
export interface Region {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Finding {
  id: string;
  severity: Severity;
  title: string;
  body: string;
  sourceDoc: string;
  sourceKind: DocumentKind;
  page: number;
  field: string;
  agent: AgentName;
  ucpArticle: string | null;
  type: "single" | "cross_document";
  region: Region;
  secondRegion?: Region;
  secondDoc?: string;
  secondKind?: DocumentKind;
}

export interface DocumentSetResult {
  document_id: string;
  extraction: ExtractionResult;
  verification: VerificationResult[];
  price_audit: PriceAuditResult;
  risk_level: "green" | "amber" | "red";
  findings: Finding[];
}
