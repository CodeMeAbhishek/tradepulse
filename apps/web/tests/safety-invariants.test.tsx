/**
 * Executable form of the TradePulse safety rules.
 *
 * Sources: .cursor/rules/00-tradepulse-core.mdc, 02-agentic-safety.mdc,
 * 03-identity-lei-vlei.mdc, and docs/adr/001-canonical-contracts-addendum.md.
 *
 * These assert product invariants, not styling. A failure here means the
 * workbench is about to tell a compliance officer something untrue.
 *
 * Owner: Atharva (ADR 001 s1.3 -- contract tests).
 */

import { describe, expect, it } from "vitest";

import { assertedOccurrences } from "./helpers/text";
import { getCaseWorkbenchDetail } from "@/lib/mock/case-detail";
import { MOCK_QUEUE_CASES } from "@/lib/mock/queue";
import { MOCK_REGWATCH_EVENTS } from "@/lib/mock/regwatch";
import {
  documentStateLabel,
  findingOutcomeLabel,
  identityOutcomeLabel,
  profileLabel,
  readinessLabel,
  vleiStatusLabel,
} from "@/lib/mock/labels";

const CASE_IDS = MOCK_QUEUE_CASES.map((c) => c.id);
const DETAILS = CASE_IDS.map((id) => getCaseWorkbenchDetail(id)).filter(
  (d): d is NonNullable<ReturnType<typeof getCaseWorkbenchDetail>> => d !== null,
);

/** Every user-visible string in the demo fixtures, flattened. */
function allDemoText(): string {
  return JSON.stringify({ MOCK_QUEUE_CASES, DETAILS, MOCK_REGWATCH_EVENTS });
}

describe("prohibited claim language", () => {
  // 00-tradepulse-core.mdc: never claim AI approved / sanctioned / fraud / goods verified.
  const FORBIDDEN_PHRASES = [
    "fraud confirmed",
    "confirmed fraud",
    "ai approved",
    "ai-approved",
    "goods verified",
    "verified goods",
    "sanctions confirmed",
    "confirmed sanction",
    "cleared by ai",
    "customs cleared",
    "let export order",
  ];

  it("no fixture text asserts a prohibited compliance claim", () => {
    const haystack = allDemoText().toLowerCase();
    const found = FORBIDDEN_PHRASES.filter(
      (p) => assertedOccurrences(haystack, p) > 0,
    );
    expect(found).toEqual([]);
  });

  it("the negation guard itself works", () => {
    // Guards against the check silently passing everything.
    expect(assertedOccurrences("the entity is fraud confirmed", "fraud confirmed")).toBe(1);
    expect(assertedOccurrences("this is not fraud confirmed", "fraud confirmed")).toBe(0);
  });

  it("does not describe an entity as simply 'sanctioned'", () => {
    const haystack = allDemoText().toLowerCase();
    // "potential match" / "screening" language is fine; a bare verdict is not.
    expect(haystack).not.toMatch(/\bis sanctioned\b/);
    expect(haystack).not.toMatch(/\bentity sanctioned\b/);
  });
});

describe("unavailable data never becomes a pass", () => {
  // 00-tradepulse-core.mdc: DATA_UNAVAILABLE / NOT_AVAILABLE / NOT_APPLICABLE
  // must never be rendered as PASS.
  const NON_PASS = ["DATA_UNAVAILABLE", "NOT_AVAILABLE", "NOT_APPLICABLE"] as const;

  it("non-pass outcomes keep a distinct label from PASS", () => {
    const passLabel = findingOutcomeLabel("PASS");
    for (const outcome of NON_PASS) {
      expect(findingOutcomeLabel(outcome)).not.toBe(passLabel);
    }
  });

  it("a case with no BoL never reports a passing reconciliation", () => {
    for (const detail of DETAILS) {
      if (!detail.reconciliation.bolPresent) {
        expect(detail.reconciliation.outcome).not.toBe("PASS");
      }
    }
  });

  it("every finding that cites unavailable data is not PASS", () => {
    for (const detail of DETAILS) {
      for (const finding of detail.findings) {
        const text = `${finding.title} ${finding.detail ?? ""}`.toLowerCase();
        if (text.includes("unavailable") || text.includes("not configured")) {
          expect(finding.outcome).not.toBe("PASS");
        }
      }
    }
  });
});

