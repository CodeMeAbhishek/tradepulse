"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api, dataMode } from "@/lib/api/client";
import {
  buildBolFixture,
  buildInvoiceFixture,
  FIXTURE_LEI,
  FIXTURE_SELLER,
} from "@/lib/api/fixtures";
import { recordToTradeCase, summaryToTradeCase } from "@/lib/api/map";
import {
  applyChecker,
  applyMaker,
  createCase as createLocalCase,
  loadCases,
  resetDemoData,
  saveCases,
  type Profile,
  type TradeCase,
} from "@/lib/demo/store";

type DemoContextValue = {
  mode: "api" | "demo";
  cases: TradeCase[];
  ready: boolean;
  error: string | null;
  apiOnline: boolean | null;
  refresh: () => Promise<void>;
  reset: () => Promise<void>;
  seedSamples: () => Promise<void>;
  create: (input: {
    counterparty: string;
    corridor: string;
    profile: Profile;
    includeBol: boolean;
    invoiceFile?: File | null;
    bolFile?: File | null;
  }) => Promise<TradeCase>;
  maker: (caseId: string, decision: "approve" | "investigate", note: string) => Promise<void>;
  checker: (caseId: string, decision: "approve" | "reject", note: string) => Promise<void>;
  loadCase: (id: string) => Promise<TradeCase | undefined>;
  get: (id: string) => TradeCase | undefined;
};

const DemoContext = createContext<DemoContextValue | null>(null);

async function hydrateFromApi(id: string): Promise<TradeCase> {
  const [record, audit, policy] = await Promise.all([
    api.getCase(id),
    api.audit(id).catch(() => []),
    api.policy(id).catch(() => undefined),
  ]);
  return recordToTradeCase(record, audit, policy);
}

