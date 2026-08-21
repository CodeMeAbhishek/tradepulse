import { createFileRoute } from "@tanstack/react-router";

import { QueueTable } from "@/components/queue/QueueView";
import { getMockQueueCases } from "@/lib/mock/queue";

/** Compliance queue — bank / trade-house case intake surface (A1). */
function QueuePage() {
  const cases = getMockQueueCases();

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-50">Compliance queue</h1>
        <p className="max-w-2xl text-sm text-slate-400">
          Review documentary trade cases routed for human decision support. Status and readiness
          labels come from the case record — this screen does not approve, reject, or clear
          transactions.
        </p>
      </div>
      <QueueTable cases={cases} />
    </main>
  );
}

export const Route = createFileRoute("/workbench/")({
  component: QueuePage,
});
