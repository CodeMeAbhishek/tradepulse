export const hero = {
  eyebrow: "VERIFICATION MIDDLEWARE · CROSS-BORDER TRADE FINANCE",
  lines: ["Twenty documents.", "Three days.", "One discrepancy that matters."],
  body: "TradePulse reads a cross-border trade document set, checks it against UCP 600 and market price bands, and returns a scored exception report with every finding traced to its source clause. The model extracts. Code decides.",
  actions: {
    primary: "See a live examination",
    secondary: "How a finding is proved",
  },
};

export const problem = {
  rows: [
    {
      figure: "USD 2.5tn",
      heading: "The trade finance gap",
      body: "Banks decline trade finance applications they cannot examine quickly enough to price. The rejected volume sits mostly with small and mid-sized exporters in exactly the corridors where document sets arrive on paper, in scans, and in four languages. Examination cost, not credit risk, decides most of it.",
      citation: "ADB Trade Finance Gaps Report — verify figure and year before quoting",
    },
    {
      figure: "3 days",
      heading: "Median manual review time for one full document set",
      body: "An examiner opens twenty-odd pages, transcribes the same eleven fields four times, and compares them by eye against the credit. Most of the three days is transcription and re-reading, not judgement. The judgement takes twenty minutes and happens last, when attention is lowest.",
      citation: null,
    },
    {
      figure: "80%",
      heading: "Share of trade-based money laundering that moves through over- and under-invoicing",
      body: "A declared unit price is the easiest number in the file to move and the hardest to challenge without a reference. An invoice at USD 4.12/kg against a corridor band of 2.60–2.90 is not a typing error, but nothing in a manual examination surfaces it unless the examiner already knows the market.",
      citation: null,
    },
  ],
  closing: "Every one of those days is an exporter's working capital, frozen.",
};

export const methodSteps = [
  {
    number: "01",
    title: "Extract",
    lead: "The model reads. Fields, never conclusions.",
    body: "Vision extraction over each page returns eleven typed fields per document — parties, quantity, unit price, currency, dates, ports, vessel, marks. Each field carries the page and coordinates it came from. The model is not asked whether anything is wrong; it is asked what the document says.",
    emits: "Typed fields with page and coordinates",
  },
  {
    number: "02",
    title: "Cross-check",
    lead: "UCP 600 rules in deterministic code.",
    body: "Invoice against bill of lading against packing list against the credit. Quantity, description, consignee, dates and amounts are compared field to field in plain code, and each mismatch is mapped to the article that makes it a discrepancy — 14(d) for data consistency, 18(c) for the invoice description, 30 for tolerance.",
    emits: "Discrepancies with UCP article references",
  },
  {
    number: "03",
    title: "Verify price",
    lead: "Declared unit value against UN Comtrade bands.",
    body: "Trade value divided by quantity gives a unit value per HS code and corridor. The band is the interquartile range of reported unit values for HS 5208.52 on IN→AE. A declared price outside the band by more than 15% is flagged with the arithmetic shown, not asserted.",
    emits: "Deviation percentage against a published band",
  },
  {
    number: "04",
    title: "Screen and score",
    lead: "Parties, vessel, ports. Then one report a human signs.",
    body: "Applicant, beneficiary, carrier, vessel and both ports are screened against OFAC SDN, EU CFSP and UN 1267 with the list version recorded. Severity is assigned by rule, the report is assembled, and a named officer signs it off. Nothing is released on the model's word.",
    emits: "Scored exception report, awaiting sign-off",
  },
];

export const boundary = {
  model: ["reads pixels", "locates fields", "normalises formats", "transcribes values"],
  code: [
    "compares values across documents",
    "applies UCP 600 articles",
    "tests against price bands",
    "assigns severity",
  ],
  line: "A model cannot invent a discrepancy it is not permitted to declare.",
};

export const numbers = [
  { value: 30, prefix: "< ", suffix: "s", label: "PER DOCUMENT SET" },
  { value: 5, prefix: "", suffix: "", label: "DOCUMENT TYPES READ" },
  { value: 0, prefix: "", suffix: "", label: "DECISIONS SCORED BY A MODEL" },
  { value: 100, prefix: "", suffix: "%", label: "FINDINGS CARRYING A SOURCE CITATION" },
];

