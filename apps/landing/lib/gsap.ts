"use client";

/**
 * Single place GSAP plugins are registered. Import gsap/ScrollTrigger from
 * here, never from "gsap" directly, so registration always happens once.
 */
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Draggable } from "gsap/Draggable";
import { InertiaPlugin } from "gsap/InertiaPlugin";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, Draggable, InertiaPlugin, useGSAP);

/** House easing: decisive out, no overshoot. A bank audience reads bounce as toy-like. */
export const EASE_OUT = "power3.out";

export const MQ = {
  motion: "(prefers-reduced-motion: no-preference)",
  desktop: "(min-width: 1024px) and (prefers-reduced-motion: no-preference)",
  /** Dragging is desktop-only: on a phone it would compete with the scroll. */
  drag: "(min-width: 1024px) and (pointer: fine) and (prefers-reduced-motion: no-preference)",
} as const;

export { gsap, ScrollTrigger, Draggable, InertiaPlugin, useGSAP };
