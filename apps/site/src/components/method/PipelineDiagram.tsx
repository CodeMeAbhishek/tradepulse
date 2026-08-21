import { motion } from "motion/react";
import { DUR, EASE } from "@/lib/motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";

/**
 * Documents in, four agents, orchestrator, scored report out.
 * Hairline strokes only — no filled shapes, no arrowheads. Paths draw left to
 * right the first time the diagram enters the viewport, then hold still.
 */

const VB = { w: 1240, h: 360 };

const DOCS = [
  "COMMERCIAL INVOICE",
  "BILL OF LADING",
  "PACKING LIST",
  "CERT. OF ORIGIN",
  "MT700 CREDIT",
];

const AGENTS = [
  { name: "EXTRACTION", note: "vision → typed fields" },
  { name: "CONSISTENCY", note: "UCP 600 in code" },
  { name: "PRICE", note: "Comtrade unit bands" },
  { name: "SANCTIONS", note: "parties, vessel, ports" },
];

const DOC_X = 24;
const DOC_W = 168;
const DOC_H = 40;
const DOC_GAP = 20;
const DOC_TOP = 40;

const BUS_IN = 268;
const AGENT_X = 344;
const AGENT_W = 268;
const AGENT_H = 56;
const AGENT_GAP = 20;
const AGENT_TOP = 44;

const BUS_OUT = 688;
const ORCH_X = 764;
const ORCH_W = 180;
const REPORT_X = 1032;
const REPORT_W = 184;
const MID_H = 92;
const MID_Y = VB.h / 2 - MID_H / 2;

const docY = (i: number) => DOC_TOP + i * (DOC_H + DOC_GAP);
const agentY = (i: number) => AGENT_TOP + i * (AGENT_H + AGENT_GAP);

