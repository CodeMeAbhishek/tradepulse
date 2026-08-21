/**
 * Data hooks for the workbench.
 *
 * Every hook reports WHERE its data came from, because the product forbids
 * presenting fixture output as if it were live. `source` is not a debug field --
 * it drives visible labelling, and callers must render it.
 */

import { useQuery } from "@tanstack/react-query";

import { getMockQueueCases } from "@/lib/mock/queue";
import type { QueueCase } from "@/lib/mock/types";

import { api } from "./client";
import { toQueueCase } from "./adapters";

export type DataSource = "live" | "fixture";

export interface CasesResult {
  cases: QueueCase[];
  source: DataSource;
  /** Why we fell back, when we did. Shown to the user, not swallowed. */
  reason: string | null;
}

/**
 * Fixture fallback is deliberate: on a demo stage a backend that is down must
 * degrade to something honest and labelled, not to a blank screen. It is only
 * ever reached after a real attempt, and the UI must say which one it got.
 */
function fixtureFallback(reason: string): CasesResult {
  return { cases: getMockQueueCases(), source: "fixture", reason };
}

export function useCases() {
  return useQuery<CasesResult>({
    queryKey: ["cases"],
    queryFn: async () => {
      try {
        const summaries = await api.listCases();
        if (summaries.length === 0) {
          return fixtureFallback("The API is reachable but holds no cases yet.");
        }
        return {
          cases: summaries.map((s) => toQueueCase(s)),
          source: "live",
          reason: null,
        };
      } catch (error) {
        return fixtureFallback(
          error instanceof Error ? error.message : "The API could not be reached.",
        );
      }
    },
    // A compliance queue is not real-time; refetching on every focus would
    // churn the officer's screen mid-review.
    staleTime: 30_000,
    refetchOnWindowFocus: false,
    // Render fixtures on the server and first paint, then swap in live data.
    // Without this the page server-renders empty and flashes on hydration.
    placeholderData: {
      cases: getMockQueueCases(),
      source: "fixture",
      reason: "Contacting the TradePulse API…",
    },
  });
}

export interface HealthResult {
  online: boolean;
  version: string | null;
  message: string | null;
}

export function useApiHealth() {
  return useQuery<HealthResult>({
    queryKey: ["api-health"],
    queryFn: async () => {
      try {
        const health = await api.health();
        return { online: true, version: health.version, message: null };
      } catch (error) {
        return {
          online: false,
          version: null,
          message: error instanceof Error ? error.message : "API unreachable.",
        };
      }
    },
    staleTime: 15_000,
    refetchOnWindowFocus: false,
  });
}
