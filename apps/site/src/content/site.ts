export const site = {
  name: "TRADEPULSE",
  mark: "✺",
  nav: [
    { label: "The bench", to: "/product" },
    { label: "Method", to: "/method" },
    { label: "Workbench", to: "/workbench" },
  ],
  action: { label: "See a live examination", to: "/product" },
  documentTypes: [
    "COMMERCIAL INVOICE",
    "BILL OF LADING",
    "PACKING LIST",
    "CERTIFICATE OF ORIGIN",
    "LETTER OF CREDIT (MT700)",
  ],
  footer: {
    line: "Every finding names its document, its page, and its field.",
    columns: [
      {
        header: "PRODUCT",
        links: [
          { label: "The examination bench", to: "/product" },
          { label: "The four agents", to: "/product" },
          { label: "One finding, fully traced", to: "/product" },
        ],
      },
      {
        header: "METHOD",
        links: [
          { label: "Architecture", to: "/method" },
          { label: "UCP 600 checks", to: "/method" },
          { label: "Price bands", to: "/method" },
        ],
      },
      {
        header: "COMPANY",
        links: [
          { label: "See a live examination", to: "/product" },
          { label: "The model/code boundary", to: "/method" },
          { label: "What we do not do", to: "/method" },
        ],
      },
    ],
    place: "GIFT IFSC · AHMEDABAD",
    corridor: "IN→AE CORRIDOR LIVE · SG, UK, US IN DEVELOPMENT",
  },
} as const;

export const sections = [
  { number: "01", name: "HERO" },
  { number: "02", name: "THE PROBLEM" },
  { number: "03", name: "THE BENCH" },
  { number: "04", name: "METHOD" },
  { number: "05", name: "BOUNDARY" },
  { number: "06", name: "THE NUMBERS" },
  { number: "07", name: "USE CASES" },
  { number: "08", name: "FAQ" },
  { number: "09", name: "CLOSING" },
] as const;
