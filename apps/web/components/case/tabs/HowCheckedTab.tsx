"use client";

import { useCase } from "@/components/case/CaseContext";

function agentStepTitle(agent: string): string {
  const key = agent.trim().toLowerCase();
  if (key.includes("extract")) return "Document extraction";
  if (key.includes("valid")) return "Independent field check";
  if (key.includes("challeng")) return "Exception review";
  if (key.includes("arbit")) return "Settled values";
  if (key.includes("reconcil") || key.includes("cross")) return "Cross-document check";
  return agent;
}

function agentStatusLabel(status: string): string {
  const key = status.trim().toUpperCase();
  if (key === "COMPLETE" || key === "DONE") return "Done";
  if (key === "REVIEW_REQUIRED") return "Needs officer review";
  if (key === "QUEUED") return "Queued";
  return status.replaceAll("_", " ");
}

export function HowCheckedTab() {
  const { live } = useCase();
  if (!live) return null;

  return (
    <section className="tp-card p-5">
      <h2 className="text-sm font-semibold text-[var(--tp-navy)]">How we checked the documents</h2>
      <p className="mb-4 mt-1 text-sm text-[var(--tp-muted)]">
        Up to three review passes. You see short findings only — not private model reasoning.
        Agreement between steps is never a compliance approval.
      </p>
      <ol className="space-y-3">
        {live.agentTrace.map((step, idx) => (
          <li
            key={`${step.agent}-${idx}`}
            className="rounded-lg border border-[var(--tp-line)] bg-slate-50 px-3 py-2.5"
          >
            <div className="flex justify-between gap-2">
              <span className="text-sm font-semibold text-[var(--tp-navy)]">
                {agentStepTitle(step.agent)}
              </span>
              <span className="text-[11px] font-medium uppercase tracking-wide text-[var(--tp-muted)]">
                {agentStatusLabel(step.status)}
              </span>
            </div>
            <p className="mt-1 text-sm leading-relaxed">{step.summary}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
