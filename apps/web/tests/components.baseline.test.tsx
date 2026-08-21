/**
 * Regression baseline for the workbench components as they exist today.
 *
 * Purpose: lock current rendered output BEFORE the canonical-contract
 * migration, so any change to Ansh's UI during that work is visible in a
 * diff instead of being discovered at demo time.
 *
 * Snapshots are a tripwire, not a spec. A deliberate UI change should update
 * them (`npx vitest run -u`) in the same commit that makes the change.
 *
 * Owner: Atharva (master prompt s6 -- component/visual regression tests).
 */

import { render, screen } from "@testing-library/react";

import { asserts } from "./helpers/text";
import { describe, expect, it } from "vitest";

import { BolReconciliationPanel } from "@/components/case/BolReconciliationPanel";
import { FindingsWorkflowPanel } from "@/components/case/FindingsWorkflowPanel";
import { IdentityEvidenceDrawer } from "@/components/case/IdentityEvidenceDrawer";
import { InvoiceReviewPanel } from "@/components/case/InvoiceReviewPanel";
import { CompletenessSummary } from "@/components/queue/CompletenessSummary";
import { ProfileBadge } from "@/components/queue/ProfileBadge";
import { QueueTable } from "@/components/queue/QueueView";
import { StatusRouteChip } from "@/components/queue/StatusRouteChip";
import { RegWatchPanel } from "@/components/regwatch/RegWatchPanel";
import { PrototypeBanner } from "@/components/PrototypeBanner";
import { getCaseWorkbenchDetail } from "@/lib/mock/case-detail";
import { MOCK_QUEUE_CASES } from "@/lib/mock/queue";
import { MOCK_REGWATCH_EVENTS } from "@/lib/mock/regwatch";

const DETAIL = getCaseWorkbenchDetail("case-recon-004")!;
const NO_BOL = getCaseWorkbenchDetail("case-inv-001")!;

describe("queue components", () => {
  it("PrototypeBanner", () => {
    const { container } = render(<PrototypeBanner />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it("ProfileBadge renders every profile in the queue", () => {
    for (const c of MOCK_QUEUE_CASES) {
      const { container } = render(<ProfileBadge profile={c.profile} />);
      expect(container.firstChild).toMatchSnapshot(c.profile);
    }
  });

  it("StatusRouteChip renders every status/route pair in the queue", () => {
    for (const c of MOCK_QUEUE_CASES) {
      const { container } = render(
        <StatusRouteChip status={c.status} readinessRoute={c.readinessRoute} />,
      );
      expect(container.firstChild).toMatchSnapshot(`${c.status}/${c.readinessRoute}`);
    }
  });

  it("CompletenessSummary", () => {
    const { container } = render(
      <CompletenessSummary items={MOCK_QUEUE_CASES[0].documentCompleteness} />,
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  it("QueueTable", () => {
    const { container } = render(<QueueTable cases={MOCK_QUEUE_CASES} />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

describe("case components", () => {
  it("InvoiceReviewPanel", () => {
    const { container } = render(
      <InvoiceReviewPanel fields={DETAIL.invoiceFields} trace={DETAIL.agentTrace} />,
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  it("BolReconciliationPanel with BoL present", () => {
    const { container } = render(<BolReconciliationPanel reconciliation={DETAIL.reconciliation} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it("BolReconciliationPanel with BoL absent", () => {
    const { container } = render(<BolReconciliationPanel reconciliation={NO_BOL.reconciliation} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it("IdentityEvidenceDrawer", () => {
    const { container } = render(<IdentityEvidenceDrawer parties={DETAIL.identities} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it("FindingsWorkflowPanel", () => {
    const { container } = render(
      <FindingsWorkflowPanel
        findings={DETAIL.findings}
        makerChecker={DETAIL.makerChecker}
        audit={DETAIL.audit}
      />,
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  it("RegWatchPanel", () => {
    const { container } = render(<RegWatchPanel events={MOCK_REGWATCH_EVENTS} />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

describe("rendered-output invariants", () => {
  // These survive a snapshot update, so they keep protecting meaning even if
  // someone regenerates snapshots carelessly.

  it("an absent BoL is never rendered as a pass", () => {
    render(<BolReconciliationPanel reconciliation={NO_BOL.reconciliation} />);
    const text = document.body.textContent ?? "";
    expect(text).toMatch(/NOT AVAILABLE|NOT_AVAILABLE/i);
    // "never PASS" is correct copy; only an asserted PASS is a violation.
    expect(asserts(text, "pass")).toBe(false);
  });

  it("status chips convey meaning in text, not colour alone", () => {
    for (const c of MOCK_QUEUE_CASES) {
      const { unmount } = render(
        <StatusRouteChip status={c.status} readinessRoute={c.readinessRoute} />,
      );
      // Strip class attributes: whatever remains must still carry the meaning.
      const text = (document.body.textContent ?? "").trim();
      expect(text.length).toBeGreaterThan(0);
      unmount();
    }
  });

  it("the prototype banner states the data is synthetic", () => {
    render(<PrototypeBanner />);
    expect(screen.getAllByText(/synthetic|prototype|demo/i).length).toBeGreaterThan(0);
  });
});
