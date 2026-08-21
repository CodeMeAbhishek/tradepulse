import { Link, createFileRoute, notFound } from "@tanstack/react-router";

import { BolReconciliationPanel } from "@/components/case/BolReconciliationPanel";
import { DocumentUploadPanel } from "@/components/case/DocumentUploadPanel";
import { FindingsWorkflowPanel } from "@/components/case/FindingsWorkflowPanel";
import { IdentityEvidenceDrawer } from "@/components/case/IdentityEvidenceDrawer";
import { InvoiceReviewPanel } from "@/components/case/InvoiceReviewPanel";
import { CompletenessSummary } from "@/components/queue/CompletenessSummary";
import { ProfileBadge } from "@/components/queue/ProfileBadge";
import { StatusRouteChip } from "@/components/queue/StatusRouteChip";
import { getCaseWorkbenchDetail } from "@/lib/mock/case-detail";
import { formatTimestamp } from "@/lib/mock/labels";
import { getMockQueueCase } from "@/lib/mock/queue";

/** Full case workbench, surfaces A2–A6 (fixture driven). */
function CasePage() {
  const { caseId } = Route.useParams();
  const caseRecord = getMockQueueCase(caseId);
  const detail = getCaseWorkbenchDetail(caseId);

  // Resolved in the loader, so this is a type narrowing rather than a branch
  // a user can reach.
  if (!caseRecord || !detail) return null;

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <p>
        <Link to="/workbench" className="text-sm text-sky-300 underline-offset-2 hover:underline">
          ← Back to compliance queue
        </Link>
      </p>

      <header className="flex flex-col gap-4 border-b border-slate-800 pb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Case workbench</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">
              {caseRecord.reference}
            </h1>
            <p className="mt-1 text-slate-300">{caseRecord.counterparty}</p>
            <p className="mt-1 font-mono text-xs text-slate-500">
              {caseRecord.corridor} · {caseRecord.dataSourceLabel} · Updated{" "}
              {formatTimestamp(caseRecord.updatedAt)}
            </p>
          </div>
          <div className="flex flex-col items-start gap-2 sm:items-end">
            <ProfileBadge profile={caseRecord.profile} />
            <StatusRouteChip
              status={caseRecord.status}
              readinessRoute={caseRecord.readinessRoute}
            />
          </div>
        </div>
        <section aria-labelledby="completeness-heading">
          <h2 id="completeness-heading" className="mb-2 text-sm font-medium text-slate-300">
            Document completeness summary
          </h2>
          <CompletenessSummary items={caseRecord.documentCompleteness} />
        </section>
      </header>

      <DocumentUploadPanel
        initialProfile={caseRecord.profile}
        initialFiles={detail.uploadedFiles}
      />
      <InvoiceReviewPanel fields={detail.invoiceFields} trace={detail.agentTrace} />
      <BolReconciliationPanel reconciliation={detail.reconciliation} />
      <IdentityEvidenceDrawer parties={detail.identities} />
      <FindingsWorkflowPanel
        findings={detail.findings}
        makerChecker={detail.makerChecker}
        audit={detail.audit}
      />

      <p className="text-sm text-slate-500">
        RegWatch source registry lives on the{" "}
        <Link to="/workbench/regwatch" className="text-sky-300 hover:underline">
          RegWatch
        </Link>{" "}
        page (A7).
      </p>
    </main>
  );
}

function CaseNotFound() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-16">
      <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Case workbench</p>
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50">
        No case filed under that reference
      </h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-400">
        This prototype serves a fixed set of synthetic demo cases. Pick one from the compliance
        queue.
      </p>
      <Link
        to="/workbench"
        className="mt-6 inline-block rounded border border-slate-600 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
      >
        ← Back to compliance queue
      </Link>
    </main>
  );
}

export const Route = createFileRoute("/workbench/cases/$caseId")({
  loader: ({ params }) => {
    // Fail before render rather than letting a bad id reach the panels.
    if (!getMockQueueCase(params.caseId) || !getCaseWorkbenchDetail(params.caseId)) {
      throw notFound();
    }
  },
  component: CasePage,
  notFoundComponent: CaseNotFound,
});
