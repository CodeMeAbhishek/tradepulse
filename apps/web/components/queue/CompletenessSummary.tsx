import type { DocumentCompletenessItem } from "@/lib/mock/types";
import { documentStateLabel } from "@/lib/mock/labels";

export function CompletenessSummary({
  items,
}: {
  items: DocumentCompletenessItem[];
}) {
  return (
    <ul className="flex flex-col gap-0.5 text-xs text-slate-300">
      {items.map((item) => (
        <li key={item.documentType} className="flex flex-wrap gap-x-1">
          <span className="text-slate-400">{item.label}:</span>
          <span className="font-medium text-slate-100">
            {documentStateLabel(item.state)}
          </span>
        </li>
      ))}
    </ul>
  );
}
