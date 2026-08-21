import { apiBaseUrl } from "./config";
import type {
  CaseRecord,
  CaseSummary,
  DocumentTypeApi,
  ShipmentMode,
  TradeProfile,
  WorkbenchPayload,
} from "./types";
import { ApiError } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
  });
  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!res.ok) {
    const msg =
      typeof body === "object" &&
      body &&
      "error" in body &&
      typeof (body as { error?: { message?: string } }).error?.message === "string"
        ? (body as { error: { message: string } }).error.message
        : `API ${res.status} ${path}`;
    throw new ApiError(msg, res.status, body);
  }
  return body as T;
}

export const api = {
  listCases(): Promise<CaseSummary[]> {
    return request("/cases");
  },

  createCase(input: {
    transaction_profile: TradeProfile;
    corridor?: string;
    shipment_mode?: ShipmentMode;
  }): Promise<CaseRecord> {
    return request("/cases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transaction_profile: input.transaction_profile,
        corridor: input.corridor ?? null,
        shipment_mode: input.shipment_mode ?? "UNKNOWN",
        data_label: "synthetic",
      }),
    });
  },

  getCase(caseId: string): Promise<CaseRecord> {
    return request(`/cases/${encodeURIComponent(caseId)}`);
  },

  getWorkbench(caseId: string): Promise<WorkbenchPayload> {
    return request(`/cases/${encodeURIComponent(caseId)}/workbench`);
  },

  async uploadDocument(
    caseId: string,
    file: File | Blob,
    documentType: DocumentTypeApi,
    filename?: string,
  ): Promise<Record<string, unknown>> {
    const form = new FormData();
    form.append("file", file, filename ?? (file instanceof File ? file.name : "upload.bin"));
    form.append("document_type", documentType);
    return request(`/cases/${encodeURIComponent(caseId)}/documents`, {
      method: "POST",
      body: form,
    });
  },

  processCase(caseId: string): Promise<WorkbenchPayload> {
    return request(`/cases/${encodeURIComponent(caseId)}/process`, { method: "POST" });
  },

  caseAction(
    caseId: string,
    body: { action: string; actor: string; actor_role: string; note?: string },
  ): Promise<CaseRecord> {
    return request(`/cases/${encodeURIComponent(caseId)}/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
};

/** Labeled fixture text the fixture LLM / transport parser understand. */
export const SAMPLE_APPLICATION_TXT = `application_number: APP-1001
facility_type: post_shipment_lc_presentation
applicant: Amit Trading Co.
beneficiary: Gulf Importers LLC
requested_amount: 500000
currency: USD
`;

export const SAMPLE_INVOICE_TXT = `invoice_number: INV-1001
invoice_date: 2026-03-01
currency: USD
seller: Amit Trading Co.
seller_lei: 5493001KJTIIGC8Y1R12
buyer: Gulf Importers LLC
description: Basmati rice
quantity: 500
unit: cartons
unit_price: 1000
line_total: 500000
total_amount: 500000
hs_code: 100630
port_of_loading: INNSA
port_of_discharge: AEJEA
`;

export const SAMPLE_BOL_MATCH_TXT = `bl_number: BOL-1001
shipper: Amit Trading Co.
quantity: 500
unit: cartons
description: Basmati rice
port_of_loading: INNSA
port_of_discharge: AEJEA
invoice_reference: INV-1001
hs_code: 100630
`;

export const SAMPLE_BOL_MISMATCH_TXT = `bl_number: BOL-1001
shipper: Amit Trading Co.
quantity: 350
unit: cartons
description: Basmati rice
port_of_loading: INNSA
port_of_discharge: AEJEA
invoice_reference: INV-1001
hs_code: 100630
`;

export const SAMPLE_AWB_TXT = `awb_number: AWB-7788
shipper: Amit Trading Co.
quantity: 500
unit: cartons
description: Basmati rice
airport_of_departure: BOM
airport_of_destination: DXB
invoice_reference: INV-1001
flight: EK501
hs_code: 100630
`;

export const SAMPLE_LC_TXT = `lc_number: LC-9001
issuing_bank: Demo Bank GIFT City
applicant: Gulf Importers LLC
beneficiary: Amit Trading Co.
amount: 500000
currency: USD
`;

export const SAMPLE_SHIPPING_BILL_TXT = `shipping_bill_number: SB-4401
exporter: INNSA
exporter_invoice: INV-1001
`;