export function DemoProvider({ children }: { children: React.ReactNode }) {
  const mode = dataMode();
  const [cases, setCases] = useState<TradeCase[]>([]);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    if (mode === "demo") {
      setCases(loadCases());
      setApiOnline(null);
      return;
    }
    try {
      const ok = await api.health();
      setApiOnline(ok);
      const list = await api.listCases();
      const mapped = await Promise.all(
        list.map(async (s) => {
          try {
            return await hydrateFromApi(s.case_id);
          } catch {
            return summaryToTradeCase(s);
          }
        }),
      );
      setCases(mapped);
    } catch (e) {
      setApiOnline(false);
      setError(e instanceof Error ? e.message : "API unavailable");
      setCases([]);
    }
  }, [mode]);

  useEffect(() => {
    void refresh().finally(() => setReady(true));
  }, [refresh]);

  const persistLocal = useCallback((next: TradeCase[]) => {
    setCases(next);
    saveCases(next);
  }, []);

  const loadCase = useCallback(
    async (id: string) => {
      if (mode === "demo") {
        return loadCases().find((c) => c.id === id);
      }
      const full = await hydrateFromApi(id);
      setCases((prev) => {
        const others = prev.filter((c) => c.id !== id);
        return [full, ...others];
      });
      return full;
    },
    [mode],
  );

  const value = useMemo<DemoContextValue>(
    () => ({
      mode,
      cases,
      ready,
      error,
      apiOnline,
      refresh,
      reset: async () => {
        if (mode === "demo") {
          persistLocal(resetDemoData());
          return;
        }
        await refresh();
      },
      seedSamples: async () => {
        if (mode !== "api") {
          persistLocal(resetDemoData());
          return;
        }
        // Prefer real library packs so the desk shows varied counterparties / corridors.
        // Fallback to two synthetic fixtures if the sample library is unavailable.
        const DESK_PACK_IDS = [
          "01-clean-match",
          "02-qty-mismatch",
          "04-name-only-review",
          "07-invoice-only",
          "08-public-lei-ready",
        ] as const;

        try {
          const packs = await api.listSamplePacks();
          const byId = new Map(packs.map((p) => [p.pack_id, p]));
          const chosen = DESK_PACK_IDS.map((id) => byId.get(id)).filter(
            (p): p is NonNullable<typeof p> => Boolean(p),
          );

          if (chosen.length > 0) {
            for (const pack of chosen) {
              const record = await api.createCase({
                transaction_profile: pack.default_profile,
                corridor: pack.suggested_corridor,
                assignee: pack.suggested_counterparty,
              });
              for (const f of pack.files) {
                const file = await api.fetchSampleFile(pack.pack_id, f.filename);
                await api.uploadDocument(
                  record.case_id,
                  file,
                  file.name,
                  f.role === "bill_of_lading" ? "bill_of_lading" : "commercial_invoice",
                );
              }
              await api.processCase(record.case_id);
            }
            await refresh();
            return;
          }
        } catch {
          // Fall through to fixture seed below.
        }

        const clean = await api.createCase({
          transaction_profile: "INVOICE_ONLY_PRE_REVIEW",
          corridor: "IN-AE",
          assignee: FIXTURE_SELLER,
        });
        await api.uploadDocument(
          clean.case_id,
          new Blob([buildInvoiceFixture({ seller: FIXTURE_SELLER, lei: FIXTURE_LEI })], {
            type: "text/plain",
          }),
          "invoice.txt",
          "commercial_invoice",
        );
        await api.processCase(clean.case_id);

        const mismatch = await api.createCase({
          transaction_profile: "POST_SHIPMENT_DOCUMENT_REVIEW",
          corridor: "IN-AE",
          assignee: FIXTURE_SELLER,
        });
        await api.uploadDocument(
          mismatch.case_id,
          new Blob(
            [
              buildInvoiceFixture({
                seller: FIXTURE_SELLER,
                lei: FIXTURE_LEI,
                quantity: 500,
                unit: "cartons",
                unitPrice: 1780.8,
                kgPerUnit: 200,
                invoiceNumber: "INV-SYN-2208",
              }),
            ],
            { type: "text/plain" },
          ),
          "commercial_invoice.txt",
          "commercial_invoice",
        );
        await api.uploadDocument(
          mismatch.case_id,
          new Blob(
            [
              buildBolFixture({
                shipper: FIXTURE_SELLER,
                quantity: 350,
                unit: "cartons",
                invoiceNumber: "INV-SYN-2208",
                blNumber: "BL-MISMATCH-01",
              }),
            ],
            { type: "text/plain" },
          ),
          "bill_of_lading.txt",
          "bill_of_lading",
        );
        await api.processCase(mismatch.case_id);
        await refresh();
      },
      create: async (input) => {
        if (mode === "demo") {
          const c = createLocalCase(input);
          persistLocal([c, ...cases]);
          return c;
        }
        const record = await api.createCase({
          transaction_profile: input.profile,
          corridor: input.corridor.replace(/\s+/g, ""),
          assignee: input.counterparty,
        });

        if (input.invoiceFile) {
          await api.uploadDocument(
            record.case_id,
            input.invoiceFile,
            input.invoiceFile.name,
            "commercial_invoice",
          );
        } else {
          await api.uploadDocument(
            record.case_id,
            new Blob(
              [
                buildInvoiceFixture({
                  seller: input.counterparty,
                  lei: FIXTURE_LEI,
                  quantity: 500,
                  unit: "MT",
                }),
              ],
              { type: "text/plain" },
            ),
            "invoice.txt",
            "commercial_invoice",
          );
        }

        const wantBol = input.includeBol || Boolean(input.bolFile);
        if (wantBol) {
          if (input.bolFile) {
            await api.uploadDocument(
              record.case_id,
              input.bolFile,
              input.bolFile.name,
              "bill_of_lading",
            );
          } else {
            await api.uploadDocument(
              record.case_id,
              new Blob(
                [
                  buildBolFixture({
                    shipper: input.counterparty,
                    quantity: 500,
                    unit: "MT",
                  }),
                ],
                { type: "text/plain" },
              ),
              "bol.txt",
              "bill_of_lading",
            );
          }
        }

        await api.processCase(record.case_id);
        const full = await hydrateFromApi(record.case_id);
        setCases((prev) => [full, ...prev.filter((x) => x.id !== full.id)]);
        return full;
      },
      maker: async (caseId, decision, note) => {
        if (mode === "demo") {
          persistLocal(applyMaker(cases, caseId, decision, note));
          return;
        }
        await api.caseAction(caseId, {
          action: decision === "approve" ? "maker_approve" : "maker_investigate",
          actor: "maker.demo",
          actor_role: "maker",
          note: note || undefined,
        });
        const full = await hydrateFromApi(caseId);
        setCases((prev) => prev.map((c) => (c.id === caseId ? full : c)));
      },
      checker: async (caseId, decision, note) => {
        if (mode === "demo") {
          persistLocal(applyChecker(cases, caseId, decision, note));
          return;
        }
        await api.caseAction(caseId, {
          action: decision === "approve" ? "checker_approve" : "checker_reject",
          actor: "checker.demo",
          actor_role: "checker",
          note: note || undefined,
        });
        const full = await hydrateFromApi(caseId);
        setCases((prev) => prev.map((c) => (c.id === caseId ? full : c)));
      },
      loadCase,
      get: (id) => cases.find((c) => c.id === id),
    }),
    [mode, cases, ready, error, apiOnline, refresh, persistLocal, loadCase],
  );

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
}

export function useDemo() {
  const ctx = useContext(DemoContext);
  if (!ctx) throw new Error("useDemo must be used within DemoProvider");
  return ctx;
}
