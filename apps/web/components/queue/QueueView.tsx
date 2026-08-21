import Link from "next/link";
import type { QueueCase } from "@/lib/mock/types";
import { formatTimestamp } from "@/lib/mock/labels";
import { ProfileBadge } from "./ProfileBadge";
import { StatusRouteChip } from "./StatusRouteChip";
import { CompletenessSummary } from "./CompletenessSummary";

export function QueueTable({ cases }: { cases: QueueCase[] }) {
  if (cases.length === 0) {
    return (
      <p className="rounded-lg border border-[var(--tp-line)] bg-white px-4 py-8 text-center text-sm text-[var(--tp-muted)]">
        No cases in queue.
      </p>
    );
  }

  return (
    <div className="tp-card overflow-x-auto">
      <table className="min-w-full border-collapse text-left text-sm">
        <caption className="sr-only">Compliance case queue</caption>
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-[var(--tp-muted)]">
          <tr>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Case
            </th>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Profile
            </th>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Status / risk route
            </th>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Document completeness
            </th>
            <th scope="col" className="px-3 py-2.5 font-medium">
              Updated (UTC)
            </th>
          </tr>
        </thead>
        <tbody>
          {cases.map((row) => (
            <tr
              key={row.id}
              className="border-t border-[var(--tp-line)] bg-white hover:bg-slate-50"
            >
              <td className="px-3 py-3 align-top">
                <Link
                  href={`/workbench/cases/${row.id}`}
                  className="font-medium text-[var(--tp-accent)] underline-offset-2 hover:underline"
                >
                  {row.reference}
                </Link>
                <p className="mt-1 max-w-[16rem] truncate text-[var(--tp-ink)]" title={row.counterparty}>
                  {row.counterparty}
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-[var(--tp-muted)]">
                  {row.corridor} · {row.dataSourceLabel}
                </p>
              </td>
              <td className="px-3 py-3 align-top">
                <ProfileBadge profile={row.profile} />
              </td>
              <td className="px-3 py-3 align-top">
                <StatusRouteChip
                  status={row.status}
                  readinessRoute={row.readinessRoute}
                />
              </td>
              <td className="px-3 py-3 align-top">
                <CompletenessSummary items={row.documentCompleteness} />
              </td>
              <td className="px-3 py-3 align-top whitespace-nowrap text-[var(--tp-muted)]">
                {formatTimestamp(row.updatedAt)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
