"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useDemo } from "@/lib/demo/DemoProvider";
import type { Profile } from "@/lib/demo/store";
import { profileLabel } from "@/lib/demo/store";

const PROFILES: Profile[] = [
  "INVOICE_ONLY_PRE_REVIEW",
  "POST_SHIPMENT_DOCUMENT_REVIEW",
  "LC_DOCUMENT_REVIEW",
  "ENHANCED_TRADE_HOUSE_REVIEW",
];

export default function NewCasePage() {
  const { create, mode } = useDemo();
  const router = useRouter();
  const [counterparty, setCounterparty] = useState("Amit Trading Co.");
  const [corridor, setCorridor] = useState("IN-AE");
  const [profile, setProfile] = useState<Profile>("POST_SHIPMENT_DOCUMENT_REVIEW");
  const [includeBol, setIncludeBol] = useState(true);
  const [mismatchQty, setMismatchQty] = useState(false);
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [bolFile, setBolFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const usingUploads = Boolean(invoiceFile || bolFile);

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div>
        <h1 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">New trade case</h1>
        <p className="mt-1 text-sm text-[var(--tp-muted)]">
          Build a documentary packet. Commercial invoice is required; Bill of Lading is needed for
          post-shipment reconciliation. TradePulse prepares evidence—you decide.
        </p>
      </div>

      <form
        className="tp-card space-y-4 p-5"
        onSubmit={(e) => {
          e.preventDefault();
          setBusy(true);
          setErr(null);
          void create({
            counterparty,
            corridor,
            profile,
            includeBol: includeBol || Boolean(bolFile),
            mismatchQty: usingUploads ? false : mismatchQty,
            invoiceFile,
            bolFile,
          })
            .then((c) => router.push(`/workbench/cases/${c.id}`))
            .catch((ex: unknown) => {
              setErr(ex instanceof Error ? ex.message : "Create failed");
            })
            .finally(() => setBusy(false));
        }}
      >
        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Counterparty</span>
          <input
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={counterparty}
            onChange={(e) => setCounterparty(e.target.value)}
            required
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Corridor</span>
          <input
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={corridor}
            onChange={(e) => setCorridor(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Transaction profile</span>
          <select
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={profile}
            onChange={(e) => setProfile(e.target.value as Profile)}
          >
            {PROFILES.map((p) => (
              <option key={p} value={p}>
                {profileLabel(p)}
              </option>
            ))}
          </select>
        </label>

        {mode === "api" ? (
          <fieldset className="space-y-3 rounded-lg border border-[var(--tp-line)] p-3">
            <legend className="px-1 text-sm font-medium text-[var(--tp-navy)]">
              Document upload
            </legend>
            <p className="text-xs text-[var(--tp-muted)]">
              Optional. Upload invoice and/or Bill of Lading (.txt or .pdf). Leave empty to use
              labeled demo fixtures. Extraction uses the configured document pipeline.
            </p>
            <label className="block text-sm">
              <span className="font-medium text-[var(--tp-navy)]">Commercial invoice</span>
              <input
                className="mt-1 block w-full text-sm"
                type="file"
                accept=".txt,.pdf,text/plain,application/pdf"
                onChange={(e) => setInvoiceFile(e.target.files?.[0] ?? null)}
              />
            </label>
            <label className="block text-sm">
              <span className="font-medium text-[var(--tp-navy)]">Bill of Lading</span>
              <input
                className="mt-1 block w-full text-sm"
                type="file"
                accept=".txt,.pdf,text/plain,application/pdf"
                onChange={(e) => setBolFile(e.target.files?.[0] ?? null)}
              />
            </label>
          </fieldset>
        ) : null}

        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            className="mt-1"
            checked={includeBol || Boolean(bolFile)}
            disabled={Boolean(bolFile)}
            onChange={(e) => setIncludeBol(e.target.checked)}
          />
          <span>
            <span className="font-medium text-[var(--tp-navy)]">Include Bill of Lading</span>
            <span className="mt-0.5 block text-[var(--tp-muted)]">
              Needed for post-shipment transport checks. Off for invoice-only — transport
              reconciliation shows as not available (not a pass).
            </span>
          </span>
        </label>
        {mode === "api" && !usingUploads ? (
          <label className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              className="mt-1"
              checked={mismatchQty}
              onChange={(e) => setMismatchQty(e.target.checked)}
            />
            <span>
              <span className="font-medium text-[var(--tp-navy)]">
                Seed quantity mismatch (500 vs 350)
              </span>
              <span className="mt-0.5 block text-[var(--tp-muted)]">
                Demo path that forces human review — not a fraud conclusion.
              </span>
            </span>
          </label>
        ) : null}
        {err ? <p className="text-sm text-rose-700">{err}</p> : null}
        <button type="submit" disabled={busy} className="tp-btn-primary disabled:opacity-50">
          {busy ? "Creating & processing…" : "Create case & open workbench"}
        </button>
      </form>
    </div>
  );
}
