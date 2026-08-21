import type { DocumentSetResult } from "@/types";
import { mockDocumentSet } from "@/data/mockDocumentSet";

// INTEGRATION SEAM — replace body with POST /api/analyze, keep signature.
// Plain client-side async function on purpose: it becomes a fetch to the
// external FastAPI service without touching anything else in the codebase.
export async function runAnalysis(): Promise<DocumentSetResult> {
  await new Promise((resolve) => setTimeout(resolve, 450));
  return mockDocumentSet;
}
