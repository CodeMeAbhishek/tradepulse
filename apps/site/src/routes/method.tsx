import { createFileRoute } from "@tanstack/react-router";

import { Section } from "@/components/shell/Section";
import { Eyebrow } from "@/components/kit/Eyebrow";
import { SectionHeading } from "@/components/kit/SectionHeading";
import { RuleDivider } from "@/components/kit/RuleDivider";
import { DataTable } from "@/components/kit/DataTable";
import { QuietLink } from "@/components/kit/QuietButton";
import { PipelineDiagram } from "@/components/method/PipelineDiagram";
import { boundaryDetail, methodHero, notDoing, priceBands, ucpChecks } from "@/content/method";

export const Route = createFileRoute("/method")({
  head: () => ({
    meta: [
      { title: "Method — how a finding is proved | TradePulse AI" },
      {
        name: "description",
        content:
          "A technical note on the boundary between extraction and decision: UCP 600 checks written as code, unit-value bands derived from reported trade, and severity from a static table.",
      },
      { property: "og:title", content: "Method — how a finding is proved | TradePulse AI" },
      {
        property: "og:description",
        content:
          "The model extracts. Code decides. Written for the people who have to defend the output.",
      },
    ],
  }),
  component: MethodPage,
});

function MethodPage() {
  return (
    <>
      <Section number="01" name="ARCHITECTURE" className="pt-[120px] lg:pt-[160px]">
        <Eyebrow>{methodHero.eyebrow}</Eyebrow>
        <h1 className="text-h1 mt-8 max-w-[26ch] font-mono text-ink">{methodHero.heading}</h1>
        <div className="ledger-grid mt-14">
          <div className="col-span-12 flex flex-col gap-6 lg:col-span-6 lg:col-start-6">
            {methodHero.body.map((p) => (
              <p key={p.slice(0, 24)} className="text-body max-w-[62ch] text-slate">
                {p}
              </p>
            ))}
          </div>
        </div>
        <div className="mt-[120px]">
          <PipelineDiagram />
        </div>
      </Section>

      <Section number="02" name="THE BOUNDARY" className="pt-0">
        <SectionHeading eyebrow="THE BOUNDARY">What is asked, and what is decided.</SectionHeading>
        <div className="mt-[96px] flex flex-col">
          {boundaryDetail.map((item) => (
            <div key={item.heading} className="hairline-t ledger-grid py-12">
              <h3 className="text-h3 col-span-12 font-mono text-ink lg:col-span-4">
                {item.heading}
              </h3>
              <p className="text-body col-span-12 mt-6 max-w-[62ch] text-slate lg:col-span-6 lg:col-start-6 lg:mt-0">
                {item.body}
              </p>
            </div>
          ))}
          <RuleDivider />
        </div>
      </Section>

      <Section number="03" name="UCP 600" className="bg-bench">
        <SectionHeading eyebrow="UCP 600">The articles written as code.</SectionHeading>
        <DataTable className="mt-[96px]" headers={ucpChecks.headers} rows={ucpChecks.rows} />
        <p className="text-small mt-8 max-w-[62ch] text-slate">
          Articles not listed here are not checked. They are absent from the report rather than
          implied by it.
        </p>
      </Section>

      <Section number="04" name="PRICE BANDS">
        <SectionHeading eyebrow="REFERENCE DATA">{priceBands.heading}</SectionHeading>
        <div className="ledger-grid mt-[96px] gap-y-12">
          <div className="col-span-12 flex flex-col gap-6 lg:col-span-5">
            {priceBands.body.map((p) => (
              <p key={p.slice(0, 24)} className="text-body max-w-[62ch] text-slate">
                {p}
              </p>
            ))}
          </div>
          <div className="col-span-12 lg:col-span-6 lg:col-start-7">
            <p className="text-label text-slate">THE DERIVATION</p>
            <pre className="text-data mt-6 overflow-x-auto border border-rule bg-paper p-6 text-ink">
              {priceBands.arithmetic.join("\n")}
            </pre>
          </div>
        </div>
      </Section>

      <Section number="05" name="BOUNDARIES" className="bg-ink">
        <Eyebrow tone="paper">WHAT WE DO NOT DO</Eyebrow>
        <h2 className="text-h1 mt-6 max-w-[26ch] font-mono text-paper">Four things we decline.</h2>
        <div className="ledger-grid mt-[96px] gap-y-10">
          {notDoing.map((item) => (
            <div
              key={item.heading}
              className="col-span-12 border-t border-slate pt-6 md:col-span-6"
            >
              <h3 className="text-h3 font-mono text-paper">{item.heading}</h3>
              <p className="text-small mt-5 max-w-[58ch] text-rule">{item.body}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section number="06" name="CLOSING" className="pb-[120px]">
        <RuleDivider tone="ink" />
        <h2 className="text-h1 mt-14 max-w-[30ch] font-mono text-ink">
          Read the rules, then watch them run.
        </h2>
        <div className="mt-12 flex flex-wrap gap-8">
          <QuietLink to="/product" variant="solid">
            See the bench
          </QuietLink>
        </div>
      </Section>
    </>
  );
}