export const useCases = [
  {
    title: "Import LC examination",
    scenario:
      "A confirming bank receives a presentation against a sight credit and has five banking days to accept or refuse. The bench returns the discrepancy list in under thirty seconds so the refusal notice, if there is one, is drafted on day one rather than day four.",
    agents: "Extraction · Cross-check · Screening",
    corridor: "IN→AE, live",
  },
  {
    title: "Export document presentation",
    scenario:
      "An exporter's documentation team checks its own presentation before it leaves the office. The quantity mismatch between invoice and bill of lading is corrected at source, which removes the discrepancy fee and the seven-day round trip.",
    agents: "Extraction · Cross-check",
    corridor: "IN→AE, live",
  },
  {
    title: "TBML price screening",
    scenario:
      "A financial crime team screens a month of corridor volume for over- and under-invoicing. Declared unit values are tested against Comtrade bands by HS code, and only presentations outside the band by more than 15% reach an analyst.",
    agents: "Extraction · Price verification",
    corridor: "IN→AE, live · SG in development",
  },
  {
    title: "Sanctions and vessel screening",
    scenario:
      "Parties, carrier, vessel and both ports are screened with the list version recorded against the file. When a list changes, the screening can be re-run against the same document set and the two results compared line by line.",
    agents: "Extraction · Screening",
    corridor: "All corridors",
  },
  {
    title: "Discrepancy audit trail",
    scenario:
      "An internal audit asks why a presentation was accepted in 2026 Q1. Every finding, its citation, the rule applied and the officer who signed it are stored with the report, so the answer is retrieved rather than reconstructed.",
    agents: "All four, recorded",
    corridor: "All corridors",
  },
  {
    title: "Correspondent bank review",
    scenario:
      "A correspondent reviews the examination quality of a respondent bank. Sampled document sets are re-examined and the two discrepancy lists are compared, which turns a questionnaire answer into a measurement.",
    agents: "Extraction · Cross-check · Price verification",
    corridor: "IN→AE, live",
  },
];

export const faq = [
  {
    q: "Where do the reference prices come from?",
    a: "UN Comtrade reported trade values and quantities, reduced to a unit value per HS code and corridor. The band is the interquartile range of those unit values for the relevant period. The demo ships pre-computed bands for HS 5208.52 on IN→AE; production pulls the feed and recomputes monthly. The band and its period are printed on every price finding so the number can be checked against the source.",
  },
  {
    q: "Are you checking against UCP 600?",
    a: "Yes, and only the articles we have written as code. The current set covers 14(c) presentation period, 14(d) data consistency, 14(e) goods description, 18(c) invoice description, 20 bill of lading, 23 air waybill, 27 clean transport document, 28 insurance cover, 30 tolerance in amount and quantity, and 31 partial shipment. Each check names its article on the finding. Articles we do not check are listed rather than implied.",
  },
  {
    q: "What happens when you produce a false positive?",
    a: "The finding is dismissed with a reason, the dismissal is stored against the document set, and the rule that produced it is reviewed with its hit rate. Because severity comes from deterministic rules, a false positive is traced to one rule and one threshold and corrected there. There is no retraining step and no unexplained change in behaviour between runs.",
  },
  {
    q: "What if the model hallucinates a discrepancy?",
    a: "It cannot, because it is never asked for one. The model returns field values with page coordinates. Discrepancies are declared by code comparing those values, so the worst a bad extraction produces is a wrong value on screen next to the region of the document it was read from — which an examiner sees and corrects in place. A discrepancy with no rule behind it has nothing to attach itself to.",
  },
  {
    q: "Who signs off?",
    a: "A named compliance officer at the bank. TradePulse produces an exception report with severities and citations; it does not accept, refuse, or waive anything. The sign-off, the officer's identity and the time are recorded with the report and appear in the audit trail.",
  },
];

export const closing = {
  heading: "See it examine a real document set.",
  action: "See a live examination",
};
