import type { DocumentCompletenessItem, QueueCase, TransactionProfile } from "./types";

/**
 * Pre-authored checklist fixtures by profile (display only).
 * Optional docs never set blocker=true.
 */
export const PROFILE_CHECKLIST_FIXTURES: Record<
  TransactionProfile,
  DocumentCompletenessItem[]
> = {
  INVOICE_ONLY_PRE_REVIEW: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "NOT_AVAILABLE",
      label: "BoL / AWB",
      blocker: false,
      reason:
        "Invoice-only profile: transport reconciliation is NOT_AVAILABLE when BoL/AWB is absent.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "NOT_APPLICABLE",
      label: "Letter of Credit",
      blocker: false,
      reason: "LC is required only for LC-profile cases.",
    },
    {
      documentType: "PACKING_LIST",
      state: "OPTIONAL",
      label: "Packing List",
      blocker: false,
      reason: "Supporting document — missing optional docs do not block this case.",
    },
  ],
  POST_SHIPMENT_DOCUMENT_REVIEW: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "REQUIRED",
      label: "BoL / AWB",
      blocker: true,
      reason: "Conditionally required for post-shipment profile; missing → DOCUMENT_PACK_INCOMPLETE.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "NOT_APPLICABLE",
      label: "Letter of Credit",
      blocker: false,
      reason: "LC is required only for LC-profile cases.",
    },
    {
      documentType: "PACKING_LIST",
      state: "CONDITIONALLY_REQUIRED",
      label: "Packing List",
      blocker: false,
      reason: "Conditionally required by policy — not a universal blocker in this fixture.",
    },
  ],
  LC_DOCUMENT_REVIEW: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "REQUIRED",
      label: "Letter of Credit",
      blocker: true,
      reason: "Required only because this case uses the LC profile.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "CONDITIONALLY_REQUIRED",
      label: "BoL / AWB",
      blocker: false,
      reason: "Configured as conditional for this LC packet fixture.",
    },
    {
      documentType: "PACKING_LIST",
      state: "OPTIONAL",
      label: "Packing List",
      blocker: false,
      reason: "Supporting document — missing optional docs do not block this case.",
    },
  ],
  DOCUMENTARY_COLLECTION_REVIEW: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "CONDITIONALLY_REQUIRED",
      label: "BoL / AWB",
      blocker: false,
      reason: "Conditional under collection profile fixture.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "NOT_APPLICABLE",
      label: "Letter of Credit",
      blocker: false,
      reason: "LC is required only for LC-profile cases.",
    },
  ],
  ENHANCED_TRADE_HOUSE_REVIEW: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "REQUIRED",
      label: "BoL / AWB",
      blocker: true,
      reason: "Required under enhanced trade-house packet fixture.",
    },
    {
      documentType: "CERTIFICATE_OF_ORIGIN",
      state: "CONDITIONALLY_REQUIRED",
      label: "Certificate of Origin",
      blocker: false,
      reason: "Conditional supporting document — not treated as a hard block in UI copy.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "NOT_APPLICABLE",
      label: "Letter of Credit",
      blocker: false,
      reason: "LC is required only for LC-profile cases.",
    },
  ],
  DOMESTIC_INDIA_GOODS_MOVEMENT: [
    {
      documentType: "COMMERCIAL_INVOICE",
      state: "REQUIRED",
      label: "Commercial Invoice",
      blocker: true,
      reason: "Required for every core review case under configured policy.",
    },
    {
      documentType: "E_INVOICE_IRN",
      state: "CONDITIONALLY_REQUIRED",
      label: "E-invoice IRN",
      blocker: false,
      reason: "Domestic profile supporting evidence — conditional.",
    },
    {
      documentType: "BILL_OF_LADING_OR_AWB",
      state: "NOT_APPLICABLE",
      label: "BoL / AWB",
      blocker: false,
      reason: "Not the primary transport evidence for this domestic fixture.",
    },
    {
      documentType: "LETTER_OF_CREDIT",
      state: "NOT_APPLICABLE",
      label: "Letter of Credit",
      blocker: false,
      reason: "LC is required only for LC-profile cases.",
    },
  ],
};

export function getChecklistForProfile(
  profile: TransactionProfile,
): DocumentCompletenessItem[] {
  return PROFILE_CHECKLIST_FIXTURES[profile].map((item) => ({ ...item }));
}
