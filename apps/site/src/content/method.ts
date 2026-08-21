export const methodHero = {
  eyebrow: "ARCHITECTURE",
  heading: "The model extracts. Code decides.",
  body: [
    "This note describes how a document set becomes a scored exception report, and where the boundary between statistical and deterministic components sits. It is written for the people who have to defend the output: examiners, ops leads, and the second line.",
    "The short version: one vision model transcribes fields and never draws conclusions. Every conclusion is a comparison written in code, against either another document in the same presentation or a published reference band. Severity is a lookup, not a judgement.",
  ],
};

export const boundaryDetail = [
  {
    heading: "What the model is asked",
    body: "The extraction agent receives page images and a field schema. For the commercial invoice it returns eleven fields: seller, buyer, invoice number, invoice date, goods description, HS code, quantity, unit, unit price, line total, and Incoterms. Each field is returned with the page number and a normalised bounding box. The prompt contains no rules, no thresholds, and no notion of a discrepancy, so there is no conclusion for the model to reach.",
  },
  {
    heading: "What the model is not asked",
    body: "It is never asked whether the quantity matches the bill of lading, whether the price is plausible, or whether the presentation is compliant. Worked example: for the demo set the model returns quantity 44,000 kg from the invoice and 42,300 kg from the bill of lading. It does not know these are the same shipment. The cross-check agent knows, because a rule says invoice quantity and transport document quantity must reconcile under Art. 14(d).",
  },
  {
    heading: "Where the decision is made",
    body: "In a function with two arguments and a threshold. The quantity check is a subtraction and a tolerance test. The price check is a division against a band. The consignee check is a normalised string comparison with a legal-suffix list. Each returns a boolean, a severity from a static table, and the article or band it used. Re-run the same document set and you get the same findings, because nothing in that path samples.",
  },
  {
    heading: "What this buys the second line",
    body: "Reproducibility and a short explanation. A finding is defended by pointing at a value on a page, the rule that read it, and the arithmetic. When a rule is wrong it is corrected in one place and the change is visible in a diff. There is no version of the system in which the answer changes because a model was updated.",
  },
];

export const ucpChecks = {
  headers: ["ARTICLE", "CHECK", "WHAT TRIGGERS A DISCREPANCY", "SEVERITY"],
  rows: [
    [
      "14(c)",
      "Presentation period",
      "Documents presented later than 21 days after shipment date, or after credit expiry",
      "CRITICAL",
    ],
    [
      "14(d)",
      "Data consistency across documents",
      "A field present in two documents does not reconcile — quantity, party, port, marks",
      "CRITICAL",
    ],
    [
      "14(e)",
      "Goods description in non-invoice documents",
      "Transport or insurance document describes goods in terms that conflict with the credit",
      "REVIEW",
    ],
    [
      "18(c)",
      "Invoice description against the credit",
      "Invoice goods description is not the description in field :45A: of the credit",
      "CRITICAL",
    ],
    [
      "20",
      "Bill of lading",
      "No carrier name, no on-board notation, no port of loading and discharge as in the credit",
      "CRITICAL",
    ],
    [
      "23",
      "Air waybill",
      "Missing actual flight date where the credit requires it, or wrong airport of departure",
      "CRITICAL",
    ],
    [
      "27",
      "Clean transport document",
      "Any clause or notation declaring a defective condition of goods or packaging",
      "CRITICAL",
    ],
    [
      "28",
      "Insurance cover",
      "Cover less than 110% of CIF value, wrong currency, or dated after shipment date",
      "REVIEW",
    ],
    [
      "30",
      "Tolerance in amount and quantity",
      "Quantity outside ±5% where permitted, or drawing above the credit amount",
      "CRITICAL",
    ],
    [
      "31",
      "Partial shipment",
      "More than one shipment where partial shipment is prohibited in field :43P:",
      "REVIEW",
    ],
  ],
};

export const priceBands = {
  heading: "Price bands",
  body: [
    "A unit-value band is derived from reported trade, not from a model. For an HS code and a directed corridor, take every reported record for the period, divide trade value by net quantity to get a unit value, discard records with missing or zero quantity, and take the interquartile range of what remains. The band is that range; the threshold is a percentage either side of it.",
    "The demo uses pre-computed bands for a single corridor — HS 5208.52, IN→AE, 2025 reporting year — because the numbers must be identical every time this is shown. Production pulls the Comtrade feed and recomputes monthly, and every finding prints the band, the corridor and the period it used so the figure can be checked at source.",
  ],
  arithmetic: [
    "unit_value      = trade_value / net_quantity            (per record)",
    "band            = [ Q1(unit_value) , Q3(unit_value) ]   (per HS + corridor)",
    "",
    "HS 5208.52 · IN→AE · 2025",
    "band            = [ 2.6000 , 2.9000 ] USD/kg",
    "declared        = 4.1200 USD/kg",
    "deviation       = (4.1200 - 2.9000) / 2.9000 = +42.1 %",
    "threshold       = 15.0 %                     -> flagged",
  ],
};

export const notDoing = [
  {
    heading: "We do not approve",
    body: "TradePulse produces an exception report. It does not accept a presentation, refuse one, waive a discrepancy, or release payment. Those are the bank's decisions and they are recorded under the name of the officer who made them. The report is an input to that decision and is stored alongside it.",
  },
  {
    heading: "We do not lend",
    body: "There is no balance sheet here, no participation in the transaction, and no fee tied to whether a presentation clears. The commercial relationship is a licence to examine documents, which keeps the incentive on finding discrepancies rather than on volume passing through.",
  },
  {
    heading: "We do not score with a model",
    body: "Severity comes from a static table keyed by rule. Risk level comes from counting severities. No language model output reaches the score, and no score changes because a model version changed. Re-running the demo set in six months returns 3 discrepancies, 2 critical, as it does today.",
  },
  {
    heading: "We do not assert without a citation",
    body: "Every finding carries a document, a page, a field, and where applicable a UCP article or a price band with its period. A finding that cannot name its source is a bug, not a low-confidence result, and it fails the report assembly step rather than appearing with a caveat.",
  },
];
