"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api/client";
import type { CaseSummary, ShipmentMode, TradeProfile } from "@/lib/api/types";
import { apiBaseUrl } from "@/lib/api/config";

const PROFILES: TradeProfile[] = [
  "PRE_SHIPMENT_TRADE_FINANCE",
  "LC_ISSUANCE_AMENDMENT",
  "POST_SHIPMENT_LC_PRESENTATION",
  "DOCUMENTARY_COLLECTION",
  "TRADE_CREDIT_FACTORING",
  "TRADE_HOUSE_COMPLIANCE_REVIEW",
];

const MODES: ShipmentMode[] = ["OCEAN", "AIR", "MULTIMODAL", "UNKNOWN"];

function formatWhen(iso: string): string {
  try {
    return new Intl.DateTimeFormat("en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "UTC",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

export function LiveQueue() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<TradeProfile>("POST_SHIPMENT_LC_PRESENTATION");
  const [shipmentMode, setShipmentMode] = useState<ShipmentMode>("OCEAN");
  const [corridor, setCorridor] = useState("IN-AE");
  const [creating, setCreating] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await api.listCases();
      setCases(list);
    } catch (e) {
      setError(
        e instanceof Error
          ? `${e.message} (API: ${apiBaseUrl()})`
          : "Failed to load cases",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function onCreate() {
    setCreating(true);
    setError(null);
    try {
      const created = await api.createCase({
        transaction_profile: profile,
        corridor: corridor || undefined,
        shipment_mode: shipmentMode,
      });
      await refresh();
      window.location.href = `/cases/${created.case_id}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    } finally {
      setCreating(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-6 flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
          Compliance queue
        </h1>
        <p className="max-w-2xl text-sm text-slate-400">
          Application-led Scrutiny → Maker → Checker cases from{" "}
          <code className="text-sky-300">{apiBaseUrl()}</code>. Decision support only — not
          Customs clearance or autonomous approval.
        </p>
      </div>

      <section className="mb-6 rounded border border-slate-700/80 bg-slate-950/40 p-4">
        <h2 className="text-sm font-medium text-slate-200">Create case</h2>
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <label className="text-xs text-slate-400">
            Profile
            <select
              className="mt-1 block rounded border border-slate-600 bg-slate-900 px-2 py-1.5 text-sm text-slate-100"
              value={profile}
              onChange={(e) => setProfile(e.target.value as TradeProfile)}
            >
              {PROFILES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-slate-400">
            Shipment mode
            <select
              className="mt-1 block rounded border border-slate-600 bg-slate-900 px-2 py-1.5 text-sm text-slate-100"
              value={shipmentMode}
              onChange={(e) => setShipmentMode(e.target.value as ShipmentMode)}
            >
              {MODES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-slate-400">
            Corridor
            <input
              className="mt-1 block rounded border border-slate-600 bg-slate-900 px-2 py-1.5 text-sm text-slate-100"
              value={corridor}
              onChange={(e) => setCorridor(e.target.value)}
            />
          </label>
          <button
            type="button"
            onClick={() => void onCreate()}
            disabled={creating}
            className="rounded bg-sky-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-sky-600 disabled:opacity-50"
          >
            {creating ? "Creating…" : "Create case"}
          </button>
          <button
            type="button"
            onClick={() => void refresh()}
            className="rounded border border-slate-600 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-900"
          >
            Refresh
          </button>
        </div>
      </section>

      {error ? (
        <p className="mb-4 rounded border border-rose-800/60 bg-rose-950/40 px-3 py-2 text-sm text-rose-100">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm text-slate-400">Loading cases…</p>
      ) : cases.length === 0 ? (
        <p className="rounded border border-slate-700 px-4 py-8 text-center text-sm text-slate-400">
          No cases yet. Create one above, then upload the trade-finance application and supporting
          documents.
        </p>
      ) : (
        <div className="overflow-x-auto rounded border border-slate-700/80">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-950 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-3 py-2.5">Case</th>
                <th className="px-3 py-2.5">Profile</th>
                <th className="px-3 py-2.5">State</th>
                <th className="px-3 py-2.5">Risk route</th>
                <th className="px-3 py-2.5">Docs</th>
                <th className="px-3 py-2.5">Updated (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.case_id} className="border-t border-slate-800 hover:bg-slate-900/60">
                  <td className="px-3 py-2.5">
                    <Link
                      href={`/cases/${c.case_id}`}
                      className="font-medium text-sky-300 hover:underline"
                    >
                      {c.case_id}
                    </Link>
                  </td>
                  <td className="px-3 py-2.5 text-slate-300">{c.transaction_profile}</td>
                  <td className="px-3 py-2.5 text-slate-200">{c.state}</td>
                  <td className="px-3 py-2.5 text-slate-400">{c.risk_route ?? "—"}</td>
                  <td className="px-3 py-2.5 text-slate-400">{c.document_count}</td>
                  <td className="px-3 py-2.5 text-slate-500">{formatWhen(c.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
