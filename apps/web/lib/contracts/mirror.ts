/**
 * Temporary TypeScript mirror of Abhishek’s frozen contracts
 * (`packages/contracts/tradepulse_contracts` on feat/platform-skeleton @ 71c24d1).
 *
 * That commit is not available on origin yet. Do NOT expand this shape privately.
 * When packages/contracts lands, replace imports with the shared package / generated types
 * and delete this mirror. Open a contract task with Abhishek + Shivansh for any gap.
 */

/** Human decision / case lifecycle states (system-design state machine). */
export type CaseState =
  | "INGESTED"
  | "PROCESSING"
  | "EXTRACTION_REVIEW"
  | "PENDING_MAKER"
  | "INVESTIGATION_REQUIRED"
  | "MAKER_APPROVED"
  | "CHECKER_APPROVED"
  | "CHECKER_REJECTED";

/**
 * Dataset / presentation provenance label.
 * Hackathon queue fixtures use SYNTHETIC only.
 */
export type DataLabel =
  | "SYNTHETIC"
  | "CACHED"
  | "LIVE"
  | "REFERENCE"
  | "PLANNED"
  | "UNAVAILABLE";

/**
 * Reference-data freshness vocabulary from Abhishek’s frozen contracts.
 * Never claim "live" unless a fixture is explicitly labelled as such.
 */
export type FreshnessLabel =
  | "synthetic"
  | "cached"
  | "live"
  | "stale"
  | "unavailable"
  | "planned";

export interface FreshnessInfo {
  label: FreshnessLabel;
  /** ISO-8601 timestamp when the underlying snapshot was taken, if known. */
  as_of: string | null;
  note: string | null;
}

/**
 * PRD-safe risk route strings until RiskRoute is a closed enum in contracts.
 * Do not invent numeric risk scores.
 */
export type RiskRouteLabel =
  | "STP_CANDIDATE"
  | "EXTRACTION_REVIEW"
  | "HIGH_RISK_REVIEW"
  | null;

export interface CaseSummary {
  case_id: string;
  status: CaseState;
  /** Open string until closed RiskRoute enum lands; use RiskRouteLabel values only. */
  risk_route: string | null;
  sla_due_at: string | null;
  assignee: string | null;
  data_label: DataLabel;
  corridor: string;
  buyer_name: string;
  seller_name: string;
  highest_severity_reason: string | null;
}

/**
 * Full case envelope — queue workbench only needs summary fields.
 * Additional CaseRecord members stay undefined until contracts are imported.
 */
export interface CaseRecord {
  case_id: string;
  summary: CaseSummary;
}

/**
 * Queue row view-model.
 * `source_freshness` is a parallel mock field until CaseSummary.source_freshness
 * is added to packages/contracts (do not fork into CaseSummary itself).
 */
export interface QueueCaseRow {
  summary: CaseSummary;
  source_freshness: FreshnessLabel;
  freshness: FreshnessInfo;
}

export const DATA_LABEL_DISPLAY: Record<DataLabel, string> = {
  SYNTHETIC: "Synthetic",
  CACHED: "Cached",
  LIVE: "Live",
  REFERENCE: "Reference",
  PLANNED: "Planned",
  UNAVAILABLE: "Unavailable",
};

export const FRESHNESS_LABEL_DISPLAY: Record<FreshnessLabel, string> = {
  synthetic: "Synthetic",
  cached: "Cached",
  live: "Live / reference",
  stale: "Stale",
  unavailable: "Unavailable",
  planned: "Planned",
};

export const CASE_STATE_DISPLAY: Record<CaseState, string> = {
  INGESTED: "Ingested",
  PROCESSING: "Processing",
  EXTRACTION_REVIEW: "Extraction review",
  PENDING_MAKER: "Pending maker",
  INVESTIGATION_REQUIRED: "Investigation required",
  MAKER_APPROVED: "Maker approved",
  CHECKER_APPROVED: "Checker approved",
  CHECKER_REJECTED: "Checker rejected",
};

export function riskRouteDisplay(route: string | null): string {
  switch (route) {
    case "STP_CANDIDATE":
      return "STP candidate — subject to institution policy and human review";
    case "EXTRACTION_REVIEW":
      return "Extraction review required";
    case "HIGH_RISK_REVIEW":
      return "High-risk review required";
    case null:
      return "Route not assigned";
    default:
      return route;
  }
}
