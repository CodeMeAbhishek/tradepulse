import { motion } from "motion/react";
import { DUR, EASE } from "@/lib/motion";
import { cn } from "@/lib/utils";

/** Hairline that draws from the left as its section enters. */
export function RuleDivider({
  className,
  tone = "rule",
}: {
  className?: string;
  tone?: "rule" | "ink";
}) {
  return (
    <motion.div
      initial={{ scaleX: 0 }}
      whileInView={{ scaleX: 1 }}
      viewport={{ once: true, amount: 0.18 }}
      transition={{ duration: DUR.divider, ease: EASE.out }}
      style={{ originX: 0, backgroundColor: tone === "ink" ? "var(--ink)" : "var(--rule)" }}
      className={cn("h-px w-full", className)}
    />
  );
}
