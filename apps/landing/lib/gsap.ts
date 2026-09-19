"use client";

/**
 * Single place GSAP plugins are registered. Import gsap/ScrollTrigger from
 * here, never from "gsap" directly, so registration always happens once.
 */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, useGSAP);

/** House easing: decisive out, no overshoot. A bank audience reads bounce as toy-like. */
export const EASE_OUT = "power3.out";

export const MQ = {
  motion: "(prefers-reduced-motion: no-preference)",
  desktop: "(min-width: 1024px) and (prefers-reduced-motion: no-preference)",
} as const;

export { gsap, ScrollTrigger, useGSAP };
