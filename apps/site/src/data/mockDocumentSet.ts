// SYNTHETIC DEMO DATA
// Cotton woven fabric, India to UAE, HS 5208.52, USD 181,280.
// Only src/lib/analysis.ts may import this file.

import type {
  DocumentSetResult,
  ExtractionResult,
  Finding,
  PriceAuditResult,
  VerificationResult,
} from "@/types";

// SYNTHETIC DEMO DATA — the shipment itself, quoted by the facsimiles.
export const shipment = {
  hsCode: "5208.52",
  corridor: "IN→AE",
  description: "Cotton woven fabric, printed, plain weave, 100% cotton",
  lcRef: "LC/EBI/2026/44817",
  invoiceRef: "GTX-2026-0912",
  blRef: "KLYG4471882",
  coRef: "CO/CBE/2026/10233",
  invoiceQtyKg: 44000,
  blQtyKg: 42300,
  unitPrice: 4.12,
  totalValue: 181280,
  currency: "USD",
  bandLow: 2.6,
  bandHigh: 2.9,
  vessel: "MV KOTA LAYANG",
  voyage: "KL-0912E",
  portOfLoading: "INNSA · Nhava Sheva",
  portOfDischarge: "AEJEA · Jebel Ali",
  incoterms: "CIF Jebel Ali",
  presentationDays: 21,
  invoiceDate: "2026-02-11",
  shipmentDate: "2026-02-18",
  lcExpiry: "2026-03-24",
  applicant: "Al-Futtaim Textiles LLC, Dubai, UAE",
  beneficiary: "Global Textiles Pvt Ltd, Coimbatore, India",
  coConsignee: "Al-Futtaim General Trading FZE, Jebel Ali Free Zone, UAE",
  issuingBank: "Emirates NBD, Dubai",
  advisingBank: "State Bank of India, Coimbatore",
} as const;

// SYNTHETIC DEMO DATA — what the extraction agent transcribed.
const extraction: ExtractionResult = {
  item: "Cotton woven fabric, printed — HS 5208.52",
  quantity: "44,000 kg",
  unit_price: "4.12",
  currency: "USD",
  buyer: "Al-Futtaim Textiles LLC, Dubai, UAE",
  seller: "Global Textiles Pvt Ltd, Coimbatore, India",
  invoice_date: "2026-02-11",
  shipment_terms: "CIF Jebel Ali",
};

// SYNTHETIC DEMO DATA — sanctions screening results.
const verification: VerificationResult[] = [
  {
    entity: "Al-Futtaim Textiles LLC",
    match_status: "clear",
    matched_name: null,
    confidence: 0,
    source_list: "OFAC SDN · EU CFSP · UN 1267",
  },
  {
    entity: "Global Textiles Pvt Ltd",
    match_status: "clear",
    matched_name: null,
    confidence: 0,
    source_list: "OFAC SDN · EU CFSP · UN 1267",
  },
  {
    entity: "MV KOTA LAYANG (IMO 9312884)",
    match_status: "clear",
    matched_name: null,
    confidence: 0,
    source_list: "OFAC vessel list · UANI",
  },
  {
    entity: "AEJEA / INNSA",
    match_status: "clear",
    matched_name: null,
    confidence: 0,
    source_list: "Port sanctions register",
  },
];

// SYNTHETIC DEMO DATA — declared unit value against the Comtrade band.
const priceAudit: PriceAuditResult = {
  item: "HS 5208.52 · IN→AE",
  declared_price: 4.12,
  benchmark_price: 2.9,
  deviation_pct: 42.1,
  flagged: true,
  threshold_pct: 15,
};

