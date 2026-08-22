"use client";

import { useMemo, useState } from "react";
import { ToneChip } from "@/components/ui/StatusChips";
import type { FindingTone, TradeCase } from "@/lib/demo/store";

type NodeKind = "case" | "doc" | "identity" | "finding" | "recon" | "route";

interface GraphNode {
  id: string;
  kind: NodeKind;
  label: string;
  sublabel: string;
  tone: FindingTone;
  x: number;
  y: number;
  evidenceTitle: string;
  evidenceBody: string[];
  source?: string;
}

interface GraphEdge {
  from: string;
  to: string;
  label?: string;
  alert?: boolean;
}

function toneStroke(tone: FindingTone): string {
  if (tone === "clear") return "#047857";
  if (tone === "review") return "#b45309";
  if (tone === "block") return "#b91c1c";
  return "#1d4ed8";
}

function toneFill(tone: FindingTone): string {
  if (tone === "clear") return "#ecfdf5";
  if (tone === "review") return "#fffbeb";
  if (tone === "block") return "#fef2f2";
  return "#eff6ff";
}

function buildGraph(c: TradeCase): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  const routeTone: FindingTone =
    c.riskRoute === "READY_FOR_HUMAN_REVIEW"
      ? "clear"
      : c.riskRoute === "HIGH_RISK_ESCALATION"
        ? "block"
        : c.riskRoute === "DOCUMENT_PACK_INCOMPLETE" || c.riskRoute === "DATA_REVIEW_REQUIRED"
          ? "info"
          : "review";

  nodes.push({
    id: "case",
    kind: "case",
    label: c.reference,
    sublabel: "Trade case",
    tone: routeTone,
    x: 420,
    y: 210,
    evidenceTitle: "Case object",
    evidenceBody: [
      `${c.counterparty} · ${c.corridor}`,
      `Profile: ${c.profile}`,
      `Amount: ${c.currency} ${c.amount}`,
      `Workflow: ${c.workflow}`,
      `Risk route: ${c.riskRoute}`,
      "Decision support only — not an autonomous approval.",
    ],
  });

  nodes.push({
    id: "route",
    kind: "route",
    label: "Human route",
    sublabel: c.riskRoute.replace(/_/g, " "),
    tone: routeTone,
    x: 420,
    y: 40,
    evidenceTitle: "Recommended human route",
    evidenceBody: [
      c.riskRoute,
      "Derived from findings, pack completeness, and reconciliation.",
      "Agent consensus never overrides this route or maker/checker.",
    ],
  });
  edges.push({ from: "case", to: "route" });

  const providedDocs = c.docs.filter((d) => d.provided);
  const docNodes = (providedDocs.length ? providedDocs : c.docs.slice(0, 2)).slice(0, 3);
  docNodes.forEach((d, i) => {
    const id = `doc-${d.type}`;
    nodes.push({
      id,
      kind: "doc",
      label: d.label,
      sublabel: d.provided ? "Provided" : "Missing",
      tone: d.provided ? "clear" : d.blocker ? "block" : "info",
      x: 80,
      y: 80 + i * 110,
      evidenceTitle: d.label,
      evidenceBody: [
        `Requirement: ${d.policy}`,
        `Provided: ${d.provided ? "yes" : "no"}`,
        `Blocks pack if missing: ${d.blocker ? "yes" : "no"}`,
        "Text is read from the document for review; automated suggestions stay unverified until an officer accepts them.",
      ],
    });
    edges.push({ from: id, to: "case" });
  });

  const outcomeUpper = c.identity.outcome.toUpperCase();
  const idTone: FindingTone =
    outcomeUpper.includes("VERIFIED") || outcomeUpper.includes("SUPPORTED")
      ? "clear"
      : outcomeUpper.includes("UNAVAILABLE") || outcomeUpper.includes("UNRESOLVED")
        ? "info"
        : outcomeUpper.includes("REVIEW")
          ? "review"
          : "info";
  nodes.push({
    id: "identity",
    kind: "identity",
    label: "Counterparty",
    sublabel: c.identity.outcome.replace(/_/g, " "),
    tone: idTone,
    x: 760,
    y: 70,
    evidenceTitle: "Identity ladder",
    evidenceBody: [
      `Document name: ${c.identity.rawName}`,
      `LEI on document: ${c.identity.leiOnDocument ?? "not provided"}`,
      c.identity.candidateName
        ? `Registry candidate: ${c.identity.candidateName}`
        : "No registry candidate persisted",
      `Outcome: ${c.identity.outcome}`,
      c.identity.action,
      `vLEI: ${c.identity.vlei}`,
      "Fuzzy name similarity alone is never identity proof.",
    ],
  });
  edges.push({ from: "case", to: "identity" });

  c.findings.slice(0, 4).forEach((f, i) => {
    const id = `finding-${f.id}`;
    nodes.push({
      id,
      kind: "finding",
      label: f.title,
      sublabel: f.statusLabel,
      tone: f.tone,
      x: 760,
      y: 200 + i * 95,
      evidenceTitle: f.title,
      evidenceBody: [f.summary, `Next: ${f.action}`],
      source: f.source,
    });
    edges.push({
      from: "case",
      to: id,
      alert: f.tone === "review" || f.tone === "block",
    });
  });

  const mismatch = c.recon.find((r) => r.status === "MISMATCH");
  const reconTone: FindingTone = mismatch
    ? "review"
    : c.recon.some((r) => r.status === "MATCH")
      ? "clear"
      : "info";
  nodes.push({
    id: "recon",
    kind: "recon",
    label: "Reconciliation",
    sublabel: mismatch ? "Quantity / field mismatch" : "Cross-document compare",
    tone: reconTone,
    x: 80,
    y: 420,
    evidenceTitle: "Invoice ↔ transport reconciliation",
    evidenceBody: mismatch
      ? [
          `Field: ${mismatch.field}`,
          `Invoice: ${mismatch.invoice}`,
          `Bill of lading: ${mismatch.bol ?? "—"}`,
          mismatch.note,
          "Discrepancy requires human review — not an automated fraud conclusion.",
        ]
      : c.recon.slice(0, 4).map((r) => `${r.field}: ${r.status} (${r.invoice} / ${r.bol ?? "—"})`),
  });
  edges.push({
    from: "doc-" + (docNodes[0]?.type ?? "INVOICE"),
    to: "recon",
    alert: Boolean(mismatch),
  });
  edges.push({ from: "recon", to: "case", alert: Boolean(mismatch), label: mismatch ? "conflict" : undefined });

  return { nodes, edges };
}

