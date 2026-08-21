/**
 * Typed mock API client placeholder.
 * Browser must not call LLM, GLEIF, VLEI, or sanctions APIs directly.
 */

export type CaseStatus =
  | "DRAFT"
  | "READY_FOR_HUMAN_REVIEW"
  | "REVIEW_REQUIRED"
  | "DOCUMENT_PACK_INCOMPLETE"
  | "DATA_REVIEW_REQUIRED";

export interface TradeCaseSummary {
  id: string;
  profile: string;
  status: CaseStatus;
  createdAt: string;
}

export interface ApiClient {
  listCases(): Promise<TradeCaseSummary[]>;
  getCase(id: string): Promise<TradeCaseSummary | null>;
}

const MOCK_CASES: TradeCaseSummary[] = [];

/**
 * Returns a typed client that serves empty mock data until the real API is wired.
 */
export function createMockApiClient(): ApiClient {
  return {
    async listCases() {
      return [...MOCK_CASES];
    },
    async getCase(id: string) {
      return MOCK_CASES.find((c) => c.id === id) ?? null;
    },
  };
}
