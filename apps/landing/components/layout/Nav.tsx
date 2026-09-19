"use client";

import { useEffect, useRef, useState } from "react";
import { BrandMark } from "@/components/brand/BrandMark";
import { HERO, LINKS, NAV } from "@/content/site";
import { getLenis } from "@/lib/lenis";

/**
 * A bar divided into cells by rules, not a floating row of links.
 *
 * The clock is real: trade desks work across corridors, and GIFT City time is
 * the timezone the demo runs in. It is the sort of detail that says a person
 * built this, and it costs one interval.
 *
 * Mobile sheet behaviour, all of it learned the hard way:
 * - Rendered as a sibling of <header>, not inside it: the header's
 *   backdrop-filter makes it the containing block for fixed children.
 * - Scrolling is paused through Lenis; body overflow alone does not stop it.
 * - Focus moves into the sheet and back to the button; Escape closes it.
 */
export function Nav() {
  const [open, setOpen] = useState(false);
  const [time, setTime] = useState<string | null>(null);
  const toggle = useRef<HTMLButtonElement>(null);
  const firstLink = useRef<HTMLAnchorElement>(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    const tick = () =>
      setTime(
        new Intl.DateTimeFormat("en-GB", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
          timeZone: "Asia/Kolkata",
        }).format(new Date())
      );
    tick();
    const id = setInterval(tick, 30_000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!open) {
      if (wasOpen.current) toggle.current?.focus();
      wasOpen.current = false;
      return;
    }
    wasOpen.current = true;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    getLenis()?.stop();
    firstLink.current?.focus();
    const mq = window.matchMedia("(min-width: 1024px)");
    const onMq = () => mq.matches && setOpen(false);
    mq.addEventListener("change", onMq);
    return () => {
      document.removeEventListener("keydown", onKey);
      mq.removeEventListener("change", onMq);
      document.body.style.overflow = "";
      getLenis()?.start();
    };
  }, [open]);

  const navigate = () => {
    getLenis()?.start();
    document.body.style.overflow = "";
    wasOpen.current = false;
    setOpen(false);
  };

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-rule bg-paper">
        <div className="grid-page">
          <a
            href="#top"
            className="col-span-2 flex min-h-14 items-center gap-2.5 px-5 lg:col-span-3 lg:px-8"
            aria-label="TradePulse, back to top"
          >
            <BrandMark className="h-6 w-6" tone="original" title="" />
            <span className="type-display text-lg">TradePulse</span>
          </a>

          <p className="type-label col-span-3 hidden items-center border-l border-rule px-8 text-mute lg:flex">
            <span className="tabular">{time ?? "--:--"}</span>
            <span className="ml-2">GIFT IFSC</span>
          </p>

          <nav aria-label="Primary" className="col-span-4 hidden items-center gap-8 border-l border-rule px-8 lg:flex">
            {NAV.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="type-label py-2 text-mute transition-colors duration-200 hover:text-ink"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <a
            href={LINKS.reviewDesk}
            target="_blank"
            rel="noreferrer"
            className="group col-span-2 hidden min-h-14 items-center justify-between gap-4 border-l border-rule bg-ink px-6 text-on-ink transition-colors duration-200 hover:bg-signal hover:text-on-signal lg:flex"
          >
            <span className="type-label">Open desk</span>
            <svg viewBox="0 0 22 12" aria-hidden className="h-3 w-5 shrink-0" fill="none">
              <path
                d="M0 6h20M15 1l5 5-5 5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="square"
                className="transition-transform duration-200 group-hover:translate-x-1"
              />
            </svg>
          </a>

          <button
            ref={toggle}
            type="button"
            className="type-label col-span-2 col-start-3 flex min-h-14 items-center justify-center border-l border-rule px-5 lg:hidden"
            aria-expanded={open}
            aria-controls="mobile-menu"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? "Close" : "Menu"}
          </button>
        </div>
      </header>

      {open && (
        <div id="mobile-menu" className="fixed inset-x-0 top-14 bottom-0 z-40 overflow-y-auto bg-paper lg:hidden">
          <nav aria-label="Mobile" className="flex min-h-full flex-col">
            {NAV.map((item) => (
              <a
                key={item.href}
                ref={item.href === NAV[0].href ? firstLink : undefined}
                href={item.href}
                onClick={navigate}
                className="border-b border-rule px-5 py-7"
              >
                <span className="type-display text-4xl">{item.label}</span>
              </a>
            ))}
            <a
              href={LINKS.reviewDesk}
              target="_blank"
              rel="noreferrer"
              className="mt-auto flex min-h-16 items-center justify-between bg-ink px-5 text-on-ink"
            >
              <span className="type-label">{HERO.primary}</span>
              <svg viewBox="0 0 22 12" aria-hidden className="h-3 w-5" fill="none">
                <path d="M0 6h20M15 1l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="square" />
              </svg>
            </a>
          </nav>
        </div>
      )}
    </>
  );
}
