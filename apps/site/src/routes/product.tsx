import { createFileRoute } from "@tanstack/react-router";

import { Section } from "@/components/shell/Section";
import { Eyebrow } from "@/components/kit/Eyebrow";
import { SectionHeading } from "@/components/kit/SectionHeading";
import { RuleDivider } from "@/components/kit/RuleDivider";
import { DataTable } from "@/components/kit/DataTable";
import { QuietLink } from "@/components/kit/QuietButton";
import { ExaminationBench } from "@/components/bench/ExaminationBench";
import { agents, productHero, screenRegions, tracedFinding } from "@/content/product";

export const Route = createFileRoute("/product")({
  head: () => ({
    meta: [
      { title: "The examination bench — TradePulse AI" },
      {
        name: "description",
        content:
          "The document set stays on screen at full size while findings sit beside it. Four agents, each finding traced to a page, a field, and a UCP 600 article or price band.",
      },
      { property: "og:title", content: "The examination bench — TradePulse AI" },
      {
        property: "og:description",
        content:
          "A working surface, not a dashboard. Every finding links back into the page and field it came from.",
      },
    ],
  }),
  component: ProductPage,
});

function ProductPage() {
  return (
    <>
      <Section number="01" name="THE BENCH" className="pt-[120px] lg:pt-[160px]">
        <Eyebrow>{productHero.eyebrow}</Eyebrow>
        <h1 className="text-h1 mt-8 max-w-[30ch] font-mono text-ink">{productHero.heading}</h1>
        <div className="ledger-grid mt-14">
          <div className="col-span-12 flex flex-col gap-6 lg:col-span-6 lg:col-start-6">
            {productHero.body.map((p) => (
              <p key={p.slice(0, 24)} className="text-body max-w-[62ch] text-slate">
                {p}
              </p>
            ))}
          </div>
        </div>

        <div className="mt-[96px]">
          <ExaminationBench />
        </div>
      </Section>

      <Section number="02" name="THE SCREEN" className="bg-bench">
        <SectionHeading eyebrow="THE SCREEN">Six regions, nothing else.</SectionHeading>
        <DataTable
          className="mt-[96px]"
          headers={screenRegions.headers}
          rows={screenRegions.rows}
        />
      </Section>

      <Section number="03" name="THE AGENTS">
        <SectionHeading eyebrow="THE AGENTS">
          Four processes, and what each may not decide.
        </SectionHeading>
        <DataTable className="mt-[96px]" headers={agents.headers} rows={agents.rows} />
      </Section>

      <Section number="04" name="ONE FINDING" className="bg-bench">
        <SectionHeading eyebrow="TRACEABILITY">{tracedFinding.heading}</SectionHeading>

        <div className="ledger-grid mt-[96px] gap-y-12">
          <div className="col-span-12 lg:col-span-5">
            <dl className="border-t border-rule">
              {tracedFinding.rows.map(([k, v]) => (
                <div key={k} className="flex justify-between gap-6 border-b border-rule py-4">
                  <dt className="text-label text-slate">{k}</dt>
                  <dd className="text-data text-right text-ink">{v}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="col-span-12 lg:col-span-6 lg:col-start-7">
            <p className="text-label text-slate">THE ARITHMETIC</p>
            <pre className="text-data mt-6 overflow-x-auto border border-rule bg-paper p-6 text-ink">
              {tracedFinding.arithmetic.join("\n")}
            </pre>
            <p className="text-small mt-6 max-w-[58ch] text-slate">{tracedFinding.note}</p>
          </div>
        </div>
      </Section>

      <Section number="05" name="CLOSING" className="pb-[120px]">
        <RuleDivider tone="ink" />
        <h2 className="text-h1 mt-14 max-w-[30ch] font-mono text-ink">
          Bring a presentation. We will examine it with you.
        </h2>
        <div className="mt-12 flex flex-wrap gap-8">
          <QuietLink to="/method" variant="solid">
            Read the technical note
          </QuietLink>
        </div>
      </Section>
    </>
  );
}
