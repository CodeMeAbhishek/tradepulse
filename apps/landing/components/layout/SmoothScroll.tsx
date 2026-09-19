"use client";

import { useEffect } from "react";
import Lenis from "lenis";
import { gsap, ScrollTrigger, MQ } from "@/lib/gsap";
import { setLenis } from "@/lib/lenis";

/**
 * Smooth scroll only.
 *
 * There are deliberately no scroll-triggered entrance tweens on this page. A
 * fade-and-rise on every section is the commonest tell of a generated site,
 * and it makes a page that is meant to read as an instrument feel like a
 * brochure. The hero plays one orchestrated sequence; everything else is
 * simply there when you arrive at it.
 *
 * Lenis and ScrollTrigger still share a clock, so anchor scrolling and any
 * future scrubbed value stay in step.
 */
export function SmoothScroll() {
  useEffect(() => {
    const mm = gsap.matchMedia();

    mm.add(MQ.motion, () => {
      const lenis = new Lenis({ duration: 1.1, anchors: true, allowNestedScroll: true });
      setLenis(lenis);

      lenis.on("scroll", ScrollTrigger.update);
      const tick = (t: number) => lenis.raf(t * 1000);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);

      return () => {
        gsap.ticker.remove(tick);
        lenis.destroy();
        setLenis(null);
      };
    });

    return () => mm.revert();
  }, []);

  return null;
}
