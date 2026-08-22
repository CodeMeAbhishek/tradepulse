"use client";

export type LadderStep = {
  rung_id: string;
  label: string;
  description: string;
  reached: boolean;
  current: boolean;
};

export type IdentityLadderModel = {
  role?: string;
  party_name?: string | null;
  resolution_status: string;
  current_rung_id: string | null;
  side_state?: string | null;
  safety_note: string;
  steps: LadderStep[];
};

const FALLBACK_STEPS: LadderStep[] = [
  {
    rung_id: "document_name",
    label: "Document name only",
    description: "Party name from the document. Not identity proof.",
    reached: true,
    current: true,
  },
  {
    rung_id: "registry_candidate",
    label: "Registry name candidate",
    description: "GLEIF/name search hit. Candidate only — review required.",
    reached: false,
    current: false,
  },
  {
    rung_id: "verified_by_lei",
    label: "Verified by LEI",
    description: "Document LEI matches a compatible GLEIF record.",
    reached: false,
    current: false,
  },
  {
    rung_id: "supported_by_vlei",
    label: "Supported by vLEI",
    description: "Verifiable credential evidence for entity/role (not a sanctions clear).",
    reached: false,
    current: false,
  },
];

/** Build a ladder view from a resolution status code when API ladder is unavailable. */
export function ladderFromStatus(status: string | null | undefined): IdentityLadderModel {
  const code = (status || "IDENTITY_UNRESOLVED").toUpperCase();
  const order = [
    "document_name",
    "registry_candidate",
    "verified_by_lei",
    "supported_by_vlei",
  ] as const;
  const map: Record<string, (typeof order)[number]> = {
    IDENTITY_UNRESOLVED: "document_name",
    POTENTIAL_ENTITY_MATCH_REVIEW: "registry_candidate",
    IDENTITY_VERIFIED_BY_LEI: "verified_by_lei",
    IDENTITY_SUPPORTED_BY_VLEI: "supported_by_vlei",
  };
  let current: (typeof order)[number] = "document_name";
  let side: string | null = null;
  let note =
    "Identity unresolved. Provide an LEI or other stable identifier when available.";

  if (code === "IDENTITY_SOURCE_UNAVAILABLE") {
    side = code;
    note = "Identity source unavailable — do not treat as verified or as a pass.";
  } else if (code === "VLEI_NOT_CONFIGURED") {
    side = code;
    note = "vLEI verifier is not configured. A plain LEI string is not a vLEI.";
  } else if (map[code]) {
    current = map[code];
    if (code === "POTENTIAL_ENTITY_MATCH_REVIEW") {
      note = "Name similarity alone is never identity proof. Request a stable identifier.";
    } else if (code === "IDENTITY_VERIFIED_BY_LEI") {
      note =
        "LEI match is strong identity evidence. It is not a sanctions clear, fraud finding, or payment approval.";
    } else if (code === "IDENTITY_SUPPORTED_BY_VLEI") {
      note =
        "vLEI supports identity/authority evidence. Fixture results must stay labeled synthetic.";
    }
  }

  const idx = order.indexOf(current);
  const steps = FALLBACK_STEPS.map((s, i) => {
    if (code === "IDENTITY_SOURCE_UNAVAILABLE") {
      return {
        ...s,
        reached: s.rung_id === "document_name",
        current: s.rung_id === "document_name",
      };
    }
    return {
      ...s,
      reached: i <= idx,
      current: s.rung_id === current,
    };
  });

  return {
    resolution_status: code,
    current_rung_id: current,
    side_state: side,
    safety_note: note,
    steps,
  };
}

export function IdentityLadder({ ladder }: { ladder: IdentityLadderModel }) {
  return (
    <div className="rounded-lg border border-[var(--tp-line)] bg-slate-50 p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-sm font-semibold text-[var(--tp-navy)]">Identity confidence ladder</h3>
        {ladder.side_state ? (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-[11px] font-medium text-amber-950">
            {ladder.side_state.replaceAll("_", " ")}
          </span>
        ) : null}
      </div>
      <p className="mt-1 text-xs text-[var(--tp-muted)]">
        Climb only with evidence. Name candidates never count as verified identity.
      </p>
      <ol className="mt-4 space-y-2">
        {ladder.steps.map((step, i) => (
          <li key={step.rung_id} className="flex gap-3">
            <div className="flex w-6 flex-col items-center">
              <span
                className={
                  step.current
                    ? "flex h-6 w-6 items-center justify-center rounded-full bg-[var(--tp-navy)] text-[11px] font-semibold text-white"
                    : step.reached
                      ? "flex h-6 w-6 items-center justify-center rounded-full bg-teal-700 text-[11px] font-semibold text-white"
                      : "flex h-6 w-6 items-center justify-center rounded-full border border-[var(--tp-line)] bg-white text-[11px] text-[var(--tp-muted)]"
                }
                aria-hidden
              >
                {i + 1}
              </span>
              {i < ladder.steps.length - 1 ? (
                <span
                  className={
                    step.reached
                      ? "mt-1 w-px flex-1 bg-teal-600/60"
                      : "mt-1 w-px flex-1 bg-[var(--tp-line)]"
                  }
                />
              ) : null}
            </div>
            <div className="min-w-0 flex-1 pb-2">
              <p
                className={
                  step.current
                    ? "text-sm font-semibold text-[var(--tp-navy)]"
                    : step.reached
                      ? "text-sm font-medium text-[var(--tp-ink)]"
                      : "text-sm text-[var(--tp-muted)]"
                }
              >
                {step.label}
                {step.current ? (
                  <span className="ml-2 text-[11px] font-medium uppercase tracking-wide text-teal-800">
                    Current
                  </span>
                ) : null}
              </p>
              <p className="mt-0.5 text-xs leading-relaxed text-[var(--tp-muted)]">
                {step.description}
              </p>
            </div>
          </li>
        ))}
      </ol>
      <p className="mt-2 border-t border-[var(--tp-line)] pt-3 text-xs leading-relaxed text-[var(--tp-teal)]">
        {ladder.safety_note}
      </p>
    </div>
  );
}