// SYNTHETIC DEMO DATA — regions are fractions of the document plane, 0–1.
const findings: Finding[] = [
  {
    id: "F-1",
    severity: "critical",
    title: "Unit price exceeds reference band",
    body: "Invoice declares USD 4.12/kg. The UN Comtrade unit-value band for HS 5208.52 on the IN→AE corridor is 2.60–2.90/kg. Deviation is +42.1% above the band ceiling, above the 15% screening threshold. Over-invoicing of this size moves USD 53,680 of value out of the corridor on one presentation.",
    sourceDoc: "Commercial Invoice",
    sourceKind: "invoice",
    page: 1,
    field: "line 3 · unit price",
    agent: "price",
    ucpArticle: null,
    type: "single",
    region: { x: 0.06, y: 0.545, w: 0.88, h: 0.085 },
  },
  {
    id: "F-2",
    severity: "critical",
    title: "Quantity does not reconcile across documents",
    body: "Commercial invoice states 44,000 kg. Bill of lading states 42,300 kg for the same shipment under B/L KLYG4471882. A 1,700 kg difference is a data inconsistency between documents presented under the same credit.",
    sourceDoc: "Commercial Invoice",
    sourceKind: "invoice",
    page: 1,
    field: "line 3 · quantity",
    agent: "consistency",
    ucpArticle: "UCP 600 Art. 14(d)",
    type: "cross_document",
    region: { x: 0.06, y: 0.545, w: 0.42, h: 0.085 },
    secondDoc: "Bill of Lading",
    secondKind: "billOfLading",
    secondRegion: { x: 0.06, y: 0.6, w: 0.42, h: 0.085 },
  },
  {
    id: "F-3",
    severity: "review",
    title: "Consignee on certificate of origin differs from LC beneficiary",
    body: "The certificate of origin names Al-Futtaim General Trading FZE, Jebel Ali Free Zone. The credit names Al-Futtaim Textiles LLC, Dubai as applicant. Related names are not the same legal party; the presentation needs the beneficiary to confirm the consignment route before the document is accepted.",
    sourceDoc: "Certificate of Origin",
    sourceKind: "certificateOfOrigin",
    page: 1,
    field: "box 2 · consignee",
    agent: "consistency",
    ucpArticle: "UCP 600 Art. 14(d)",
    type: "cross_document",
    region: { x: 0.06, y: 0.34, w: 0.44, h: 0.1 },
    secondDoc: "Letter of Credit (MT700)",
    secondKind: "mt700",
    secondRegion: { x: 0.06, y: 0.29, w: 0.6, h: 0.09 },
  },
  {
    id: "F-4",
    severity: "passed",
    title: "No sanctions matches on parties, vessel or ports",
    body: "Applicant, beneficiary, carrier, vessel MV KOTA LAYANG (IMO 9312884), port of loading INNSA and port of discharge AEJEA screened clear against OFAC SDN, EU CFSP and UN 1267 at list versions dated 2026-02-19.",
    sourceDoc: "Letter of Credit (MT700)",
    sourceKind: "mt700",
    page: 1,
    field: ":50: applicant · :59: beneficiary",
    agent: "sanctions",
    ucpArticle: null,
    type: "single",
    region: { x: 0.06, y: 0.29, w: 0.6, h: 0.14 },
  },
  {
    id: "F-5",
    severity: "passed",
    title: "LC expiry and presentation period within terms",
    body: "Shipment dated 2026-02-18, presentation period 21 days, credit expires 2026-03-24. Documents presented 2026-02-26, on day 8 of 21 and 26 days before expiry.",
    sourceDoc: "Letter of Credit (MT700)",
    sourceKind: "mt700",
    page: 1,
    field: ":31D: date and place of expiry",
    agent: "consistency",
    ucpArticle: "UCP 600 Art. 14(c)",
    type: "single",
    region: { x: 0.06, y: 0.45, w: 0.6, h: 0.07 },
  },
];

// SYNTHETIC DEMO DATA — the full result the backend will return.
export const mockDocumentSet: DocumentSetResult = {
  document_id: "SET-2026-0912-IN-AE",
  extraction,
  verification,
  price_audit: priceAudit,
  risk_level: "red",
  findings,
};
