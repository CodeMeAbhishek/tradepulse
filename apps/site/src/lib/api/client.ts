/**
 * Client for the TradePulse FastAPI backend.
 *
 * Deliberately a plain async module, not a TanStack server function: the API is
 * a separate service, and the seam must not depend on this framework.
 *
 * The browser talks to this backend and to nothing else. It must never call
 * GLEIF, a VLEI verifier, a sanctions source, or a model provider directly --
 * every one of those lives behind the API, where the audit trail is.
 */

import type { ApiCaseRecord, ApiCaseSummary, ApiErrorBody, ApiProcessResult } from "./types";

const DEFAULT_BASE = "http://localhost:8000";

export function apiBaseUrl(): string {
  const configured = import.meta.env["VITE_API_URL"];
  return (typeof configured === "string" && configured.trim()) || DEFAULT_BASE;
}

/** A failed call, carrying the backend's own error contract when it sent one. */
export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;
  readonly correlationId: string | undefined;
  readonly retryable: boolean;

  constructor(
    message: string,
    opts: { status: number; code?: string; correlationId?: string; retryable?: boolean },
  ) {
    super(message);
    this.name = "ApiRequestError";
    this.status = opts.status;
    this.code = opts.code ?? "UNKNOWN";
    this.correlationId = opts.correlationId;
    this.retryable = opts.retryable ?? false;
  }
}

/** Aborts rather than hanging: a stalled call must surface, not spin forever. */
const TIMEOUT_MS = 15_000;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch (cause) {
    clearTimeout(timer);
    const aborted = cause instanceof DOMException && cause.name === "AbortError";
    throw new ApiRequestError(
      aborted
        ? `Request to ${path} timed out after ${TIMEOUT_MS / 1000}s.`
        : `Could not reach the TradePulse API at ${apiBaseUrl()}.`,
      { status: 0, code: aborted ? "TIMEOUT" : "NETWORK_UNREACHABLE", retryable: true },
    );
  }
  clearTimeout(timer);

  if (!response.ok) {
    // The backend returns a typed error envelope; fall back if it did not.
    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = null;
    }
    throw new ApiRequestError(body?.error?.message ?? `Request to ${path} failed.`, {
      status: response.status,
      ...(body?.error?.code !== undefined ? { code: body.error.code } : {}),
      ...(body?.error?.correlation_id !== undefined
        ? { correlationId: body.error.correlation_id }
        : {}),
      ...(body?.error?.retryable !== undefined ? { retryable: body.error.retryable } : {}),
    });
  }

  return (await response.json()) as T;
}

export const api = {
  health: () => request<{ status: string; service: string; version: string }>("/healthz"),

  listCases: () => request<ApiCaseSummary[]>("/api/v1/cases"),

  getCase: (caseId: string) =>
    request<ApiCaseRecord>(`/api/v1/cases/${encodeURIComponent(caseId)}`),

  processCase: (caseId: string) =>
    request<ApiProcessResult>(`/api/v1/cases/${encodeURIComponent(caseId)}/process`, {
      method: "POST",
    }),

  createCase: (input: { transaction_profile: string; corridor?: string }) =>
    request<ApiCaseRecord>("/api/v1/cases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }),

  uploadDocument: (caseId: string, file: File, documentType: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("document_type", documentType);
    // No Content-Type header: the browser must set the multipart boundary.
    return request<{ document_id: string; sha256: string; processing_state: string }>(
      `/api/v1/cases/${encodeURIComponent(caseId)}/documents`,
      { method: "POST", body: form },
    );
  },
};
