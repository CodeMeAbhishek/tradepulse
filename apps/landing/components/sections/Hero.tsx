"use client";

import { useRef } from "react";
import { Label } from "@/components/ui/Label";
import { Pallet } from "@/components/hero/Pallet";
import { HERO, LINKS } from "@/content/site";
import { gsap, useGSAP, Draggable, MQ } from "@/lib/gsap";

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

        // One scrubbed timeline so every beat stays in lockstep with the
        // reader: cartons land bottom row first, the shelf draws under them,
        // the figures count up as their pallet fills, then the three empty
        // slots appear and the exception mark strikes. Scrubbed rather than
        // fired once — the stacking follows the scroll rather than happening
        // whether anyone is looking or not.
        const cartons = gsap.utils.toArray<HTMLElement>("[data-fall]");
        cartons.sort((a, b) => Number(a.dataset.order) - Number(b.dataset.order));

        // Start and end are anchored to different things on purpose.
        //
        // Start at the document top, because on most screens the readout is
        // already partly visible on arrival — a "scroll into view" trigger
        // would begin part-way along and the cartons would be half-placed
        // before the reader had scrolled at all.
        //
        // End when the pallet reaches the middle of the screen, so the last
        // carton lands as the thing you are looking at arrives where you are
        // looking. A fixed pixel runway cannot do that: it finishes too late
        // on a short window and too early on a tall one.
        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: root.current,
            start: "top top",
            endTrigger: "[data-pallet]",
            end: "center center",
            scrub: 0.5,
          },
        });

        tl.from(
          cartons,
          {
            y: -120,
            rotate: () => gsap.utils.random(-14, 14),
            opacity: 0,
            ease: "back.out(1.1)",
            stagger: 0.05,
            duration: 0.5,
          },
          0
        );

        tl.from("[data-shelf]", { scaleX: 0, opacity: 0, duration: 0.5, ease: "power2.out" }, 0);

        tl.from("[data-seam]", { scaleY: 0, duration: 0.6, ease: "power2.out" }, 0);

        // The gaps arrive last: they are the point being made.
        tl.from(
          "[data-ghost]",
          { opacity: 0, scale: 0.86, ease: "power2.out", stagger: 0.07, duration: 0.3 },
          0.62
        );

        tl.fromTo(
          "[data-mark]",
          { scale: 1 },
          { scale: 1.75, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.inOut" },
          0.85
        );

        tl.from("[data-verdict]", { opacity: 0, y: 12, duration: 0.3, ease: "power2.out" }, 0.88);

      });

      // Cartons can be picked up, thrown, and left wherever they land —
      // but only within their own document's half of the panel. A carton from
      // the invoice cannot end up on the bill of lading, because the whole
      // point is that these are two separate records being compared.
      //
      // They keep the position you leave them in; double-click sends one home.
      mm.add(MQ.drag, () => {
        const made = (["left", "right"] as const).flatMap((sideName) =>
          Draggable.create(`[data-side="${sideName}"] [data-carton]`, {
            type: "x,y",
            bounds: `[data-bounds="${sideName}"]`,
            inertia: true,
            allowContextMenu: true,
            // The held state is a CSS class, not a tween. Any GSAP tween on
            // the drag target rewrites its transform matrix and wipes the
            // drag offset, which is the trap this whole layering avoids.
            onPress() {
              this.target.classList.add("is-held");
              this.target.style.zIndex = "20";
            },
            onRelease() {
              this.target.classList.remove("is-held");
            },
          })
        );

        const home = (e: Event) => {
          const el = (e.currentTarget as HTMLElement) ?? null;
          if (el) gsap.to(el, { x: 0, y: 0, rotate: 0, duration: 0.6, ease: "power3.out" });
        };
        const grabs = gsap.utils.toArray<HTMLElement>("[data-carton]");
        grabs.forEach((el) => el.addEventListener("dblclick", home));

        return () => {
          made.forEach((d) => d.kill());
          grabs.forEach((el) => {
            el.removeEventListener("dblclick", home);
            el.classList.remove("is-held");
            el.style.zIndex = "";
            gsap.set(el, { x: 0, y: 0, rotate: 0 });
          });
        };
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
        <figure data-panel data-readout className="panel relative col-span-4 bg-paper-2 lg:col-span-8">
          {/* Drag areas: a carton belongs to its document and cannot cross the
              seam into the other one. Invisible, and never in the way of a
              pointer — they exist so Draggable has a rectangle to clamp to. */}
          <div data-bounds="left" aria-hidden className="pointer-events-none absolute inset-y-0 left-0 w-1/2" />
          <div data-bounds="right" aria-hidden className="pointer-events-none absolute inset-y-0 right-0 w-1/2" />

          <div className="flex items-baseline justify-between">
            <Label>{compare.ref}</Label>
            <span className="type-label text-mute">{compare.field}</span>
          </div>

          <div className="relative mt-10 grid grid-cols-2 lg:mt-14">
            <div
              data-seam
              aria-hidden
              className="absolute inset-y-0 left-1/2 w-px origin-top -translate-x-1/2 bg-rule"
            />
            <div
              data-mark
              aria-hidden
              className="absolute top-1/2 left-1/2 z-10 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rotate-45 bg-signal"
              style={{ boxShadow: "0 0 0 7px var(--p-paper-2)" }}
            />
            {[compare.left, compare.right].map((side, i) => (
              <div
                key={side.doc}
                data-side={i === 0 ? "left" : "right"}
                className={i === 0 ? "pr-8 text-right lg:pr-16" : "pl-8 lg:pl-16"}
              >
                <p className="type-label min-h-[2.4em] text-mute">{side.doc}</p>
                <p
                  data-value
                  className="type-display type-data mt-3 text-[clamp(3rem,9vw,7rem)] tabular"
                >
                  {side.value}
                </p>
                <p className="type-label mt-3 text-mute">{side.unit}</p>
                <Pallet filled={i === 0 ? 10 : 7} align={i === 0 ? "right" : "left"} />
              </div>
            ))}
          </div>

          <figcaption data-verdict className="type-body mt-10 max-w-[32ch] lg:mt-14">
            {compare.verdict}
          </figcaption>
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
