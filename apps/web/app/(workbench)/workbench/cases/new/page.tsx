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
  suggested_counterparty: string;
  suggested_corridor: string;
  files: Array<{ role: string; filename: string; media_type: string }>;
};

type PreviewState = {
  packTitle: string;
  roleLabel: string;
  filename: string;
  mediaType: string;
  text: string | null;
  objectUrl: string | null;
};

function fileForRole(pack: SamplePack, role: string) {
  return pack.files.find((f) => f.role === role) ?? null;
}

export default function NewCasePage() {
  const { create, mode } = useDemo();
  const router = useRouter();
  const [counterparty, setCounterparty] = useState("");
  const [corridor, setCorridor] = useState("");
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
  const [preview, setPreview] = useState<PreviewState | null>(null);
  const [previewBusy, setPreviewBusy] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    if (mode !== "api") {
      setCounterparty("Amit Trading Co.");
      setCorridor("IN-AE");
      return;
    }
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

  useEffect(() => {
    return () => {
      if (preview?.objectUrl) URL.revokeObjectURL(preview.objectUrl);
    };
  }, [preview?.objectUrl]);

  const selectedPack = packs.find((p) => p.pack_id === selectedPackId) ?? null;

  useEffect(() => {
    if (!selectedPack || docSource !== "library") return;
    setCounterparty(selectedPack.suggested_counterparty);
    setCorridor(selectedPack.suggested_corridor);
    setProfile(selectedPack.default_profile as Profile);
    setIncludeBol(selectedPack.include_bol);
  }, [selectedPack, docSource]);

  const closePreview = () => {
    setPreview((prev) => {
      if (prev?.objectUrl) URL.revokeObjectURL(prev.objectUrl);
      return null;
    });
    setPreviewError(null);
  };

  const openSampleDoc = async (pack: SamplePack, role: "commercial_invoice" | "bill_of_lading") => {
    const meta = fileForRole(pack, role);
    if (!meta) {
      setPreviewError(role === "commercial_invoice" ? "No invoice in this packet." : "No Bill of Lading in this packet.");
      return;
    }
    const key = `${pack.pack_id}:${meta.filename}`;
    setPreviewBusy(key);
    setPreviewError(null);
    try {
      const file = await api.fetchSampleFile(pack.pack_id, meta.filename);
      const isPdf =
        meta.media_type.includes("pdf") ||
        meta.filename.toLowerCase().endsWith(".pdf") ||
        file.type.includes("pdf");
      if (isPdf) {
        const objectUrl = URL.createObjectURL(file);
        setPreview({
          packTitle: pack.title,
          roleLabel: role === "commercial_invoice" ? "Commercial invoice" : "Bill of Lading",
          filename: meta.filename,
          mediaType: "application/pdf",
          text: null,
          objectUrl,
        });
      } else {
        const text = await file.text();
        setPreview({
          packTitle: pack.title,
          roleLabel: role === "commercial_invoice" ? "Commercial invoice" : "Bill of Lading",
          filename: meta.filename,
          mediaType: meta.media_type || "text/plain",
          text,
          objectUrl: null,
        });
      }
    } catch (ex: unknown) {
      setPreviewError(ex instanceof Error ? ex.message : "Could not open sample document");
    } finally {
      setPreviewBusy(null);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h1 className="font-display text-3xl font-semibold text-[var(--tp-navy)]">New trade case</h1>
        <p className="mt-1 text-sm text-[var(--tp-muted)]">
          Assemble the documentary packet. A commercial invoice is required; a Bill of Lading is
          needed when you are reviewing after shipment. Choose a labelled demo packet or upload your
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
              if (!selectedPack) throw new Error("Select a demo packet from the library");
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
                Sample library
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
                Upload documents
              </button>
            </div>

            {docSource === "library" ? (
              <div className="space-y-2">
                <p className="text-xs text-[var(--tp-muted)]">
                  Pick a demo packet — counterparty, corridor, and profile update from that packet’s
                  documents. Use View invoice to inspect the source file before creating the case.
                </p>
                {packsError ? <p className="text-xs text-rose-700">{packsError}</p> : null}
                {previewError ? <p className="text-xs text-rose-700">{previewError}</p> : null}
                <div className="grid gap-2 sm:grid-cols-2">
                  {packs.map((p) => {
                    const active = p.pack_id === selectedPackId;
                    const inv = fileForRole(p, "commercial_invoice");
                    const bol = fileForRole(p, "bill_of_lading");
                    const invKey = inv ? `${p.pack_id}:${inv.filename}` : "";
                    const bolKey = bol ? `${p.pack_id}:${bol.filename}` : "";
                    return (
                      <div
                        key={p.pack_id}
                        className={cn(
                          "rounded-lg border p-3 text-left transition",
                          active
                            ? "border-[var(--tp-brand-orange)] bg-[rgba(233,99,29,0.06)] ring-1 ring-[var(--tp-brand-orange)]"
                            : "border-[var(--tp-line)] bg-[var(--tp-elevated)] hover:border-[var(--tp-brand-blue)]",
                        )}
                      >
                        <button
                          type="button"
                          onClick={() => setSelectedPackId(p.pack_id)}
                          className="w-full cursor-pointer text-left"
                        >
                          <span className="block text-sm font-semibold text-[var(--tp-navy)]">
                            {p.title}
                          </span>
                          <span className="mt-1 block text-[11px] font-semibold uppercase tracking-wide text-[var(--tp-brand-orange)]">
                            Demo sample
                          </span>
                          <span className="mt-1 block font-mono text-[11px] text-[var(--tp-navy)]">
                            {p.suggested_counterparty} · {p.suggested_corridor}
                          </span>
                          <span className="mt-1 block text-xs leading-snug text-[var(--tp-muted)]">
                            {p.summary}
                          </span>
                        </button>
                        <div className="mt-3 flex flex-wrap gap-2 border-t border-[var(--tp-line)] pt-2">
                          {inv ? (
                            <button
                              type="button"
                              className="cursor-pointer rounded-md border border-[var(--tp-line)] bg-white px-2.5 py-1 text-xs font-semibold text-[var(--tp-brand-blue)] hover:border-[var(--tp-brand-blue)] disabled:opacity-50"
                              disabled={previewBusy === invKey}
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedPackId(p.pack_id);
                                void openSampleDoc(p, "commercial_invoice");
                              }}
                            >
                              {previewBusy === invKey ? "Opening…" : "View invoice"}
                            </button>
                          ) : null}
                          {bol ? (
                            <button
                              type="button"
                              className="cursor-pointer rounded-md border border-[var(--tp-line)] bg-white px-2.5 py-1 text-xs font-semibold text-[var(--tp-navy)] hover:border-[var(--tp-brand-blue)] disabled:opacity-50"
                              disabled={previewBusy === bolKey}
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedPackId(p.pack_id);
                                void openSampleDoc(p, "bill_of_lading");
                              }}
                            >
                              {previewBusy === bolKey ? "Opening…" : "View BoL"}
                            </button>
                          ) : null}
                        </div>
                      </div>
                    );
                  })}
                </div>
                {!packs.length && !packsError ? (
                  <p className="text-xs text-[var(--tp-muted)]">Loading demo packets…</p>
                ) : null}
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-xs text-[var(--tp-muted)]">
                  Upload a commercial invoice and, if needed, a Bill of Lading (.txt or .pdf).
                  TradePulse will extract fields for your review.
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

        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Counterparty</span>
          <input
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={counterparty}
            onChange={(e) => setCounterparty(e.target.value)}
            readOnly={mode === "api" && docSource === "library"}
            required
          />
          {mode === "api" && docSource === "library" ? (
            <span className="mt-1 block text-xs text-[var(--tp-muted)]">
              Taken from the selected demo packet (matches the invoice seller).
            </span>
          ) : null}
        </label>
        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Corridor</span>
          <input
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={corridor}
            onChange={(e) => setCorridor(e.target.value)}
            readOnly={mode === "api" && docSource === "library"}
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-[var(--tp-navy)]">Transaction profile</span>
          <select
            className="mt-1 w-full rounded-lg border border-[var(--tp-line)] px-3 py-2"
            value={profile}
            onChange={(e) => setProfile(e.target.value as Profile)}
            disabled={mode === "api" && docSource === "library"}
          >
            {PROFILES.map((p) => (
              <option key={p} value={p}>
                {profileLabel(p)}
              </option>
            ))}
          </select>
        </label>

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
                Needed for post-shipment transport checks. Turn off for invoice-only review —
                transport comparison then shows as not available (that is not a pass).
              </span>
            </span>
          </label>
        ) : null}

        {err ? <p className="text-sm text-rose-700">{err}</p> : null}
        <button type="submit" disabled={busy} className="tp-btn-primary disabled:opacity-50">
          {busy ? "Preparing case for review…" : "Create case & open for review"}
        </button>
      </form>

      {preview ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="sample-preview-title"
          onClick={closePreview}
        >
          <div
            className="flex max-h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-[var(--tp-line)] bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-3 border-b border-[var(--tp-line)] px-4 py-3">
              <div>
                <p
                  id="sample-preview-title"
                  className="text-sm font-semibold text-[var(--tp-navy)]"
                >
                  {preview.roleLabel}
                </p>
                <p className="mt-0.5 text-xs text-[var(--tp-muted)]">
                  {preview.packTitle} · {preview.filename} · Demo sample
                </p>
              </div>
              <button
                type="button"
                className="cursor-pointer rounded-md px-2 py-1 text-sm font-medium text-[var(--tp-muted)] hover:bg-[var(--tp-bg)] hover:text-[var(--tp-navy)]"
                onClick={closePreview}
              >
                Close
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-auto bg-[var(--tp-bg)] p-4">
              {preview.objectUrl ? (
                <iframe
                  title={preview.filename}
                  src={preview.objectUrl}
                  className="h-[65vh] w-full rounded-lg border border-[var(--tp-line)] bg-white"
                />
              ) : (
                <pre className="whitespace-pre-wrap rounded-lg border border-[var(--tp-line)] bg-white p-4 font-mono text-xs leading-relaxed text-[var(--tp-ink)]">
                  {preview.text}
                </pre>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
