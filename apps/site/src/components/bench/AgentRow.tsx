import { motion } from "motion/react";
import type { AgentName } from "@/types";
import { AGENT_LABEL } from "@/lib/severity";
import { EASE } from "@/lib/motion";

/** Name, then a determinate sweep line. No percentages, no spinners. */
export function AgentRow({
  agent,
  state,
  sweepSeconds,
  reduced,
  children,
}: {
  agent: AgentName;
  state: "waiting" | "running" | "done";
  sweepSeconds: number;
  reduced: boolean;
  children?: React.ReactNode;
}) {
  const width = state === "waiting" ? 0 : state === "running" ? "100%" : "100%";

  return (
    <section className="hairline-b py-6">
      <div className="flex items-baseline justify-between gap-6">
        <h3 className="text-label text-ink">{AGENT_LABEL[agent]}</h3>
        <span className="text-label text-slate">
          {state === "waiting" ? "QUEUED" : state === "running" ? "READING" : "COMPLETE"}
        </span>
      </div>
      <div className="mt-3 h-px w-full bg-rule">
        <motion.div
          className="h-px"
          style={{ backgroundColor: "var(--ink)", originX: 0 }}
          initial={{ width: 0 }}
          animate={{ width }}
          transition={{
            duration: reduced ? 0 : state === "running" ? sweepSeconds : 0.2,
            ease: EASE.inOut,
          }}
        />
      </div>
      {children ? <div className="mt-2">{children}</div> : null}
    </section>
  );
}
