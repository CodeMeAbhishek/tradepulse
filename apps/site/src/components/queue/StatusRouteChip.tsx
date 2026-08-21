import type { CaseStatus, ReadinessRoute } from "@/lib/mock/types";
import { readinessLabel } from "@/lib/mock/labels";

/**
 * Severity rides on the left rule, not on a tinted pill and not on the text.
 *
 * Two reasons. The site paints status as a hairline plus a label and never
 * tints a panel, so tinted chips read as a foreign component. And --amber
 * measures ~2.8:1 against paper, so amber *text* is unreadable at this size --
 * keeping the label in ink means the wording always carries the meaning and
 * the colour is reinforcement, which is what the UI rules require anyway.
 */
function toneClass(route: ReadinessRoute): string {
  switch (route) {
    case "READY_FOR_HUMAN_REVIEW":
      return "border-l-verified";
    case "REVIEW_REQUIRED":
    case "MAKER_REVIEW_REQUIRED":
      return "border-l-amber";
    case "HIGH_RISK_ESCALATION":
      return "border-l-stamp";
    case "DOCUMENT_PACK_INCOMPLETE":
    case "DATA_REVIEW_REQUIRED":
    default:
      return "border-l-rule";
  }
}

export function StatusRouteChip({
  status,
  readinessRoute,
}: {
  status: CaseStatus;
  readinessRoute: ReadinessRoute;
}) {
  return (
    <div className="flex flex-col gap-1">
      <span
        className={`text-label inline-flex w-fit items-center border-l-2 pl-2 text-ink ${toneClass(readinessRoute)}`}
      >
        {readinessLabel(readinessRoute)}
      </span>
      <span className="font-mono text-[11px] text-slate">Status code: {status}</span>
    </div>
  );
}
