import { FINAL_CTA, LINKS } from "@/content/site";

/** A signal-coloured block running the full width, at the largest type here. */
export function FinalCta() {
  return (
    <section className="grid-page border-b border-rule-on-ink bg-signal text-on-signal">
      <div className="panel col-span-4 lg:col-span-8">
        <h2 className="type-display max-w-[12ch] text-[clamp(2.5rem,6.6vw,6rem)]">
          {FINAL_CTA.title}
        </h2>
        <p className="type-label mt-10 max-w-[44ch] leading-[1.7] text-on-signal">
          {FINAL_CTA.fine}
        </p>
      </div>
      <a
        href={LINKS.reviewDesk}
        target="_blank"
        rel="noreferrer"
        className="group panel col-span-4 flex items-end justify-between gap-6 border-t border-on-signal/25 bg-ink text-on-ink transition-colors duration-200 hover:bg-ink-2 lg:col-span-4 lg:border-t-0 lg:border-l"
      >
        <span className="type-display text-[clamp(1.75rem,3vw,2.75rem)]">{FINAL_CTA.primary}</span>
        <svg viewBox="0 0 22 12" aria-hidden className="mb-2 h-4 w-7 shrink-0" fill="none">
          <path
            d="M0 6h20M15 1l5 5-5 5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="square"
            className="transition-transform duration-200 group-hover:translate-x-1.5"
          />
        </svg>
      </a>
    </section>
  );
}
