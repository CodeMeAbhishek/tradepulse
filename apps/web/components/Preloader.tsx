"use client";

import { useEffect, useState } from "react";

/**
 * TradePulse preloader — "The Infinite Spin".
 *
 * Loading: the two arcs counter-rotate at a constant linear speed while the
 * centre mark is masked out. Loaded: the arcs settle back to zero and the mark
 * develops left to right. Then the overlay fades and React unmounts it.
 *
 * Three details that matter:
 *
 * - The overlay is removed by REACT, never by `element.remove()`. React renders
 *   this node, so tearing it out of the DOM directly desynchronises React's
 *   internal tree from the document; the next navigation then fails with
 *   "insertBefore / removeChild: node is not a child of this node".
 *
 * - `transform-box: view-box` with `transform-origin: 100px 100px` pins both
 *   arcs to the centre of the viewBox. The default (`fill-box`) uses each arc's
 *   own bounding box, whose centre is not the circle's centre, so the arcs
 *   would wobble as they turned.
 *
 * - A failsafe fires regardless of load events. A spinner that never leaves is
 *   the worst outcome on a demo stage.
 */

type Phase = "loading" | "loaded" | "done";

/** Set by the mounted component so the exported trigger can reach it. */
let setPhaseExternal: ((p: Phase) => void) | null = null;

/** Starts the reveal. Safe to call before mount or more than once. */
export function triggerLoadedState(): void {
  setPhaseExternal?.("loaded");
}

export function Preloader() {
  const [phase, setPhase] = useState<Phase>("loading");

  useEffect(() => {
    setPhaseExternal = setPhase;
    return () => {
      setPhaseExternal = null;
    };
  }, []);

  // Start the reveal once the page has loaded.
  useEffect(() => {
    if (document.readyState === "complete") {
      setPhase("loaded");
      return;
    }
    const onLoad = () => setPhase("loaded");
    window.addEventListener("load", onLoad);
    const failsafe = window.setTimeout(() => setPhase("loaded"), 6000);
    return () => {
      window.removeEventListener("load", onLoad);
      window.clearTimeout(failsafe);
    };
  }, []);

  // Hold the finished logo briefly, fade, then let React unmount it.
  useEffect(() => {
    if (phase !== "loaded") return;
    const fade = window.setTimeout(() => setPhase("done"), 800);
    return () => window.clearTimeout(fade);
  }, [phase]);

  const [gone, setGone] = useState(false);
  useEffect(() => {
    if (phase !== "done") return;
    const remove = window.setTimeout(() => setGone(true), 450);
    return () => window.clearTimeout(remove);
  }, [phase]);

  if (gone) return null;

  return (
    <div id="tp-preloader" data-state={phase} role="status" aria-label="Loading TradePulse">
      <svg viewBox="0 0 200 200" width="132" height="132" aria-hidden="true">
        {/* Outer blue arc — clockwise */}
        <path
          id="outer-blue-arc"
          d="M 119.7 26.6 A 76 76 0 1 0 171.4 74"
          fill="none"
          stroke="#1B4F9E"
          strokeWidth="15"
          strokeLinecap="round"
        />

        {/* Inner orange arc — counter-clockwise */}
        <path
          id="outer-orange-arc"
          d="M 48 70 A 60 60 0 0 1 156.4 120.5"
          fill="none"
          stroke="#E9631D"
          strokeWidth="13"
          strokeLinecap="round"
        />

        {/* Masked out until the reveal */}
        <g id="center-t-and-arrow">
          <path d="M 55 76 H 122 V 92 H 98 V 132 H 80 V 92 H 55 Z" fill="#1B4F9E" />
          <path
            d="M 44 138 L 66 112 L 82 128 L 101 96 L 116 112 L 152 59"
            fill="none"
            stroke="#E9631D"
            strokeWidth="12"
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          <path d="M 177 31 L 166 69 L 141 47 Z" fill="#2E6FB7" />
        </g>
      </svg>

      <p id="tp-preloader-word">TRADEPULSE</p>
    </div>
  );
}
