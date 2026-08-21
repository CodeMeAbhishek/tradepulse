export const productHero = {
  eyebrow: "THE EXAMINATION BENCH",
  heading: "The document is never replaced by a summary of itself.",
  body: [
    "The bench is a working surface, not a dashboard. The document set stays on screen at full size while the findings sit beside it, and every finding is a link back into the page and field it came from. Clicking a finding moves the document, not the reader.",
    "It is used by trade finance examiners at the point of presentation, by financial crime analysts screening corridor volume, and by internal audit reconstructing a decision months later. All three need the same thing: the value, the rule, and the place on the page.",
  ],
};

export const screenRegions = {
  headers: ["REGION", "WHAT IS ON IT", "WHY IT IS THERE"],
  rows: [
    [
      "Status strip",
      "Document count, corridor, HS code",
      "The scope of the examination, readable without scrolling",
    ],
    [
      "Document plane, left",
      "The presented document at full size on paper stock",
      "The evidence itself, never a summary of it",
    ],
    [
      "Annotation overlay",
      "A drawn box on the cited region, and a connector between two conflicting values",
      "Proof that the finding names a real place on the page",
    ],
    [
      "Agent column, right",
      "Four agents, each with the findings it emitted",
      "Which process produced which finding",
    ],
    [
      "Findings list",
      "Severity, title, body, citation, UCP article",
      "The report, in the order an examiner works through it",
    ],
    [
      "Score line",
      "Discrepancy count, critical count, numeric risk score",
      "The headline, kept secondary to the findings that caused it",
    ],
  ],
};

export const agents = {
  headers: ["AGENT", "WHAT IT READS", "WHAT IT EMITS", "NOT PERMITTED TO DECIDE"],
  rows: [
    [
      "EXTRACTION",
      "Every page of every document, as pixels",
      "Typed field values with page and coordinates",
      "Whether any value is correct, expected, or acceptable",
    ],
    [
      "CROSS-CHECK",
      "Extracted fields from all five documents",
      "Discrepancies mapped to UCP 600 articles",
      "Anything not covered by a written rule; it cannot invent an article",
    ],
    [
      "PRICE VERIFICATION",
      "Declared unit value, HS code, corridor, quantity",
      "Deviation percentage against a published band",
      "Whether a price is fraudulent; it reports distance from a band",
    ],
    [
      "SCREENING",
      "Party names, carrier, vessel, IMO, ports",
      "Match status per entity with list name and version",
      "Whether a match blocks the transaction; that is the officer's call",
    ],
  ],
};

export const tracedFinding = {
  heading: "One finding, fully traced",
  rows: [
    ["SOURCE DOCUMENT", "Commercial Invoice GTX-2026-0912"],
    ["PAGE", "1 of 2"],
    ["FIELD", "line 3 · unit price"],
    ["EXTRACTED VALUE", "USD 4.12 / kg"],
    ["QUANTITY ON THE SAME LINE", "44,000 kg"],
    ["LINE TOTAL AS PRINTED", "USD 181,280.00"],
    ["RULE APPLIED", "Price band deviation, threshold 15% either side"],
    ["REFERENCE BAND", "USD 2.60 – 2.90 / kg · HS 5208.52 · IN→AE"],
    ["BAND SOURCE", "UN Comtrade reported values, pre-computed for the demo"],
    ["SEVERITY", "CRITICAL"],
  ],
  arithmetic: [
    "declared        = 181,280.00 / 44,000 kg   = 4.1200 USD/kg",
    "band ceiling    =                            2.9000 USD/kg",
    "deviation       = (4.1200 - 2.9000) / 2.9000 = +0.4207",
    "deviation pct   =                            = +42.1 %",
    "threshold       =                            =  15.0 %",
    "value at band   = 2.9000 x 44,000 kg        = 127,600.00 USD",
    "excess declared = 181,280.00 - 127,600.00   =  53,680.00 USD",
  ],
  note: "The arithmetic is printed because it is the whole argument. An examiner who disagrees with the finding disagrees with a division, a subtraction, and a published band — not with a score.",
};
