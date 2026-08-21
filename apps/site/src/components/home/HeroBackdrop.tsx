import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { mt700Doc } from "@/content/documents";
import { useReducedMotion } from "@/hooks/useReducedMotion";

/**
 * The MT700 behind the headline. Decorative, never announced, never clickable.
 * Parallaxes 40px upward across the hero's own scroll range — the scroll target
 * is this element, so nothing measures `window` during render.
 */

// Flattened once at module scope: the block never changes.
const LINES: string[] = mt700Doc.tags.flatMap((t) => [
  `${t.tag} ${t.value[0]}`,
  ...t.value.slice(1).map((v) => `      ${v}`),
]);

const MASK = "radial-gradient(66% 68% at 44% 42%, #000 0%, rgba(0,0,0,0.6) 52%, rgba(0,0,0,0) 88%)";

export function HeroBackdrop() {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });
  // Reduced motion flattens the range rather than dropping the prop, so the
  // hook order and the style object stay identical between renders.
  const y = useTransform(scrollYProgress, [0, 1], reduced ? [0, 0] : [0, -40]);

  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none absolute inset-0 overflow-hidden select-none"
    >
      <motion.pre
        style={{
          y,
          // Dissolve at every edge so the block reads as texture in the paper,
          // never as numbers competing with the headline.
          maskImage: MASK,
          WebkitMaskImage: MASK,
        }}
        className="text-h2 absolute top-[9%] left-[2%] hidden whitespace-pre font-mono text-ink opacity-[0.03] lg:block"
      >
        {LINES.join("\n")}
      </motion.pre>
    </div>
  );
}
