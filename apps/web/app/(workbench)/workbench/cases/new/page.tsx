"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import { useDemo } from "@/lib/demo/DemoProvider";
import type { Profile } from "@/lib/demo/store";
import { profileLabel } from "@/lib/demo/store";
import { cn } from "@/lib/cn";

const PROFILES: Profile[] = [
  "INVOICE_ONLY_PRE_REVIEW",
  "POST_SHIPMENT_DOCUMENT_REVIEW",
  "LC_DOCUMENT_REVIEW",
  "ENHANCED_TRADE_HOUSE_REVIEW",
];

type DocSource = "upload" | "library";

type SamplePack = {
  pack_id: string;
  title: string;
  summary: string;
  data_label: string;
  default_profile: string;
  include_bol: boolean;
  files: Array<{ role: string; filename: string; media_type: string }>;
};

export default function NewCasePage() {
  const { create, mode } = useDemo();
  const router = useRouter();
  const [counterparty, setCounterparty] = useState("Amit Trading Co.");
  const [corridor, setCorridor] = useState("IN-AE");
  const [profile, setProfile] = useState<Profile>("POST_SHIPMENT_DOCUMENT_REVIEW");
  const [includeBol, setIncludeBol] = useState(true);
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [bolFile, setBolFile] = useState<File | null>(null);
  const [docSource, setDocSource] = useState<DocSource>("library");
  const [packs, setPacks] = useState<SamplePack[]>([]);
  const [selectedPackId, setSelectedPackId] = useState<string | null>(null);
  const [packsError, setPacksError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (mode !== "api") return;
    let cancelled = false;
    void api
      .listSamplePacks()
      .then((list) => {
        if (cancelled) return;
        setPacks(list);
        if (list[0]) setSelectedPackId(list[0].pack_id);
      })
      .catch((ex: unknown) => {
        if (cancelled) return;
        setPacksError(ex instanceof Error ? ex.message : "Could not load sample library");
      });
    return () => {
      cancelled = true;
    };
  }, [mode]);

  const selectedPack = packs.find((p) => p.pack_id === selectedPackId) ?? null;

  useEffect(() => {
    if (!selectedPack || docSource !== "library") return;
    setProfile(selectedPack.default_profile as Profile);
    setIncludeBol(selectedPack.include_bol);
  }, [selectedPack, docSource]);

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">New trade case</h1>
        <p className="mt-1 text-sm text-[var(--tp-muted)]">
          Build a documentary packet. Commercial invoice is required; Bill of Lading is needed for
          post-shipment reconciliation. Pick a labeled sample from the cloud library or upload your
          own files.
        </p>
      </div>

      <form
        className="tp-card space-y-4 p-5"
        onSubmit={(e) => {
          e.preventDefault();
          setBusy(true);
          setErr(null);
          void (async () => {
            let inv = invoiceFile;
            let bol = bolFile;
            let useBol = includeBol || Boolean(bol);

            if (mode === "api" && docSource === "library") {
              if (!selectedPack) throw new Error("Select a sample pack from the library");
              inv = null;
              bol = null;
              for (const f of selectedPack.files) {
                const file = await api.fetchSampleFile(selectedPack.pack_id, f.filename);
                if (f.role === "commercial_invoice") inv = file;
                if (f.role === "bill_of_lading") bol = file;
              }
              if (!inv) throw new Error("Sample pack is missing a commercial invoice");
              useBol = selectedPack.include_bol || Boolean(bol);
            }

            const c = await create({
              counterparty,
              corridor,
              profile,
              includeBol: useBol,
              invoiceFile: inv,
              bolFile: bol,
            });
            router.push(`/workbench/cases/${c.id}`);
          })()
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
            <legend className="px-1 text-sm font-medium text-[var(--tp-navy)]">Documents</legend>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className={cn(
                  "cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-semibold transition",
                  docSource === "library"
                    ? "border-[var(--tp-brand-blue)] bg-[var(--tp-brand-blue)] text-white"
                    : "border-[var(--tp-line)] bg-[var(--tp-elevated)] text-[var(--tp-navy)]",
                )}
                onClick={() => setDocSource("library")}
              >
                Sample library (cloud)
              </button>
              <button
                type="button"
                className={cn(
                  "cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-semibold transition",
                  docSource === "upload"
                    ? "border-[var(--tp-brand-blue)] bg-[var(--tp-brand-blue)] text-white"
                    : "border-[var(--tp-line)] bg-[var(--tp-elevated)] text-[var(--tp-navy)]",
                )}
                onClick={() => setDocSource("upload")}
              >
                Upload files
              </button>
            </div>

            {docSource === "library" ? (
              <div className="space-y-2">
                <p className="text-xs text-[var(--tp-muted)]">
                  SYNTHETIC_DEMO packs hosted with the API (same idea as a Canva project library).
                  Jury can pick a scenario without local files.
                </p>
                {packsError ? <p className="text-xs text-rose-700">{packsError}</p> : null}
                <div className="grid gap-2 sm:grid-cols-2">
                  {packs.map((p) => {
                    const active = p.pack_id === selectedPackId;
                    return (
                      <button
                        key={p.pack_id}
                        type="button"
                        onClick={() => setSelectedPackId(p.pack_id)}
                        className={cn(
                          "cursor-pointer rounded-lg border p-3 text-left transition",
                          active
                            ? "border-[var(--tp-brand-orange)] bg-[rgba(233,99,29,0.06)] ring-1 ring-[var(--tp-brand-orange)]"
                            : "border-[var(--tp-line)] bg-[var(--tp-elevated)] hover:border-[var(--tp-brand-blue)]",
                        )}
                      >
                        <span className="block text-sm font-semibold text-[var(--tp-navy)]">
                          {p.title}
                        </span>
                        <span className="mt-1 block text-[11px] font-semibold uppercase tracking-wide text-[var(--tp-brand-orange)]">
                          {p.data_label}
                        </span>
                        <span className="mt-1 block text-xs leading-snug text-[var(--tp-muted)]">
                          {p.summary}
                        </span>
                      </button>
                    );
                  })}
                </div>
                {!packs.length && !packsError ? (
                  <p className="text-xs text-[var(--tp-muted)]">Loading sample packs…</p>
                ) : null}
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-xs text-[var(--tp-muted)]">
                  Upload invoice and/or Bill of Lading (.txt or .pdf). Extraction uses the configured
                  document pipeline.
                </p>
                <label className="block text-sm">
                  <span className="font-medium text-[var(--tp-navy)]">Commercial invoice</span>
                  <input
                    className="mt-1 block w-full cursor-pointer text-sm"
                    type="file"
                    accept=".txt,.pdf,text/plain,application/pdf"
                    onChange={(e) => setInvoiceFile(e.target.files?.[0] ?? null)}
                  />
                </label>
                <label className="block text-sm">
                  <span className="font-medium text-[var(--tp-navy)]">Bill of Lading</span>
                  <input
                    className="mt-1 block w-full cursor-pointer text-sm"
                    type="file"
                    accept=".txt,.pdf,text/plain,application/pdf"
                    onChange={(e) => setBolFile(e.target.files?.[0] ?? null)}
                  />
                </label>
              </div>
            )}
          </fieldset>
        ) : null}

        {docSource === "upload" || mode !== "api" ? (
          <label className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              className="mt-1 cursor-pointer"
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
        ) : null}

        {err ? <p className="text-sm text-rose-700">{err}</p> : null}
        <button type="submit" disabled={busy} className="tp-btn-primary disabled:opacity-50">
          {busy ? "Creating & processing…" : "Create case & open workbench"}
        </button>
      </form>
    </div>
  );
}
