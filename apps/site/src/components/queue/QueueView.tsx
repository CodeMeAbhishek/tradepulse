import { Link } from "@tanstack/react-router";
import type { QueueCase } from "@/lib/mock/types";
import { formatTimestamp } from "@/lib/mock/labels";
import { ProfileBadge } from "./ProfileBadge";
import { StatusRouteChip } from "./StatusRouteChip";
import { CompletenessSummary } from "./CompletenessSummary";

export function QueueTable({ cases }: { cases: QueueCase[] }) {
  if (cases.length === 0) {
    return (
      <p className="rounded border border-rule bg-paper/60 px-4 py-8 text-center text-sm text-slate">
        No cases in queue. Mock fixtures are empty.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded border border-rule">
      <table className="min-w-full border-collapse text-left text-sm">
        <caption className="sr-only">Compliance case queue</caption>
        <thead className="bg-paper text-xs uppercase tracking-wide text-slate">
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
            <tr key={row.id} className="border-t border-rule bg-paper hover:bg-bench/80">
              <td className="px-3 py-3 align-top">
                <Link
                  to="/workbench/cases/$caseId"
                  params={{ caseId: row.id }}
                  className="font-medium text-ink underline-offset-2 hover:underline"
                >
                  {row.reference}
                </Link>
                <p className="mt-1 max-w-[16rem] truncate text-slate" title={row.counterparty}>
                  {row.counterparty}
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-slate">
                  {row.corridor} · {row.dataSourceLabel}
                </p>
              </td>
              <td className="px-3 py-3 align-top">
                <ProfileBadge profile={row.profile} />
              </td>
              <td className="px-3 py-3 align-top">
                <StatusRouteChip status={row.status} readinessRoute={row.readinessRoute} />
              </td>
              <td className="px-3 py-3 align-top">
                <CompletenessSummary items={row.documentCompleteness} />
              </td>
              <td className="px-3 py-3 align-top whitespace-nowrap text-slate">
                {formatTimestamp(row.updatedAt)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