export function InvestigationCanvas({ tradeCase }: { tradeCase: TradeCase }) {
  const { nodes, edges } = useMemo(() => buildGraph(tradeCase), [tradeCase]);
  const [selectedId, setSelectedId] = useState<string>("case");
  const selected = nodes.find((n) => n.id === selectedId) ?? nodes[0];

  const nodeById = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes]);

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className="tp-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-[var(--tp-line)] px-4 py-3">
          <div>
            <h2 className="text-sm font-semibold text-[var(--tp-navy)]">Investigation canvas</h2>
            <p className="mt-0.5 text-xs text-[var(--tp-muted)]">
              Object graph for this case — click a node for evidence. Not a global surveillance map.
            </p>
          </div>
          <span className="text-[11px] uppercase tracking-[0.12em] text-[var(--tp-muted)]">
            Decision support
          </span>
        </div>

        <div className="relative overflow-x-auto bg-[linear-gradient(180deg,#f8fafc_0%,#eef2f6_100%)]">
          <svg
            viewBox="0 0 980 560"
            className="h-[min(62vh,560px)] min-w-[720px] w-full"
            role="img"
            aria-label="Case investigation graph"
          >
            <defs>
              <marker
                id="tp-arrow"
                markerWidth="8"
                markerHeight="8"
                refX="6"
                refY="3"
                orient="auto"
              >
                <path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8" />
              </marker>
            </defs>

            {edges.map((e) => {
              const a = nodeById.get(e.from);
              const b = nodeById.get(e.to);
              if (!a || !b) return null;
              const midX = (a.x + b.x) / 2;
              const midY = (a.y + b.y) / 2;
              return (
                <g key={`${e.from}-${e.to}`}>
                  <line
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke={e.alert ? "#b45309" : "#94a3b8"}
                    strokeWidth={e.alert ? 2.2 : 1.4}
                    strokeDasharray={e.alert ? "5 4" : undefined}
                    markerEnd="url(#tp-arrow)"
                    opacity={0.85}
                  />
                  {e.label ? (
                    <text
                      x={midX}
                      y={midY - 6}
                      textAnchor="middle"
                      className="fill-[var(--tp-warn)]"
                      style={{ fontSize: 10, fontWeight: 600 }}
                    >
                      {e.label}
                    </text>
                  ) : null}
                </g>
              );
            })}

            {nodes.map((n) => {
              const active = n.id === selected.id;
              const w = n.kind === "case" ? 168 : 150;
              const h = n.kind === "case" ? 64 : 56;
              return (
                <g
                  key={n.id}
                  transform={`translate(${n.x - w / 2}, ${n.y - h / 2})`}
                  className="cursor-pointer"
                  onClick={() => setSelectedId(n.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(ev) => {
                    if (ev.key === "Enter" || ev.key === " ") {
                      ev.preventDefault();
                      setSelectedId(n.id);
                    }
                  }}
                >
                  <rect
                    width={w}
                    height={h}
                    rx={10}
                    fill={toneFill(n.tone)}
                    stroke={active ? varNavy() : toneStroke(n.tone)}
                    strokeWidth={active ? 2.5 : 1.5}
                  />
                  <text
                    x={w / 2}
                    y={22}
                    textAnchor="middle"
                    style={{ fontSize: 11, fontWeight: 700, fill: "#0c2340" }}
                  >
                    {truncate(n.label, 22)}
                  </text>
                  <text
                    x={w / 2}
                    y={40}
                    textAnchor="middle"
                    style={{ fontSize: 9, fill: "#5b6b7c" }}
                  >
                    {truncate(n.sublabel, 28)}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </section>

      <aside key={selected.id} className="tp-card flex flex-col p-4">
        <div className="flex items-start justify-between gap-2 animate-[tpFade_280ms_ease-out]">
          <div>
            <p className="text-[11px] uppercase tracking-[0.12em] text-[var(--tp-muted)]">
              Evidence
            </p>
            <h3 className="mt-1 text-base font-semibold text-[var(--tp-navy)]">
              {selected.evidenceTitle}
            </h3>
          </div>
          <ToneChip
            tone={selected.tone}
            label={
              selected.tone === "clear"
                ? "Clear"
                : selected.tone === "review"
                  ? "Review"
                  : selected.tone === "block"
                    ? "Block"
                    : "Info"
            }
          />
        </div>
        <ul className="mt-4 flex-1 space-y-2 text-sm leading-relaxed text-[var(--tp-ink)]">
          {selected.evidenceBody.map((line) => (
            <li key={line} className="border-l-2 border-[var(--tp-line)] pl-3">
              {line}
            </li>
          ))}
        </ul>
        {selected.source ? (
          <p className="mt-4 break-all font-mono text-[10px] text-[var(--tp-muted)]">
            Source: {selected.source}
          </p>
        ) : null}
        <p className="mt-3 text-[11px] text-[var(--tp-muted)]">
          Provenance stays with the case. Replay creates a new result version; history is not overwritten.
        </p>
      </aside>
    </div>
  );
}

function truncate(s: string, n: number): string {
  return s.length <= n ? s : `${s.slice(0, n - 1)}…`;
}

function varNavy(): string {
  return "#0c2340";
}
