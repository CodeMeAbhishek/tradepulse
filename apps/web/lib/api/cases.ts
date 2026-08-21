import type { QueueCaseRow } from "@/lib/contracts/mirror";
import { MOCK_QUEUE_CASES } from "@/lib/mocks/queue";

export type QueueLoadState =
  | { status: "loading" }
  | { status: "empty"; rows: [] }
  | { status: "error"; message: string }
  | { status: "ready"; rows: QueueCaseRow[] };

export type QueueMockMode = "ready" | "empty" | "error";

/**
 * Typed mock consumer for GET /api/v1/cases until Abhishek freezes
 * CaseQueueResponse. No browser calls to LLM / GLEIF / sanctions / RegWatch.
 */
export async function loadQueueMock(
  mode: QueueMockMode = "ready",
  options?: { delayMs?: number },
): Promise<QueueLoadState> {
  const delayMs = options?.delayMs ?? 350;
  await new Promise((resolve) => setTimeout(resolve, delayMs));

  if (mode === "error") {
    return {
      status: "error",
      message:
        "Queue mock failed to load. Backend /api/v1/cases is not wired in this shell task.",
    };
  }

  if (mode === "empty") {
    return { status: "empty", rows: [] };
  }

  return { status: "ready", rows: MOCK_QUEUE_CASES };
}
