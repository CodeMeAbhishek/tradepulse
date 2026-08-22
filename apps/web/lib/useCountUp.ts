"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Counts a number up to its target when it changes.
 *
 * Used only on the overview tiles, so a queue that fills in reads as arriving
 * rather than appearing. Deliberately short: this is a settling motion, not a
 * spectacle, and the final value is always exact — it never rounds or estimates.
 *
 * Honours prefers-reduced-motion by jumping straight to the value.
 */
export function useCountUp(target: number, durationMs = 420): number {
  const [value, setValue] = useState(target);
  const frame = useRef<number | null>(null);
  const from = useRef(target);

  useEffect(() => {
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduced || target === value) {
      setValue(target);
      return;
    }

    from.current = value;
    const start = performance.now();
    const delta = target - from.current;

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      // Ease out: quick to most of the way, then settles.
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(Math.round(from.current + delta * eased));
      if (t < 1) frame.current = requestAnimationFrame(tick);
    };

    frame.current = requestAnimationFrame(tick);
    return () => {
      if (frame.current !== null) cancelAnimationFrame(frame.current);
    };
    // `value` is intentionally excluded: including it restarts the animation on
    // every frame it sets.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, durationMs]);

  return value;
}
