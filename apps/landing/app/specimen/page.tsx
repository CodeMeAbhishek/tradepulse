import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Specimen — TradePulse typography",
  robots: { index: false, follow: false },
};

/**
 * TEMPORARY. Three type pairings rendered on the real hero, stat row, compare
 * table and paragraph, so the choice is made from actual rendering rather than
 * from a description. Deleted once a pairing is picked.
 */

type Pairing = {
  key: string;
  name: string;
  note: string;
  display: string;
  body: string;
  displayWeight: number;
  /** Zodiak is a serif, so it wants slightly tighter tracking than the sans. */
  tracking: string;
};

const PAIRINGS: Pairing[] = [
  {
    key: "A",
    name: "Zodiak · Switzer · Fragment Mono",
    note: "Serif headline. The register of a bank or a broadsheet — recommended.",
    display: "var(--font-zodiak)",
    body: "var(--font-switzer)",
    displayWeight: 700,
    tracking: "-0.02em",
  },
  {
    key: "B",
    name: "Switzer · Switzer · Fragment Mono",
    note: "One family throughout, weight carrying the hierarchy. Quiet and Swiss.",
    display: "var(--font-switzer)",
    body: "var(--font-switzer)",
    displayWeight: 700,
    tracking: "-0.03em",
  },
  {
    key: "C",
    name: "Cabinet Grotesk · Switzer · Fragment Mono",
    note: "Grotesk headline with a little more character. Leans startup.",
    display: "var(--font-cabinet)",
    body: "var(--font-switzer)",
    displayWeight: 700,
    tracking: "-0.025em",
  },
];

const ROWS: [string, string, string, "match" | "mismatch"][] = [
  ["Goods description", "Copper cathodes Grade A", "Copper cathodes Grade A", "match"],
  ["Quantity", "500", "350", "mismatch"],
  ["Unit", "cartons", "cartons", "match"],
  ["Port of loading", "Mundra, IN", "Mundra, IN", "match"],
];

const FIGURES: [string, string, string][] = [
  ["USD 106 bn", "Banking assets at GIFT IFSC", "December 2025"],
  ["7.5×", "Growth in five years", "Sept 2020 – Dec 2025"],
  ["37", "Banks operating there", "December 2025"],
];

function Block({ p }: { p: Pairing }) {
  return (
    <section
      style={{ fontFamily: `${p.body}, system-ui, sans-serif` }}
      className="border-t border-rule py-16"
    >
      <header className="mb-10 flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="type-label flex h-7 w-7 items-center justify-center bg-ink text-white">
          {p.key}
        </span>
        <h2 className="text-lg font-semibold">{p.name}</h2>
        <p className="text-sm text-ink-muted">{p.note}</p>
      </header>

      {/* Hero */}
      <p className="type-label text-ink-muted">For bank &amp; GIFT IFSC trade desks</p>
      <h3
        style={{
          fontFamily: `${p.display}, Georgia, serif`,
          fontWeight: p.displayWeight,
          letterSpacing: p.tracking,
        }}
        className="mt-5 max-w-[18ch] text-[clamp(2.5rem,6vw,4.75rem)] leading-[0.98]"
      >
        Two documents. One number that doesn&rsquo;t match.
      </h3>
      <p className="mt-6 max-w-[54ch] text-lg leading-relaxed text-ink-muted">
        TradePulse reads every field, surfaces the discrepancies with evidence, and hands your
        officer a case they can defend.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        <span className="inline-flex min-h-11 items-center bg-navy px-5 font-medium text-white">
          Open a reviewed case
        </span>
        <span className="inline-flex min-h-11 items-center border border-rule-strong px-5 font-medium">
          How it works
        </span>
      </div>

      {/* Figures */}
      <div className="mt-14 grid gap-8 border-y border-rule py-8 sm:grid-cols-3">
        {FIGURES.map(([fig, label, period]) => (
          <div key={label}>
            <p
              style={{ fontFamily: `${p.display}, Georgia, serif`, fontWeight: p.displayWeight }}
              className="tabular text-[clamp(2rem,4vw,3rem)] leading-none"
            >
              {fig}
            </p>
            <p className="mt-3 font-medium">{label}</p>
            <p className="type-label mt-1.5 text-ink-muted">{period}</p>
          </div>
        ))}
      </div>

      {/* Compare table */}
      <div className="mt-12 overflow-hidden border border-rule bg-card">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-rule">
              {["Field", "Invoice", "Bill of lading", "Status"].map((h) => (
                <th key={h} className="type-label px-4 py-3 font-normal text-ink-muted">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(([field, a, b, status]) => (
              <tr key={field} className="border-b border-rule last:border-0">
                <td className="px-4 py-3 font-medium">{field}</td>
                <td className="tabular px-4 py-3 font-mono text-ink-muted">{a}</td>
                <td className="tabular px-4 py-3 font-mono text-ink-muted">{b}</td>
                <td className="px-4 py-3">
                  {status === "match" ? (
                    <span className="type-label inline-flex items-center gap-1.5 text-verified">
                      <span className="h-1.5 w-1.5 bg-current" />
                      Match
                    </span>
                  ) : (
                    <span className="type-label inline-flex items-center gap-1.5 text-mismatch">
                      <span
                        className="h-1.5 w-1.5 bg-current"
                        style={{ clipPath: "polygon(0 0, 100% 0, 0 100%)" }}
                      />
                      Mismatch
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paragraph */}
      <p className="mt-12 max-w-[68ch] leading-relaxed text-ink-muted">
        A similar name is a lead, not proof. TradePulse places every counterparty on a four-rung
        identity ladder, from a name printed on a document up to a matched Legal Entity Identifier.
        Missing information stays open and is never converted into a pass, and every finding carries
        the document, page, field and rule it came from.
      </p>
    </section>
  );
}

export default function SpecimenPage() {
  return (
    <main className="shell py-16">
      <h1 className="text-3xl font-semibold">Typography specimen</h1>
      <p className="mt-3 max-w-[60ch] text-ink-muted">
        Three pairings on the real content. All families are free for commercial use and
        self-hosted. Pick one and the other two get deleted.
      </p>
      {PAIRINGS.map((p) => (
        <Block key={p.key} p={p} />
      ))}
    </main>
  );
}
