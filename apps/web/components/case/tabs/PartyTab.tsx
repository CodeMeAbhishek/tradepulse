"use client";

import {
  IdentityLadder,
} from "@/components/case/IdentityLadder";
import { useCase } from "@/components/case/CaseContext";

export function PartyTab() {
  const { live, ladder } = useCase();
  if (!live) return null;
  const identity = live.identity;

  return (
    <section className="space-y-4">
      {ladder ? <IdentityLadder ladder={ladder} /> : null}
      <div className="tp-card grid gap-6 p-5 md:grid-cols-2">
        <div>
          <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Document party</h2>
          <dl className="mt-3 space-y-3 text-sm">
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                Name on document
              </dt>
              <dd className="mt-0.5 font-medium">{identity.rawName}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                LEI on document
              </dt>
              <dd className="mt-0.5 font-mono text-xs">
                {identity.leiOnDocument ?? "Not provided"}
              </dd>
              <p className="mt-1 text-xs leading-relaxed text-[var(--tp-muted)]">
                LEI is a 20-character Legal Entity Identifier. When the invoice LEI matches a
                GLEIF registry record, that is strong identity evidence — not a sanctions clear.
              </p>
            </div>
            {identity.candidateName ? (
              <div>
                <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                  Registry legal name
                </dt>
                <dd className="mt-0.5">{identity.candidateName}</dd>
              </div>
            ) : null}
          </dl>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Identity outcome</h2>
          <dl className="mt-3 space-y-3 text-sm">
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">Status</dt>
              <dd className="mt-0.5 text-base font-semibold text-[var(--tp-navy)]">
                {identity.outcome}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">
                What this means
              </dt>
              <dd className="mt-0.5 leading-relaxed">{identity.action}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-[var(--tp-muted)]">vLEI</dt>
              <dd className="mt-0.5 text-[var(--tp-muted)]">{identity.vlei}</dd>
              <p className="mt-1 text-xs leading-relaxed text-[var(--tp-muted)]">
                vLEI is a verifiable credential for role/authority. A plain LEI string is not a
                vLEI. Fixture demos must stay labeled synthetic.
              </p>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}
