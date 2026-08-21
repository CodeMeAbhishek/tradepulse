import { motion } from "motion/react";
import type { Finding as FindingType } from "@/types";
import { SEVERITY_COLOR, SEVERITY_LABEL, SEVERITY_TEXT } from "@/lib/severity";
import { SPRING } from "@/lib/motion";
import { cn } from "@/lib/utils";

export function Finding({
  finding,
  selected,
  onSelect,
  index,
  registerRef,
}: {
  finding: FindingType;
  selected: boolean;
  onSelect: () => void;
  index: number;
  registerRef?: (el: HTMLButtonElement | null) => void;
}) {
  return (
    <motion.li
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={SPRING}
      className="hairline-b"
    >
      <button
        ref={registerRef}
        type="button"
        data-finding-index={index}
        aria-pressed={selected}
        onClick={onSelect}
        className={cn(
          "block w-full px-1 py-6 text-left transition-colors duration-[120ms]",
          selected ? "bg-paper" : "bg-transparent",
        )}
        style={selected ? { boxShadow: "none" } : undefined}
      >
        <span
          className={cn("text-label block", SEVERITY_TEXT[finding.severity])}
          style={{ color: SEVERITY_COLOR[finding.severity] }}
        >
          {SEVERITY_LABEL[finding.severity]}
        </span>
        <span className="text-h3 mt-3 block font-mono text-ink">{finding.title}</span>
        <span className="text-small mt-3 block max-w-[52ch] text-slate">{finding.body}</span>
        <span className="text-data mt-4 block text-slate">
          {finding.sourceDoc} · p.{finding.page} · {finding.field}
          {finding.ucpArticle ? ` · ${finding.ucpArticle}` : ""}
        </span>
        {finding.type === "cross_document" ? (
          <span className="text-label mt-3 block text-slate">
            {finding.sourceDoc} → {finding.secondDoc}
          </span>
        ) : null}
      </button>
    </motion.li>
  );
}
