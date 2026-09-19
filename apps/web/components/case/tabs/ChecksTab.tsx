"use client";

import { useState } from "react";
import { ToneChip } from "@/components/ui/StatusChips";
import type { Finding } from "@/lib/demo/store";
import { parseLegacySourceString } from "@/lib/sources/resolve";

export function ChecksTab({
  findings,
  showEvidence,
  setShowEvidence,
}: {
  findings: Finding[];
  showEvidence: Record<string, boolean>;
  setShowEvidence: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}) {
  if (findings.length === 0) {
    return (
      <p className="text-sm text-[var(--tp-muted)] md:col-span-3">
        No checks yet. Process the case after uploading documents.
      </p>
    );
  }

  return (
    <section className="grid gap-3 md:grid-cols-3">
      {findings.map((f: Finding, i) => (
        <article
          key={f.id}
          className="tp-card tp-reveal flex flex-col p-4"
          style={{ "--i": i } as React.CSSProperties}
        >
          <div className="flex items-start justify-between gap-2">
            <h2 className="text-sm font-semibold text-[var(--tp-navy)]">{f.title}</h2>
            <ToneChip tone={f.tone} label={f.statusLabel} />
          </div>
          <p className="mt-2 flex-1 text-sm leading-relaxed text-[var(--tp-ink)]">{f.summary}</p>
          <p className="mt-3 text-sm font-medium text-[var(--tp-teal)]">Next: {f.action}</p>
          <button
            type="button"
            className="mt-3 self-start cursor-pointer text-xs font-medium text-[var(--tp-muted)] underline-offset-2 hover:underline"
            onClick={() =>
              setShowEvidence((prev) => ({ ...prev, [f.id]: !prev[f.id] }))
            }
          >
            {showEvidence[f.id] ? "Hide evidence source" : "Show evidence source"}
          </button>
          {showEvidence[f.id] ? (
            <div className="mt-2 space-y-1.5">
              {(f.sources && f.sources.length > 0
                ? f.sources
                : parseLegacySourceString(f.source)
              ).map((src) => (
                <div key={src.label} className="rounded-md bg-[var(--tp-bg)] px-2.5 py-2">
                  {src.platform ? (
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--tp-muted)]">
                      {src.platform}
                      {src.url ? " · open to verify" : " · no public URL"}
                    </p>
                  ) : null}
                  {src.url ? (
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-0.5 inline-block cursor-pointer font-mono text-[11px] font-medium text-[var(--tp-brand-blue)] underline-offset-2 hover:underline"
                    >
                      {src.label}
                    </a>
                  ) : (
                    <p className="mt-0.5 font-mono text-[11px] text-[var(--tp-muted)]">
                      {src.label}
                    </p>
                  )}
                </div>
              ))}
            </div>
          ) : null}
        </article>
      ))}
    </section>
  );
}
