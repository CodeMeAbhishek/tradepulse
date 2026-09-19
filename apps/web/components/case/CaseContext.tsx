"use client";

import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import type { TradeCase } from "@/lib/demo/store";
import type { IdentityLadderModel } from "@/components/case/IdentityLadder";

export type CaseContextValue = {
  /** The loaded trade case (undefined while loading). */
  live: TradeCase | undefined;
  /** Current API mode. */
  mode: "api" | "demo";
  /** Whether the case is currently being processed. */
  busy: boolean;
  /** Error message from the last action, if any. */
  err: string | null;
  /** Identity ladder model (loaded async in API mode). */
  ladder: IdentityLadderModel | null;
  /** Maker action: approve or escalate. */
  maker: (caseId: string, decision: "approve" | "investigate", note: string) => Promise<void>;
  /** Checker action: approve or reject. */
  checker: (caseId: string, decision: "approve" | "reject", note: string) => Promise<void>;
  /** Run an async action with busy/error state management. */
  run: (fn: () => Promise<void>) => void;
};

const CaseContext = createContext<CaseContextValue | null>(null);

export function CaseProvider({
  value,
  children,
}: {
  value: CaseContextValue;
  children: ReactNode;
}) {
  return <CaseContext.Provider value={value}>{children}</CaseContext.Provider>;
}

export function useCase() {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error("useCase must be used within CaseProvider");
  return ctx;
}
