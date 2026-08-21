import Link from "next/link";
import { notFound } from "next/navigation";
import { DocumentUploadPanel } from "@/components/case/DocumentUploadPanel";
import { InvoiceReviewPanel } from "@/components/case/InvoiceReviewPanel";
import { BolReconciliationPanel } from "@/components/case/BolReconciliationPanel";
import { IdentityEvidenceDrawer } from "@/components/case/IdentityEvidenceDrawer";
import { FindingsWorkflowPanel } from "@/components/case/FindingsWorkflowPanel";
import { CompletenessSummary } from "@/components/queue/CompletenessSummary";
import { ProfileBadge } from "@/components/queue/ProfileBadge";
import { StatusRouteChip } from "@/components/queue/StatusRouteChip";
import { getCaseWorkbenchDetail } from "@/lib/mock/case-detail";
import { getMockQueueCase } from "@/lib/mock/queue";
import { formatTimestamp } from "@/lib/mock/labels";

/**
 * Full case workbench surfaces A2–A6 (mock/fixture driven).
 */
export default async function CasePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const caseRecord = getMockQueueCase(id);
  const detail = getCaseWorkbenchDetail(id);

  if (!caseRecord || !detail) {
    notFound();
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <p>
        <Link
          href="/"
          className="text-sm text-sky-300 underline-offset-2 hover:underline"
        >
          ← Back to compliance queue
        </Link>
      </p>

      <header className="flex flex-col gap-4 border-b border-slate-800 pb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">
              Case workbench
            </p>
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
          <h2
            id="completeness-heading"
            className="mb-2 text-sm font-medium text-slate-300"
          >
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
        <Link href="/regwatch" className="text-sky-300 hover:underline">
          RegWatch
        </Link>{" "}
        page (A7).
      </p>
    </main>
  );
}
