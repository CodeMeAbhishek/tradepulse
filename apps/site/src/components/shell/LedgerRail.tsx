import { useEffect, useState } from "react";
import { motion, useScroll, useSpring } from "motion/react";
import { DUR } from "@/lib/motion";

/** The margin of a bound ledger. Hidden below 1024px. */
export function LedgerRail({ fallback }: { fallback: { number: string; name: string } }) {
  const [active, setActive] = useState(fallback);
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 120, damping: 30 });

  useEffect(() => {
    const nodes = Array.from(document.querySelectorAll<HTMLElement>("[data-section-number]"));
    if (!nodes.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        const el = visible?.target as HTMLElement | undefined;
        if (!el) return;
        setActive({
          number: el.dataset["sectionNumber"] ?? fallback.number,
          name: el.dataset["sectionName"] ?? fallback.name,
        });
      },
      { rootMargin: "-20% 0px -60% 0px", threshold: 0 },
    );
    nodes.forEach((n) => observer.observe(n));
    return () => observer.disconnect();
  }, [fallback]);

  return (
    <div
      aria-hidden
      className="fixed top-0 left-0 z-40 hidden h-screen w-[72px] border-r border-rule lg:block"
    >
      <div className="flex h-full flex-col items-center justify-between py-[92px]">
        <motion.span
          key={`${active.number}-${active.name}`}
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: DUR.routeChange }}
          className="text-label whitespace-nowrap text-slate"
          style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
        >
          {active.number} · {active.name}
        </motion.span>

        <div className="h-[38%] w-px bg-rule">
          <motion.div
            className="w-px origin-top bg-ink"
            style={{ height: "100%", scaleY: progress }}
          />
        </div>
      </div>
    </div>
  );
}
