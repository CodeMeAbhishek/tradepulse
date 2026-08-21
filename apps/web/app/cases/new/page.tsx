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
        <h1 className="text-2xl font-semibold text-[var(--tp-navy)]">New trade case</h1>
        <p className="mt-1 text-sm text-[var(--tp-muted)]">
          {mode === "api"
            ? "Creates a case on the API, uploads invoice/BoL (your files or synthetic fixtures), then runs process."
            : "Creates a local demo case (no API)."}
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
            .then((c) => router.push(`/cases/${c.id}`))
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
              Optional. Upload .txt or .pdf from{" "}
              <code className="text-[11px]">data/fixtures/synthetic-trade-docs/</code>. Leave empty
              to seed labeled fixtures. Extraction uses Bedrock when{" "}
              <code className="text-[11px]">LLM_PROVIDER=bedrock</code>.
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
              Required for post-shipment. Off on invoice-only → transport recon NOT_AVAILABLE.
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
                Demo climax path — review required, not a fraud conclusion.
              </span>
            </span>
          </label>
        ) : null}
        {err ? <p className="text-sm text-rose-700">{err}</p> : null}
        <button
          type="submit"
          disabled={busy}
          className="rounded-lg bg-[var(--tp-navy)] px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Creating & processing…" : "Create case & open workbench"}
        </button>
      </form>
    </div>
  );
}
