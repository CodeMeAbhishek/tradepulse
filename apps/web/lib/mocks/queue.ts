import type { QueueCaseRow } from "@/lib/contracts/mirror";

/**
 * Frozen hackathon queue fixtures.
 * All rows are DataLabel.SYNTHETIC. Freshness is fixture-declared (never LIVE here).
 * No sanctions results, GLEIF hits, or numeric risk scores.
 */
export const MOCK_QUEUE_CASES: QueueCaseRow[] = [
  {
    summary: {
      case_id: "TP-2026-0001",
      status: "PENDING_MAKER",
      risk_route: "HIGH_RISK_REVIEW",
      sla_due_at: "2026-08-21T18:00:00+05:30",
      assignee: "A. Mehta",
      data_label: "SYNTHETIC",
      corridor: "IN → AE (GIFT IFSC)",
      buyer_name: "Gulf Horizon Trading LLC",
      seller_name: "Amit TRD Co.",
      highest_severity_reason:
        "Potential counterparty name similarity — review required",
    },
    source_freshness: "cached",
    freshness: {
      label: "cached",
      as_of: "2026-08-20T12:00:00Z",
      note: "Fixture-declared cached reference snapshot; not a live registry call.",
    },
  },
  {
    summary: {
      case_id: "TP-2026-0002",
      status: "EXTRACTION_REVIEW",
      risk_route: "EXTRACTION_REVIEW",
      sla_due_at: "2026-08-21T16:30:00+05:30",
      assignee: "R. Kapoor",
      data_label: "SYNTHETIC",
      corridor: "IN → SG",
      buyer_name: "Meridian Logistics Pte Ltd",
      seller_name: "Surya Exports Pvt Ltd",
      highest_severity_reason:
        "Low-confidence extraction — human review required",
    },
    source_freshness: "synthetic",
    freshness: {
      label: "synthetic",
      as_of: null,
      note: "Synthetic demo documents only.",
    },
  },
  {
    summary: {
      case_id: "TP-2026-0003",
      status: "PENDING_MAKER",
      risk_route: "STP_CANDIDATE",
      sla_due_at: "2026-08-22T10:00:00+05:30",
      assignee: null,
      data_label: "SYNTHETIC",
      corridor: "IN → GB",
      buyer_name: "Northbridge Commodities Ltd",
      seller_name: "Deccan Agri Exports",
      highest_severity_reason: null,
    },
    source_freshness: "cached",
    freshness: {
      label: "cached",
      as_of: "2026-08-19T08:00:00Z",
      note: "Fixture-declared cached snapshot for demo reliability.",
    },
  },
  {
    summary: {
      case_id: "TP-2026-0004",
      status: "INVESTIGATION_REQUIRED",
      risk_route: "HIGH_RISK_REVIEW",
      sla_due_at: "2026-08-21T15:00:00+05:30",
      assignee: "A. Mehta",
      data_label: "SYNTHETIC",
      corridor: "IN → AE",
      buyer_name: "Oasis Metals FZE",
      seller_name: "Indus Steel Traders",
      highest_severity_reason:
        "Document discrepancy — quantity mismatch across invoice and bill of lading",
    },
    source_freshness: "stale",
    freshness: {
      label: "stale",
      as_of: "2026-07-01T00:00:00Z",
      note: "Fixture marks reference snapshot as stale; not treated as pass.",
    },
  },
  {
    summary: {
      case_id: "TP-2026-0005",
      status: "PROCESSING",
      risk_route: null,
      sla_due_at: "2026-08-21T20:00:00+05:30",
      assignee: "S. Iyer",
      data_label: "SYNTHETIC",
      corridor: "IN → DE",
      buyer_name: "Rhein Trade GmbH",
      seller_name: "Coastal Spices LLP",
      highest_severity_reason: null,
    },
    source_freshness: "unavailable",
    freshness: {
      label: "unavailable",
      as_of: null,
      note: "Data unavailable — unable to pass freshness-dependent checks.",
    },
  },
];
