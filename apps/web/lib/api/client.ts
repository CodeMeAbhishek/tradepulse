/** Typed TradePulse API client — browser calls only the local/backend API. */

export type TradeProfile =
  | "INVOICE_ONLY_PRE_REVIEW"
  | "POST_SHIPMENT_DOCUMENT_REVIEW"
  | "LC_DOCUMENT_REVIEW"
  | "DOCUMENTARY_COLLECTION_REVIEW"
  | "ENHANCED_TRADE_HOUSE_REVIEW"
  | "DOMESTIC_INDIA_GOODS_MOVEMENT"
  | "MERCHANT_SHIPMENT_READINESS";

export type CaseState =
  | "INGESTED"
  | "PROCESSING"
  | "EXTRACTION_REVIEW"
  | "PENDING_MAKER"
  | "INVESTIGATION_REQUIRED"
  | "MAKER_APPROVED"
  | "CHECKER_APPROVED"
  | "CHECKER_REJECTED"
  | "PROCESSING_FAILED";

export interface CaseSummary {
  case_id: string;
  transaction_profile: TradeProfile;
  state: CaseState;
  risk_route: string | null;
  assignee: string | null;
  created_at: string;
  updated_at: string;
  data_label: string;
  document_count: number;
}

export interface CaseRecord {
  case_id: string;
  transaction_profile: TradeProfile;
  state: CaseState;
  corridor: string | null;
  risk_route: string | null;
  assignee: string | null;
  created_at: string;
  updated_at: string;
  data_label: string;
  version: number;
  identities: IdentityEvidence[];
  metadata: Record<string, unknown>;
}

export interface IdentityEvidence {
  role: string;
  raw_name: string | null;
  normalized_name: string | null;
  resolution_status: string;
  lei: {
    lei: string | null;
    legal_name: string | null;
    is_exact_document_match: boolean;
    source: string;
  } | null;
  vlei: {
    status: string;
    source: string;
    data_label: string | null;
  } | null;
  registry_candidates: Array<{
    candidate_name: string;
    source: string;
    score: number | null;
    stable_identifier: string | null;
  }>;
}

export interface RuleResult {
  check_id: string;
  rule_pack_version: string;
  status: string;
  severity: string;
  reason: string;
  rule_reference: string | null;
  recommended_action: string | null;
  data_sources: Array<{ source_id: string; version: string | null; snapshot_id: string | null }>;
  evidence: Array<{ field: string | null; value: unknown; page: number | null; note: string | null }>;
}

export interface FieldComparison {
  field_path: string;
  invoice_value: unknown;
  bol_value: unknown;
  status: string;
  reason: string;
}

export interface WorkbenchSnapshot {
  policy?: {
    pack_status?: string;
    requirements?: Array<{
      document_type: string;
      state?: string;
      requirement?: string;
      provided: boolean;
      blocker?: boolean;
      blocks_completeness?: boolean;
    }>;
  };
  findings?: RuleResult[];
  risk_route?: string | null;
  reconciliation?: {
    status: string;
    comparisons: FieldComparison[];
    reason: string;
    recommended_action: string | null;
  } | null;
  identities?: IdentityEvidence[];
  documents?: Array<{
    document_id: string;
    document_type: string;
    filename: string;
    sha256: string;
  }>;
  invoice_number?: string | null;
  currency?: string | null;
  total_amount?: number | null;
  seller_name?: string | null;
  agent_trace?: Array<{
    agent_name?: string;
    status?: string;
    round?: number;
    notes?: string | null;
    claims?: unknown[];
    challenges?: unknown[];
  }>;
  debate_rounds_used?: number;
  extraction_provider?: string | null;
  extraction_model?: string | null;
}

export interface ProcessResponse extends WorkbenchSnapshot {
  case: CaseRecord;
}

export interface AuditEvent {
  event_id?: string;
  event_type: string;
  actor: string;
  case_id: string | null;
  occurred_at?: string;
  timestamp?: string;
  created_at?: string;
  payload?: Record<string, unknown>;
}

export interface RegWatchEvent {
  proposal_id: string;
  rule_pack_id: string;
  proposed_version: string;
  summary: string;
  active: boolean;
  status?: string;
  source_id?: string | null;
}

function baseUrl(): string {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
    "http://127.0.0.1:8000/api/v1"
  );
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${baseUrl()}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as {
        error?: { message?: string; code?: string };
        detail?: unknown;
      };
      detail =
        body.error?.message ||
        body.error?.code ||
        (typeof body.detail === "string" ? body.detail : detail);
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => fetch(`${baseUrl().replace(/\/api\/v1$/, "")}/healthz`).then((r) => r.ok),

  listCases: () => request<CaseSummary[]>("/cases"),

  getCase: (id: string) => request<CaseRecord>(`/cases/${id}`),

  createCase: (body: {
    transaction_profile: TradeProfile;
    corridor?: string;
    assignee?: string;
    data_label?: string;
  }) =>
    request<CaseRecord>("/cases", {
      method: "POST",
      body: JSON.stringify({ data_label: "synthetic", ...body }),
    }),

  uploadDocument: async (
    caseId: string,
    file: Blob,
    filename: string,
    documentType: "commercial_invoice" | "bill_of_lading",
  ) => {
    const form = new FormData();
    form.append("file", file, filename);
    form.append("document_type", documentType);
    return request<Record<string, unknown>>(`/cases/${caseId}/documents`, {
      method: "POST",
      body: form,
    });
  },

  processCase: (caseId: string) =>
    request<ProcessResponse>(`/cases/${caseId}/process`, { method: "POST" }),

  caseAction: (
    caseId: string,
    body: { action: string; actor: string; actor_role: string; note?: string },
  ) =>
    request<CaseRecord>(`/cases/${caseId}/actions`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  audit: (caseId: string) => request<AuditEvent[]>(`/cases/${caseId}/audit`),

  policy: (caseId: string) => request<WorkbenchSnapshot["policy"]>(`/cases/${caseId}/policy`),

  identityLadder: (caseId: string) =>
    request<
      Array<{
        role: string;
        party_name: string | null;
        resolution_status: string;
        current_rung_id: string | null;
        side_state: string | null;
        safety_note: string;
        steps: Array<{
          rung_id: string;
          label: string;
          description: string;
          reached: boolean;
          current: boolean;
        }>;
      }>
    >(`/cases/${caseId}/identity-ladder`),

  examinerPack: (caseId: string) =>
    request<Record<string, unknown>>(`/cases/${caseId}/examiner-pack`),

  regwatchEvents: () => request<RegWatchEvent[]>("/regwatch/events"),

  sources: () => request<Array<{ source_id: string; label?: string }>>("/sources"),
};

export function dataMode(): "api" | "demo" {
  const mode = (process.env.NEXT_PUBLIC_DATA_MODE || "api").toLowerCase();
  return mode === "demo" ? "demo" : "api";
}
