import { useState } from "react";
import type { IdentityParty } from "@/lib/mock/types";
import { formatTimestamp, identityOutcomeLabel, vleiStatusLabel } from "@/lib/mock/labels";

export function IdentityEvidenceDrawer({ parties }: { parties: IdentityParty[] }) {
  const [openId, setOpenId] = useState<string | null>(parties[0]?.role ?? null);

  return (
    <section className="rounded border border-rule bg-paper p-4" aria-labelledby="identity-heading">
      <h2 id="identity-heading" className="text-lg font-semibold text-ink">
        Identity evidence
      </h2>
      <p className="mt-1 text-sm text-slate">
        LEI and VLEI are separate. Fuzzy name candidates are never shown as verified identity. A
        plain LEI string is not a VLEI.
      </p>

      <ul className="mt-4 space-y-2">
        {parties.map((party) => {
          const open = openId === party.role;
          return (
            <li key={party.role} className="rounded border border-rule">
              <button
                type="button"
                className="flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left"
                onClick={() => setOpenId(open ? null : party.role)}
                aria-expanded={open}
              >
                <span className="text-sm font-medium text-ink">
                  {party.role}: {party.normalizedName}
                </span>
                <span className="text-xs text-ink">
                  {identityOutcomeLabel(party.identityOutcome)}
                </span>
              </button>
              {open ? (
                <div className="border-t border-rule px-3 py-3 text-sm text-slate">
                  <dl className="grid gap-2 sm:grid-cols-2">
                    <div>
                      <dt className="text-xs text-slate">Raw document name</dt>
                      <dd>{party.rawName}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate">Normalized name</dt>
                      <dd>{party.normalizedName}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate">Document LEI</dt>
                      <dd className="font-mono text-xs">{party.lei ?? "Not on document"}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate">LEI status</dt>
                      <dd>{party.leiStatus}</dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate">VLEI status</dt>
                      <dd>
                        {vleiStatusLabel(party.vleiStatus)} — {party.vleiLabel}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs text-slate">Source / snapshot</dt>
                      <dd className="text-xs">
                        {party.source}
                        {party.snapshotId ? ` · ${party.snapshotId}` : ""}
                        {party.retrievedAt
                          ? ` · ${formatTimestamp(party.retrievedAt)}`
                          : " · no retrieval timestamp"}
                      </dd>
                    </div>
                  </dl>

                  <h3 className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate">
                    GLEIF candidate(s)
                  </h3>
                  {party.gleifCandidates.length === 0 ? (
                    <p className="mt-1 text-slate">No candidates in fixture.</p>
                  ) : (
                    <ul className="mt-2 space-y-2">
                      {party.gleifCandidates.map((c) => (
                        <li
                          key={c.lei}
                          className="rounded border border-rule bg-bench/60 px-2 py-2"
                        >
                          <p className="font-mono text-xs text-ink">{c.lei}</p>
                          <p>{c.legalName}</p>
                          <p className="text-xs text-slate">
                            {c.similarityNote}
                            {c.isExactDocumentMatch
                              ? " · Exact document LEI match"
                              : " · Candidate only — not verified identity"}
                          </p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : null}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