describe("LEI and VLEI honesty", () => {
  // 03-identity-lei-vlei.mdc
  it("a fixture VLEI is never labelled VERIFIED_LIVE", () => {
    for (const detail of DETAILS) {
      for (const party of detail.identities) {
        if (party.vleiStatus === "VERIFIED_LIVE") {
          // Only a trusted live verifier may produce this; no demo fixture may.
          expect(party.source.toLowerCase()).not.toContain("fixture");
          expect(party.source.toLowerCase()).not.toContain("mock");
          expect(party.source.toLowerCase()).not.toContain("demo");
        }
      }
    }
  });

  it("VERIFIED_FIXTURE parties carry a visible synthetic marker", () => {
    for (const detail of DETAILS) {
      for (const party of detail.identities) {
        if (party.vleiStatus === "VERIFIED_FIXTURE") {
          const marker = `${party.vleiLabel} ${party.source}`.toUpperCase();
          expect(marker).toMatch(/SYNTHETIC|DEMO|FIXTURE/);
        }
      }
    }
  });

  it("an identity with no LEI is never reported as verified by LEI", () => {
    for (const detail of DETAILS) {
      for (const party of detail.identities) {
        if (party.lei === null) {
          expect(party.identityOutcome).not.toBe("IDENTITY_VERIFIED_BY_LEI");
        }
      }
    }
  });

  it("a non-exact GLEIF candidate never yields IDENTITY_VERIFIED_BY_LEI", () => {
    for (const detail of DETAILS) {
      for (const party of detail.identities) {
        const hasExact = party.gleifCandidates.some((c) => c.isExactDocumentMatch);
        if (!hasExact && party.gleifCandidates.length > 0) {
          expect(party.identityOutcome).not.toBe("IDENTITY_VERIFIED_BY_LEI");
        }
      }
    }
  });

  it("VLEI status and identity outcome stay separate concepts", () => {
    // ADR 001 s3.2 -- a VLEI may be NOT_CONFIGURED while identity is LEI-verified.
    const labels = new Set(
      DETAILS.flatMap((d) => d.identities).map((p) => vleiStatusLabel(p.vleiStatus)),
    );
    for (const label of labels) {
      expect(label).not.toMatch(/IDENTITY_/);
    }
  });
});

describe("bounded agent trace", () => {
  // 02-agentic-safety.mdc: max 3 rounds; unresolved -> review required.
  it("no case exceeds 3 agent rounds", () => {
    for (const detail of DETAILS) {
      const rounds = detail.agentTrace.map((t) => t.round);
      for (const round of rounds) {
        expect(round).toBeLessThanOrEqual(3);
      }
    }
  });

  it("does not expose chain-of-thought style narration", () => {
    const haystack = allDemoText().toLowerCase();
    for (const phrase of ["let me think", "thinking:", "chain of thought", "i should"]) {
      expect(haystack).not.toContain(phrase);
    }
  });
});

describe("label coverage", () => {
  // A missing label renders "undefined" to a compliance officer.
  it("every profile in the queue has a human label", () => {
    for (const c of MOCK_QUEUE_CASES) {
      expect(profileLabel(c.profile)).toBeTruthy();
      expect(profileLabel(c.profile)).not.toContain("undefined");
    }
  });

  it("every readiness route in the queue has a human label", () => {
    for (const c of MOCK_QUEUE_CASES) {
      expect(readinessLabel(c.readinessRoute)).toBeTruthy();
      expect(readinessLabel(c.readinessRoute)).not.toContain("undefined");
    }
  });

  it("every document state and identity outcome has a human label", () => {
    for (const c of MOCK_QUEUE_CASES) {
      for (const item of c.documentCompleteness) {
        expect(documentStateLabel(item.state)).toBeTruthy();
      }
    }
    for (const detail of DETAILS) {
      for (const party of detail.identities) {
        expect(identityOutcomeLabel(party.identityOutcome)).toBeTruthy();
        expect(identityOutcomeLabel(party.identityOutcome)).not.toContain("undefined");
      }
    }
  });
});

describe("demo data is labelled synthetic", () => {
  // PRD s9 -- data honesty.
  it("every queue case declares a synthetic data source", () => {
    for (const c of MOCK_QUEUE_CASES) {
      expect(c.dataSourceLabel).toBe("SYNTHETIC_DEMO");
    }
  });
});
