import type { RegWatchEvent } from "./types";

export const MOCK_REGWATCH_EVENTS: RegWatchEvent[] = [
  {
    id: "rw-001",
    sourceName: "IFSCA circular snapshot (demo)",
    publisher: "IFSCA",
    detectedAt: "2026-08-20T08:00:00Z",
    summary:
      "Proposed update to documentary checklist wording for enhanced trade-house reviews.",
    proposedDiff:
      "+ Require Certificate of Origin when corridor policy flag ENHANCED_ORIGIN=true\n- Keep CoO optional for baseline post-shipment profile",
    approvalState: "PROPOSED",
    replayAllowed: false,
    oldResultSummary: "Active rule pack v0.4 — CoO conditional, non-blocking in baseline.",
    newResultSummary:
      "Proposed pack v0.4.1 — not active until human approval. Replay would create a new result version.",
  },
  {
    id: "rw-002",
    sourceName: "Demo sanctions publisher checksum",
    publisher: "DEMO_MOCK_WATCHLIST",
    detectedAt: "2026-08-18T16:20:00Z",
    summary: "Snapshot checksum change detected on demo list.",
    proposedDiff: "~ Replace screen-snap-demo-01 with screen-snap-demo-02",
    approvalState: "APPROVED",
    replayAllowed: true,
    oldResultSummary: "Cases evaluated on screen-snap-demo-01 retained as prior result versions.",
    newResultSummary:
      "Approved pack references screen-snap-demo-02. Selective replay appends new versions; history not overwritten.",
  },
];

export function getRegWatchEvents(): RegWatchEvent[] {
  return [...MOCK_REGWATCH_EVENTS];
}

export function getRegWatchEvent(id: string): RegWatchEvent | undefined {
  return MOCK_REGWATCH_EVENTS.find((e) => e.id === id);
}
