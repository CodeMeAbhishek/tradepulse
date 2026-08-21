import type { CaseStatus, ReadinessRoute } from "@/lib/mock/types";
import { readinessLabel } from "@/lib/mock/labels";

function toneClass(route: ReadinessRoute): string {
  switch (route) {
    case "READY_FOR_HUMAN_REVIEW":
      return "border-emerald-700/60 bg-emerald-950/40 text-emerald-100";
    case "DOCUMENT_PACK_INCOMPLETE":
    case "DATA_REVIEW_REQUIRED":
      return "border-sky-700/60 bg-sky-950/40 text-sky-100";
    case "REVIEW_REQUIRED":
    case "MAKER_REVIEW_REQUIRED":
      return "border-amber-700/60 bg-amber-950/40 text-amber-100";
    case "HIGH_RISK_ESCALATION":
      return "border-rose-700/60 bg-rose-950/40 text-rose-100";
    default:
      return "border-slate-600 bg-slate-900 text-slate-200";
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
        className={`inline-flex w-fit items-center rounded border px-2 py-0.5 text-xs font-medium ${toneClass(readinessRoute)}`}
      >
        {readinessLabel(readinessRoute)}
      </span>
      <span className="font-mono text-[11px] text-slate-400">
        Status code: {status}
      </span>
    </div>
  );
}
