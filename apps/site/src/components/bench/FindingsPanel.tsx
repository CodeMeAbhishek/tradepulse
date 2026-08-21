import { useRef } from "react";
import type { DocumentSetResult, Finding as FindingType } from "@/types";
import { AGENT_ORDER } from "@/lib/severity";
import { Finding } from "@/components/kit/Finding";
import { AgentRow } from "./AgentRow";

const SWEEP: Record<(typeof AGENT_ORDER)[number], number> = {
  extraction: 1,
  consistency: 1,
  price: 0.8,
  sanctions: 0.7,
};

export function FindingsPanel({
  result,
  revealed,
  activeAgentIndex,
  selectedId,
  onSelect,
  reduced,
}: {
  result: DocumentSetResult;
  revealed: string[];
  activeAgentIndex: number;
  selectedId: string | null;
  onSelect: (f: FindingType) => void;
  reduced: boolean;
}) {
  const panelRef = useRef<HTMLDivElement>(null);
  const visible = result.findings.filter((f) => revealed.includes(f.id));
  const criticals = visible.filter((f) => f.severity === "critical").length;
  const discrepancies = visible.filter((f) => f.severity !== "passed").length;
  const riskScore = criticals * 30 + (discrepancies - criticals) * 10;
  const complete = activeAgentIndex >= AGENT_ORDER.length;

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    // Read the buttons in DOM order. Findings render grouped by agent, so an
    // array indexed by position in `result.findings` walks the list in a
    // different order than the reader sees.
    const els = Array.from(
      panelRef.current?.querySelectorAll<HTMLButtonElement>("button[data-finding-index]") ?? [],
    );
    if (!els.length) return;
    const current = els.indexOf(document.activeElement as HTMLButtonElement);
    const next =
      e.key === "ArrowDown" ? Math.min(els.length - 1, current + 1) : Math.max(0, current - 1);
    // At either end `next` is the current row; clicking it again would toggle
    // the selection off, so only move focus there.
    els[next]?.focus();
    if (next !== current) els[next]?.click();
  };

  return (
    <div className="flex min-w-0 flex-col">
      <div className="hairline-b pb-6">
        <p className="text-display font-mono text-ink">
          {complete ? `${discrepancies} discrepancies` : `${visible.length} findings`}
        </p>
        <p className="text-data mt-2 text-slate">
          {complete
            ? `${criticals} critical · risk score ${riskScore} / 100 · ${result.risk_level.toUpperCase()}`
            : "examination in progress"}
        </p>
      </div>

      <div ref={panelRef} aria-live="polite" aria-atomic="false" onKeyDown={onKeyDown}>
        {AGENT_ORDER.map((agent, i) => {
          const state =
            i < activeAgentIndex ? "done" : i === activeAgentIndex ? "running" : "waiting";
          const agentFindings = visible.filter((f) => f.agent === agent);
          return (
            <AgentRow
              key={agent}
              agent={agent}
              state={state}
              sweepSeconds={SWEEP[agent]}
              reduced={reduced}
            >
              {agentFindings.length ? (
                <ul>
                  {agentFindings.map((f) => (
                    <Finding
                      key={f.id}
                      finding={f}
                      index={result.findings.indexOf(f)}
                      selected={selectedId === f.id}
                      onSelect={() => onSelect(f)}
                    />
                  ))}
                </ul>
              ) : null}
            </AgentRow>
          );
        })}
      </div>

      <p className="text-small mt-6 max-w-[46ch] text-slate">
        Select a finding to move the document to the region it cites. Arrow keys walk the list.
      </p>
    </div>
  );
}
