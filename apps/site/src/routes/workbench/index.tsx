import { createFileRoute } from "@tanstack/react-router";

import { DataSourceStrip } from "@/components/workbench/DataSourceStrip";
import { QueueTable } from "@/components/queue/QueueView";
import { useCases } from "@/lib/api/useCases";

/**
 * Compliance queue (A1).
 *
 * Reads from the TradePulse API and falls back to synthetic fixtures when the
 * API cannot be reached -- always saying which one is on screen. A demo must
 * never die on a blank list, and must never pass fixtures off as live results.
 */
function QueuePage() {
  const { data, isFetching } = useCases();
  const cases = data?.cases ?? [];

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">Compliance queue</h1>
        <p className="max-w-2xl text-sm text-slate">
          Review documentary trade cases routed for human decision support. Status and readiness
          labels come from the case record — this screen does not approve, reject, or clear
          transactions.
        </p>
      </div>

      <div className="mb-4 overflow-hidden rounded border border-rule">
        <DataSourceStrip
          source={data?.source ?? "fixture"}
          reason={data?.reason ?? null}
          loading={isFetching}
        />
      </div>

      {cases.length > 0 ? (
        <QueueTable cases={cases} />
      ) : (
        <p className="rounded border border-rule bg-paper px-4 py-6 text-sm text-slate">
          No cases to review. Create one through the API to see it here.
        </p>
      )}
    </main>
  );
}

export const Route = createFileRoute("/workbench/")({
  component: QueuePage,
});
