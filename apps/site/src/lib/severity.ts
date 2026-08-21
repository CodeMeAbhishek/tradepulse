import type { Severity } from "@/types";

// Static maps only. A Tailwind class is never assembled from a variable.
export const SEVERITY_LABEL: Record<Severity, string> = {
  critical: "CRITICAL",
  review: "NEEDS REVIEW",
  passed: "PASSED",
};

/** #C1272D reaches the page only through the `critical` entry. */
export const SEVERITY_COLOR: Record<Severity, string> = {
  critical: "var(--stamp)",
  review: "var(--amber)",
  passed: "var(--verified)",
};

export const SEVERITY_TEXT: Record<Severity, string> = {
  critical: "text-stamp",
  review: "text-amber",
  passed: "text-verified",
};

export const AGENT_LABEL = {
  extraction: "EXTRACTION",
  consistency: "CROSS-DOCUMENT CONSISTENCY · UCP 600",
  price: "PRICE VERIFICATION · UN COMTRADE",
  sanctions: "SANCTIONS SCREENING",
} as const;

export const AGENT_ORDER = ["extraction", "consistency", "price", "sanctions"] as const;
