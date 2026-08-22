import type { FindingTone, RiskRoute, WorkflowState } from "@/lib/demo/store";
import { riskLabel, workflowLabel } from "@/lib/demo/store";

export function RiskChip({ route }: { route: RiskRoute }) {
  const tone =
    route === "READY_FOR_HUMAN_REVIEW"
      ? "tp-chip-ok"
      : route === "DOCUMENT_PACK_INCOMPLETE" || route === "DATA_REVIEW_REQUIRED"
        ? "tp-chip-info"
        : route === "HIGH_RISK_ESCALATION"
          ? "tp-chip-block"
          : "tp-chip-review";
  return <span className={`tp-chip ${tone}`}>{riskLabel(route)}</span>;
}

export function WorkflowChip({ state }: { state: WorkflowState }) {
  return <span className="tp-chip tp-chip-neutral">{workflowLabel(state)}</span>;
}

export function ToneChip({ tone, label }: { tone: FindingTone; label: string }) {
  const cls =
    tone === "clear"
      ? "tp-chip-ok"
      : tone === "review"
        ? "tp-chip-review"
        : tone === "block"
          ? "tp-chip-block"
          : "tp-chip-info";
  return <span className={`tp-chip ${cls}`}>{label}</span>;
}

/** Red-gradient flag for document mismatches (coach: not soft amber). */
export function MismatchFlag({ label = "Mismatch" }: { label?: string }) {
  return <span className="tp-flag-mismatch">{label}</span>;
}
