import { createFileRoute } from "@tanstack/react-router";
import { motion } from "motion/react";

import { Section } from "@/components/shell/Section";
import { Eyebrow } from "@/components/kit/Eyebrow";
import { SectionHeading } from "@/components/kit/SectionHeading";
import { InlineCitation } from "@/components/kit/InlineCitation";
import { QuietButton, QuietLink } from "@/components/kit/QuietButton";
import { ExaminationBench } from "@/components/bench/ExaminationBench";
import { site } from "@/content/site";
import { boundary, closing, hero, methodSteps, problem } from "@/content/home";
import { DUR, EASE, STAGGER_LINE, reveal } from "@/lib/motion";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TradePulse AI — verification middleware for trade finance" },
      {
        name: "description",
        content:
          "TradePulse examines a cross-border trade document set against UCP 600 and unit-value bands in under 30 seconds, and returns a scored exception report with every finding traced to its source.",
      },
      {
        property: "og:title",
        content: "TradePulse AI — verification middleware for trade finance",
      },
      {
        property: "og:description",
        content:
          "The model extracts. Code decides. A scored exception report with every finding traced to its document, page and field.",
      },
    ],
  }),
  component: HomePage,
});

function HomePage() {
  return (
    <>
      {/* 01 — HERO */}
      <Section number="01" name="HERO" className="pt-[104px] pb-[88px] lg:pt-[128px]">
        <Eyebrow>{hero.eyebrow}</Eyebrow>

        <div className="ledger-grid mt-8">
          <h1 className="text-h2 col-span-12 font-mono text-ink sm:text-h1 lg:col-span-7 lg:text-display">
            {hero.lines.map((line, i) => (
              <motion.span
                key={line}
                className="block"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: DUR.ruleDraw,
                  ease: EASE.out,
                  delay: 0.08 + i * STAGGER_LINE,
                }}
              >
                {line}
              </motion.span>
            ))}
          </h1>

          <div className="col-span-12 mt-10 lg:col-span-4 lg:col-start-9 lg:mt-2">
            <p className="text-body max-w-[52ch] text-slate">{hero.body}</p>
            <div className="mt-9 flex flex-wrap items-center gap-6">
              <QuietButton
                onClick={() => {
                  document
                    .getElementById("bench")
                    ?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
              >
                {hero.actions.primary}
              </QuietButton>
              <QuietLink to="/method">{hero.actions.secondary}</QuietLink>
            </div>
          </div>
        </div>

        {/* the problem, compressed to three figures on one paper plane */}
        <div className="mt-[104px] border border-rule bg-paper">
          <div className="grid divide-y divide-rule md:grid-cols-3 md:divide-x md:divide-y-0">
            {problem.rows.map((row) => (
              <motion.div key={row.figure} {...reveal} className="p-8">
                <p className="text-h2 font-mono text-ink">{row.figure}</p>
                <p className="text-label mt-4 max-w-[26ch] text-slate">{row.heading}</p>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="mt-5">
          <InlineCitation>{problem.rows[0]?.citation}</InlineCitation>
        </div>

        {/* the five accepted types, on one hairline */}
        <div className="hairline-t hairline-b mt-14 flex flex-wrap gap-x-10 gap-y-3 py-5">
          {site.documentTypes.map((t) => (
            <span key={t} className="text-label text-slate">
              {t}
            </span>
          ))}
        </div>
      </Section>

      {/* 02 — THE BENCH */}
      <Section number="02" name="THE BENCH" id="bench" className="bg-bench pt-0">
        <div className="ledger-grid">
          <div className="col-span-12 lg:col-span-4">
            <SectionHeading eyebrow="THE EXAMINATION BENCH">
              One document set, examined in front of you.
            </SectionHeading>
          </div>
          <p className="text-body col-span-12 mt-6 max-w-[58ch] text-slate lg:col-span-6 lg:col-start-6 lg:mt-0">
            Load the sample set. Four agents read it in sequence, and each finding names the
            document, the page and the field it came from. Select a finding and the document moves
            to the region it cites.
          </p>
        </div>

        <div className="mt-14">
          <ExaminationBench />
        </div>
      </Section>

      {/* 03 — METHOD */}
      <Section number="03" name="METHOD">
        <div className="ledger-grid">
          <div className="col-span-12 lg:col-span-4">
            <SectionHeading eyebrow="METHOD">Four steps, in order.</SectionHeading>
          </div>

          <div className="col-span-12 mt-10 lg:col-span-7 lg:col-start-6 lg:mt-0">
            <div className="border border-rule bg-paper">
              {methodSteps.map((step) => (
                <motion.div
                  key={step.number}
                  {...reveal}
                  className="flex gap-6 border-b border-rule p-8 last:border-b-0"
                >
                  <p className="text-data shrink-0 text-slate">{step.number}</p>
                  <div>
                    <h3 className="text-h3 font-mono text-ink">{step.title}</h3>
                    <p className="text-small mt-3 max-w-[58ch] text-slate">{step.body}</p>
                    <p className="text-label mt-5 text-ink">EMITS · {step.emits}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* 04 — BOUNDARY */}
      <Section number="04" name="BOUNDARY" className="bg-ink">
        <Eyebrow tone="paper">THE BOUNDARY</Eyebrow>
        <h2 className="text-h1 mt-6 max-w-[30ch] font-mono text-paper">Where the model stops.</h2>

        <div className="ledger-grid mt-16 gap-y-12">
          <div className="col-span-12 lg:col-span-5">
            <p className="text-label text-rule">THE MODEL</p>
            <ul className="mt-6 border-t border-slate">
              {boundary.model.map((item) => (
                <li key={item} className="text-body border-b border-slate py-4 text-rule">
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="col-span-12 lg:col-span-5 lg:col-start-8">
            <p className="text-label text-rule">THE CODE</p>
            <ul className="mt-6 border-t border-slate">
              {boundary.code.map((item) => (
                <li key={item} className="text-body border-b border-slate py-4 text-paper">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <p className="text-h3 mt-16 max-w-[46ch] font-mono text-paper">{boundary.line}</p>
      </Section>

      {/* 05 — CLOSING */}
      <Section number="05" name="CLOSING" className="py-[112px]">
        <div className="ledger-grid items-end">
          <h2 className="text-h1 col-span-12 max-w-[26ch] font-mono text-ink lg:col-span-6">
            {closing.heading}
          </h2>
          <div className="col-span-12 mt-10 flex flex-wrap gap-6 lg:col-span-5 lg:col-start-8 lg:mt-0">
            <QuietLink to="/product" variant="solid">
              {closing.action}
            </QuietLink>
            <QuietLink to="/method">Read the technical note</QuietLink>
          </div>
        </div>
      </Section>
    </>
  );
}
