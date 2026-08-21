/**
 * Lightweight invariant checks for queue mocks (no test runner required).
 * Run: npx tsx lib/mocks/check-invariants.ts
 */
import { MOCK_QUEUE_CASES } from "./queue";

const ALLOWED_ROUTES = new Set([
  "STP_CANDIDATE",
  "EXTRACTION_REVIEW",
  "HIGH_RISK_REVIEW",
  null,
]);

let failures = 0;

for (const row of MOCK_QUEUE_CASES) {
  const { summary, source_freshness } = row;
  if (summary.data_label !== "SYNTHETIC") {
    console.error(`${summary.case_id}: data_label must be SYNTHETIC`);
    failures += 1;
  }
  if (source_freshness === "live") {
    console.error(
      `${summary.case_id}: must not claim live freshness without labelled fixture policy`,
    );
    failures += 1;
  }
  if (!ALLOWED_ROUTES.has(summary.risk_route)) {
    console.error(`${summary.case_id}: unexpected risk_route ${summary.risk_route}`);
    failures += 1;
  }
}

if (failures > 0) {
  console.error(`Invariant check failed: ${failures} issue(s)`);
  process.exit(1);
}

console.log(`OK — ${MOCK_QUEUE_CASES.length} synthetic queue rows passed invariants`);
