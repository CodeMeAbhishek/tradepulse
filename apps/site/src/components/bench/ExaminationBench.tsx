import { useCallback, useEffect, useRef, useState } from "react";
import type { DocumentSetResult, Finding } from "@/types";
import { runAnalysis } from "@/lib/analysis";
import { AGENT_ORDER } from "@/lib/severity";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { StatusStrip } from "./StatusStrip";
import { BenchEmptyState } from "./BenchEmptyState";
import { DocumentStage } from "./DocumentStage";
import { FindingsPanel } from "./FindingsPanel";

const SWEEP_MS = [1000, 1000, 800, 700];

export function ExaminationBench() {
  const reduced = useReducedMotion();
  const [phase, setPhase] = useState<"empty" | "running" | "result">("empty");
  const [result, setResult] = useState<DocumentSetResult | null>(null);
  const [revealed, setRevealed] = useState<string[]>([]);
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const [selected, setSelected] = useState<Finding | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const load = useCallback(async () => {
    setPhase("running");
    setRevealed([]);
    setActiveAgentIndex(0);
    setSelected(null);

    const set = await runAnalysis();
    setResult(set);

    let elapsed = 0;
    AGENT_ORDER.forEach((agent, i) => {
      elapsed += SWEEP_MS[i] ?? 800;
      timers.current.push(
        setTimeout(() => {
          setActiveAgentIndex(i + 1);
          setRevealed((prev) => [
            ...prev,
            ...set.findings.filter((f) => f.agent === agent).map((f) => f.id),
          ]);
          if (i === AGENT_ORDER.length - 1) setPhase("result");
        }, elapsed),
      );
    });
  }, []);

  const documentsLoaded = phase === "empty" ? 0 : 5;

  return (
    <div className="flex flex-col gap-6">
      <StatusStrip
        documents={documentsLoaded}
        corridor="IN→AE"
        hsCode="5208.52"
        state={phase === "empty" ? "AWAITING SET" : phase === "running" ? "EXAMINING" : "REPORTED"}
      />

      {phase === "empty" || !result ? (
        <BenchEmptyState onLoad={load} />
      ) : (
        <div className="grid gap-8 xl:grid-cols-[60fr_40fr]">
          <DocumentStage finding={selected} reduced={reduced} />
          <FindingsPanel
            result={result}
            revealed={revealed}
            activeAgentIndex={activeAgentIndex}
            selectedId={selected?.id ?? null}
            onSelect={(f) => setSelected((prev) => (prev?.id === f.id ? null : f))}
            reduced={reduced}
          />
        </div>
      )}
    </div>
  );
}
