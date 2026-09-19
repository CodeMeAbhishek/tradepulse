"use client";

import { useRef } from "react";
import { Label } from "@/components/ui/Label";
import { HERO, LINKS } from "@/content/site";
import { gsap, useGSAP, MQ } from "@/lib/gsap";

/**
 * Four panels, four column positions.
 *
 * The headline occupies two thirds of the width; the standfirst sits in an ink
 * panel starting at column nine; the comparison and the action each hold their
 * own cell. Nothing is centred and nothing floats — the panels meet edge to
 * edge and the rules between them come from their own borders.
 */
export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { compare } = HERO;

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(MQ.motion, () => {
        gsap
          .timeline({ defaults: { ease: "power3.out" } })
          .from("[data-panel]", { opacity: 0, duration: 0.5, stagger: 0.09 })
          .from("[data-value]", { yPercent: 40, opacity: 0, duration: 0.7, stagger: 0.12 }, "-=0.2")
          .from("[data-mark]", { scale: 0, duration: 0.4, ease: "back.out(2.2)" }, "-=0.15");
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} id="top" className="border-b border-rule">
      <div className="grid-page border-b border-rule">
        <div data-panel className="panel col-span-4 flex items-end lg:col-span-8 lg:min-h-[58svh]">
          <h1 className="type-display text-[clamp(2.75rem,7.6vw,7.5rem)]">{HERO.headline}</h1>
        </div>

        <div
          data-panel
          className="panel col-span-4 flex flex-col justify-between gap-10 border-t border-rule bg-ink text-on-ink lg:col-span-4 lg:border-t-0 lg:border-l"
        >
          <Label tone="onInk">{HERO.kicker}</Label>
          <p className="type-body max-w-[26ch] text-mute-on-ink">
            <span className="text-on-ink">{HERO.bodyLead}</span> {HERO.bodyRest}
          </p>
        </div>
      </div>

      <div className="grid-page">
        <figure data-panel className="panel col-span-4 bg-paper-2 lg:col-span-8">
          <div className="flex items-baseline justify-between">
            <Label>{compare.ref}</Label>
            <span className="type-label text-mute">{compare.field}</span>
          </div>

          <div className="relative mt-10 grid grid-cols-2 lg:mt-14">
            <div aria-hidden className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-rule" />
            <div
              data-mark
              aria-hidden
              className="absolute top-1/2 left-1/2 z-10 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rotate-45 bg-signal"
              style={{ boxShadow: "0 0 0 7px var(--p-paper-2)" }}
            />
            {[compare.left, compare.right].map((side, i) => (
              <div key={side.doc} className={i === 0 ? "pr-8 text-right lg:pr-16" : "pl-8 lg:pl-16"}>
                <p className="type-label min-h-[2.4em] text-mute">{side.doc}</p>
                <p data-value className="type-display type-data mt-3 text-[clamp(3rem,9vw,7rem)]">
                  {side.value}
                </p>
                <p className="type-label mt-3 text-mute">{side.unit}</p>
              </div>
            ))}
          </div>

          <figcaption className="type-body mt-10 max-w-[32ch] lg:mt-14">{compare.verdict}</figcaption>
        </figure>

        <div data-panel className="col-span-4 flex flex-col border-t border-rule lg:col-span-4 lg:border-t-0 lg:border-l">
          <a
            href={LINKS.reviewDesk}
            target="_blank"
            rel="noreferrer"
            className="group panel flex flex-1 flex-col justify-between gap-10 bg-signal text-on-signal transition-[filter] duration-200 hover:brightness-110"
          >
            <Label tone="onInk" className="!text-on-signal">
              Live demo
            </Label>
            <span className="flex items-end justify-between gap-6">
              <span className="type-display text-[clamp(1.75rem,3vw,2.75rem)]">{HERO.primary}</span>
              <svg viewBox="0 0 22 12" aria-hidden className="mb-2 h-4 w-7 shrink-0" fill="none">
                <path
                  d="M0 6h20M15 1l5 5-5 5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="square"
                  className="transition-transform duration-200 group-hover:translate-x-1.5"
                />
              </svg>
            </span>
          </a>
          <p className="panel type-label border-t border-rule leading-[1.7] text-mute">
            {HERO.residency}
          </p>
        </div>
      </div>
    </section>
  );
}