export function PipelineDiagram() {
  const reduced = useReducedMotion();

  const draw = (delay: number) => ({
    initial: { pathLength: reduced ? 1 : 0 },
    whileInView: { pathLength: 1 },
    viewport: { once: true, amount: 0.3 } as const,
    transition: reduced ? { duration: 0 } : { duration: DUR.connector, ease: EASE.inOut, delay },
  });

  const fade = (delay: number) => ({
    initial: { opacity: reduced ? 1 : 0 },
    whileInView: { opacity: 1 },
    viewport: { once: true, amount: 0.3 } as const,
    transition: reduced ? { duration: 0 } : { duration: DUR.divider, delay },
  });

  const docBusTop = docY(0) + DOC_H / 2;
  const docBusBottom = docY(DOCS.length - 1) + DOC_H / 2;
  const agentBusTop = agentY(0) + AGENT_H / 2;
  const agentBusBottom = agentY(AGENTS.length - 1) + AGENT_H / 2;

  return (
    <figure className="hairline-t hairline-b -mx-6 overflow-x-auto py-12 lg:-mx-8">
      <div className="min-w-[900px] px-6 lg:px-8">
        <svg
          viewBox={`0 0 ${VB.w} ${VB.h}`}
          className="h-auto w-full"
          role="img"
          aria-label="Pipeline: five documents enter extraction, cross-document consistency, price verification and sanctions screening; an orchestrator assembles a scored exception report."
        >
          {/* documents in */}
          {DOCS.map((d, i) => (
            <motion.g key={d} {...fade(i * 0.06)}>
              <rect
                x={DOC_X}
                y={docY(i)}
                width={DOC_W}
                height={DOC_H}
                fill="none"
                stroke="var(--rule)"
                strokeWidth={1}
              />
              <text
                x={DOC_X + 14}
                y={docY(i) + DOC_H / 2 + 4}
                fontSize={12}
                letterSpacing="0.1em"
                fill="var(--slate)"
                style={{ fontFamily: "var(--font-condensed)" }}
              >
                {d}
              </text>
            </motion.g>
          ))}

          {/* documents → collection bus */}
          {DOCS.map((d, i) => (
            <motion.path
              key={`in-${d}`}
              d={`M ${DOC_X + DOC_W} ${docY(i) + DOC_H / 2} H ${BUS_IN}`}
              fill="none"
              stroke="var(--rule)"
              strokeWidth={1}
              {...draw(0.1 + i * 0.05)}
            />
          ))}
          <motion.path
            d={`M ${BUS_IN} ${docBusTop} V ${docBusBottom}`}
            fill="none"
            stroke="var(--rule)"
            strokeWidth={1}
            {...draw(0.35)}
          />

          {/* bus → each agent */}
          {AGENTS.map((a, i) => (
            <motion.path
              key={`fan-${a.name}`}
              d={`M ${BUS_IN} ${(docBusTop + docBusBottom) / 2} C ${(BUS_IN + AGENT_X) / 2} ${(docBusTop + docBusBottom) / 2}, ${(BUS_IN + AGENT_X) / 2} ${agentY(i) + AGENT_H / 2}, ${AGENT_X} ${agentY(i) + AGENT_H / 2}`}
              fill="none"
              stroke="var(--ink)"
              strokeWidth={1}
              {...draw(0.45 + i * 0.06)}
            />
          ))}

          {/* the four agents */}
          {AGENTS.map((a, i) => (
            <motion.g key={a.name} {...fade(0.5 + i * 0.06)}>
              <rect
                x={AGENT_X}
                y={agentY(i)}
                width={AGENT_W}
                height={AGENT_H}
                fill="none"
                stroke="var(--ink)"
                strokeWidth={1}
              />
              <text
                x={AGENT_X + 16}
                y={agentY(i) + 24}
                fontSize={12}
                letterSpacing="0.1em"
                fill="var(--ink)"
                style={{ fontFamily: "var(--font-condensed)" }}
              >
                {`0${i + 1} · ${a.name}`}
              </text>
              <text
                x={AGENT_X + 16}
                y={agentY(i) + 43}
                fontSize={13}
                fill="var(--slate)"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                {a.note}
              </text>
            </motion.g>
          ))}

          {/* agents → orchestrator */}
          {AGENTS.map((a, i) => (
            <motion.path
              key={`out-${a.name}`}
              d={`M ${AGENT_X + AGENT_W} ${agentY(i) + AGENT_H / 2} C ${(AGENT_X + AGENT_W + BUS_OUT) / 2} ${agentY(i) + AGENT_H / 2}, ${(AGENT_X + AGENT_W + BUS_OUT) / 2} ${VB.h / 2}, ${BUS_OUT} ${VB.h / 2}`}
              fill="none"
              stroke="var(--ink)"
              strokeWidth={1}
              {...draw(0.7 + i * 0.05)}
            />
          ))}
          <motion.path
            d={`M ${BUS_OUT} ${agentBusTop} V ${agentBusBottom}`}
            fill="none"
            stroke="var(--rule)"
            strokeWidth={1}
            {...draw(0.7)}
          />
          <motion.path
            d={`M ${BUS_OUT} ${VB.h / 2} H ${ORCH_X}`}
            fill="none"
            stroke="var(--ink)"
            strokeWidth={1}
            {...draw(0.95)}
          />

          {/* orchestrator */}
          <motion.g {...fade(1)}>
            <rect
              x={ORCH_X}
              y={MID_Y}
              width={ORCH_W}
              height={MID_H}
              fill="none"
              stroke="var(--ink)"
              strokeWidth={1}
            />
            <text
              x={ORCH_X + 16}
              y={MID_Y + 32}
              fontSize={12}
              letterSpacing="0.1em"
              fill="var(--ink)"
              style={{ fontFamily: "var(--font-condensed)" }}
            >
              ORCHESTRATOR
            </text>
            <text
              x={ORCH_X + 16}
              y={MID_Y + 56}
              fontSize={13}
              fill="var(--slate)"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              severity table
            </text>
            <text
              x={ORCH_X + 16}
              y={MID_Y + 74}
              fontSize={13}
              fill="var(--slate)"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              static, not learned
            </text>
          </motion.g>

          {/* orchestrator → report */}
          <motion.path
            d={`M ${ORCH_X + ORCH_W} ${VB.h / 2} H ${REPORT_X}`}
            fill="none"
            stroke="var(--ink)"
            strokeWidth={1}
            {...draw(1.05)}
          />
          <motion.text
            x={(ORCH_X + ORCH_W + REPORT_X) / 2 - 6}
            y={VB.h / 2 - 10}
            fontSize={16}
            fill="var(--ink)"
            style={{ fontFamily: "var(--font-mono)" }}
            {...fade(1.15)}
          >
            →
          </motion.text>

          {/* scored report out */}
          <motion.g {...fade(1.15)}>
            <rect
              x={REPORT_X}
              y={MID_Y}
              width={REPORT_W}
              height={MID_H}
              fill="none"
              stroke="var(--ink)"
              strokeWidth={1}
            />
            <text
              x={REPORT_X + 16}
              y={MID_Y + 32}
              fontSize={12}
              letterSpacing="0.1em"
              fill="var(--ink)"
              style={{ fontFamily: "var(--font-condensed)" }}
            >
              EXCEPTION REPORT
            </text>
            <text
              x={REPORT_X + 16}
              y={MID_Y + 56}
              fontSize={13}
              fill="var(--slate)"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              scored · cited
            </text>
            <text
              x={REPORT_X + 16}
              y={MID_Y + 74}
              fontSize={13}
              fill="var(--slate)"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              signed by a human
            </text>
          </motion.g>
        </svg>
      </div>
      <figcaption className="text-label mt-8 px-6 text-slate lg:px-8">
        FIG. 01 · NOTHING CROSSES THE ORCHESTRATOR WITHOUT A DOCUMENT, A PAGE AND A FIELD
      </figcaption>
    </figure>
  );
}
