// Facsimile copy. Presentation-side only; the analysis result is the seam.

export type FieldRow = { label: string; value: string };

export const invoiceDoc = {
  letterhead: "GLOBAL TEXTILES PVT LTD",
  address: ["41/3 Avinashi Road, Peelamedu", "Coimbatore 641004, Tamil Nadu, India"],
  meta: [
    { label: "INVOICE NO", value: "GTX-2026-0912" },
    { label: "DATE", value: "2026-02-11" },
    { label: "LC REFERENCE", value: "LC/EBI/2026/44817" },
  ] as FieldRow[],
  title: "COMMERCIAL INVOICE",
  parties: [
    { label: "BUYER", value: "Al-Futtaim Textiles LLC, Dubai, UAE" },
    { label: "SELLER", value: "Global Textiles Pvt Ltd, Coimbatore, India" },
    { label: "INCOTERMS", value: "CIF Jebel Ali" },
    { label: "COUNTRY OF ORIGIN", value: "India" },
  ] as FieldRow[],
  lineHeaders: ["LINE", "DESCRIPTION", "HS CODE", "QUANTITY", "UNIT PRICE", "AMOUNT"],
  lines: [
    ["1", "Cotton yarn, combed, 40s", "5205.24", "2,000 kg", "3.05", "6,100.00"],
    ["2", "Packing and marking", "—", "1 lot", "480.00", "480.00"],
    ["3", "Cotton woven fabric, printed", "5208.52", "44,000 kg", "4.12", "181,280.00"],
  ],
  total: "USD 187,860.00",
  signature: "For Global Textiles Pvt Ltd · Authorised signatory",
  stamp: ["GLOBAL TEXTILES", "COIMBATORE"],
};

export const blDoc = {
  letterhead: "PACIFIC INTERNATIONAL LINES",
  address: ["7 Straits View, Marina One", "Singapore 018936"],
  meta: [
    { label: "B/L NO", value: "KLYG4471882" },
    { label: "DATE OF ISSUE", value: "2026-02-18" },
    { label: "VOYAGE", value: "KL-0912E" },
  ] as FieldRow[],
  title: "BILL OF LADING",
  parties: [
    { label: "SHIPPER", value: "Global Textiles Pvt Ltd, Coimbatore, India" },
    { label: "CONSIGNEE", value: "Al-Futtaim Textiles LLC, Dubai, UAE" },
    { label: "VESSEL", value: "MV KOTA LAYANG · IMO 9312884" },
    { label: "PORT OF LOADING", value: "INNSA · Nhava Sheva" },
    { label: "PORT OF DISCHARGE", value: "AEJEA · Jebel Ali" },
  ] as FieldRow[],
  cargoHeaders: ["MARKS", "PACKAGES", "DESCRIPTION", "GROSS WEIGHT"],
  cargo: [["GTX/AFT/0912", "880 bales", "Cotton woven fabric, printed", "42,300 kg"]],
  notation: "SHIPPED ON BOARD 2026-02-18 · FREIGHT PREPAID · CLEAN",
  signature: "As agent for the carrier · Authorised signatory",
  stamp: ["PIL AGENCY", "NHAVA SHEVA"],
};

export const coDoc = {
  letterhead: "TIRUPUR EXPORTERS ASSOCIATION",
  address: ["Chamber of Commerce Building, Kumaran Road", "Tirupur 641601, India"],
  meta: [
    { label: "CERTIFICATE NO", value: "CO/CBE/2026/10233" },
    { label: "DATE", value: "2026-02-19" },
  ] as FieldRow[],
  title: "CERTIFICATE OF ORIGIN",
  boxes: [
    { label: "BOX 1 · EXPORTER", value: "Global Textiles Pvt Ltd, Coimbatore, India" },
    {
      label: "BOX 2 · CONSIGNEE",
      value: "Al-Futtaim General Trading FZE, Jebel Ali Free Zone, UAE",
    },
    { label: "BOX 3 · COUNTRY OF ORIGIN", value: "India" },
    { label: "BOX 4 · TRANSPORT", value: "MV KOTA LAYANG · INNSA to AEJEA" },
    { label: "BOX 5 · GOODS", value: "Cotton woven fabric, printed · HS 5208.52 · 42,300 kg" },
  ] as FieldRow[],
  declaration:
    "It is hereby certified, on the basis of control carried out, that the goods described above originate in India.",
  signature: "Authorised certifying officer",
  stamp: ["TEA TIRUPUR", "CERTIFIED"],
};

export const mt700Doc = {
  letterhead: "EMIRATES NBD",
  address: ["Baniyas Road, Deira", "PO Box 777, Dubai, UAE"],
  meta: [
    { label: "MESSAGE TYPE", value: "MT700" },
    { label: "SENT", value: "2026-01-28 09:14 GST" },
  ] as FieldRow[],
  title: "ISSUE OF A DOCUMENTARY CREDIT",
  tags: [
    { tag: ":20:", label: "DOCUMENTARY CREDIT NUMBER", value: ["LC/EBI/2026/44817"] },
    { tag: ":31D:", label: "DATE AND PLACE OF EXPIRY", value: ["260324 DUBAI"] },
    { tag: ":32B:", label: "CURRENCY CODE, AMOUNT", value: ["USD181280,00"] },
    { tag: ":44E:", label: "PORT OF LOADING", value: ["NHAVA SHEVA, INDIA (INNSA)"] },
    {
      tag: ":45A:",
      label: "DESCRIPTION OF GOODS",
      value: [
        "COTTON WOVEN FABRIC, PRINTED, PLAIN WEAVE,",
        "100PCT COTTON, HS 5208.52",
        "44000 KG AT USD 4,12 PER KG",
        "CIF JEBEL ALI (INCOTERMS 2020)",
      ],
    },
    {
      tag: ":46A:",
      label: "DOCUMENTS REQUIRED",
      value: [
        "1. SIGNED COMMERCIAL INVOICE IN TRIPLICATE",
        "2. FULL SET 3/3 ORIGINAL CLEAN ON BOARD B/L",
        "3. PACKING LIST IN DUPLICATE",
        "4. CERTIFICATE OF ORIGIN ISSUED BY CHAMBER",
      ],
    },
    {
      tag: ":47A:",
      label: "ADDITIONAL CONDITIONS",
      value: [
        "DOCUMENTS TO BE PRESENTED WITHIN 21 DAYS",
        "OF SHIPMENT DATE BUT WITHIN LC VALIDITY",
        "PARTIAL SHIPMENT PROHIBITED",
        "ALL BANK CHARGES OUTSIDE UAE FOR",
        "BENEFICIARY ACCOUNT",
      ],
    },
  ],
  parties: [
    { label: ":50: APPLICANT", value: "AL-FUTTAIM TEXTILES LLC, DUBAI, UAE" },
    { label: ":59: BENEFICIARY", value: "GLOBAL TEXTILES PVT LTD, COIMBATORE, INDIA" },
    { label: "ADVISING BANK", value: "STATE BANK OF INDIA, COIMBATORE" },
  ] as FieldRow[],
  signature: "Authenticated SWIFT message · Emirates NBD trade services",
  stamp: ["EMIRATES NBD", "TRADE SERVICES"],
};
