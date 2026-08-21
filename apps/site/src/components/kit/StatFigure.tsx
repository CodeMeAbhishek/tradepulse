import { useEffect, useRef, useState } from "react";
import { useInView } from "motion/react";
import { DUR } from "@/lib/motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";

/** Counts from zero on first entry only. Client-only measurement. */
export function StatFigure({
  value,
  prefix = "",
  suffix = "",
  label,
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  label: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.18 });
  const reduced = useReducedMotion();
  const [shown, setShown] = useState(0);

  useEffect(() => {
    if (!inView) return;
    if (reduced || value === 0) {
      setShown(value);
      return;
    }
    const start = performance.now();
    let frame = 0;
    const tick = (now: number) => {
      const t = Math.min((now - start) / (DUR.counter * 1000), 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setShown(Math.round(value * eased));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, reduced, value]);

  return (
    <div ref={ref} className="hairline-t flex flex-col gap-4 pt-6">
      <span className="text-h1 font-mono text-ink">
        {prefix}
        {shown}
        {suffix}
      </span>
      <span className="text-label max-w-[22ch] text-slate">{label}</span>
    </div>
  );
}
