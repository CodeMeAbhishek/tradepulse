import Link from "next/link";
import type { QueueCase } from "@/lib/mock/types";
import { formatTimestamp } from "@/lib/mock/labels";
import { ProfileBadge } from "./ProfileBadge";
import { StatusRouteChip } from "./StatusRouteChip";
import { CompletenessSummary } from "./CompletenessSummary";

export function QueueTable({ cases }: { cases: QueueCase[] }) {
  if (cases.length === 0) {
    return (
      <p className="rounded border border-slate-700 bg-slate-950/60 px-4 py-8 text-center text-sm text-slate-400">
        No cases in queue. Mock fixtures are empty.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded border border-slate-700/80">
      <table className="min-w-full border-collapse text-left text-sm">
        <caption className="sr-only">Compliance case queue</caption>
        <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-400">
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
              className="border-t border-slate-800 bg-slate-900/40 hover:bg-slate-900/80"
            >
              <td className="px-3 py-3 align-top">
                <Link
                  href={`/cases/${row.id}`}
                  className="font-medium text-sky-300 underline-offset-2 hover:underline"
                >
                  {row.reference}
                </Link>
                <p className="mt-1 max-w-[16rem] truncate text-slate-200" title={row.counterparty}>
                  {row.counterparty}
                </p>
                <p className="mt-0.5 font-mono text-[11px] text-slate-500">
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
              <td className="px-3 py-3 align-top whitespace-nowrap text-slate-400">
                {formatTimestamp(row.updatedAt)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
