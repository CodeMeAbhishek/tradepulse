/**
 * Automated accessibility checks for the workbench components.
 *
 * A compliance officer operating this all day may be keyboard-only, and the
 * product's own UI rules require that colour is never the sole meaning channel
 * and that evidence is reachable. axe catches the mechanical subset of that;
 * the assertions below cover what axe cannot see.
 *
 * Owner: Atharva (master prompt s6 -- accessibility and keyboard paths).
 */

import { render } from "@testing-library/react";
import { axe } from "vitest-axe";
import { describe, expect, it } from "vitest";

import { BolReconciliationPanel } from "@/components/case/BolReconciliationPanel";
import { FindingsWorkflowPanel } from "@/components/case/FindingsWorkflowPanel";
import { IdentityEvidenceDrawer } from "@/components/case/IdentityEvidenceDrawer";
import { InvoiceReviewPanel } from "@/components/case/InvoiceReviewPanel";
import { QueueTable } from "@/components/queue/QueueView";
import { RegWatchPanel } from "@/components/regwatch/RegWatchPanel";
import { getCaseWorkbenchDetail } from "@/lib/mock/case-detail";
import { MOCK_QUEUE_CASES } from "@/lib/mock/queue";
import { MOCK_REGWATCH_EVENTS } from "@/lib/mock/regwatch";

const DETAIL = getCaseWorkbenchDetail("case-recon-004")!;

/**
 * jsdom has no layout or canvas, so axe cannot evaluate colour contrast here --
 * it would skip the rule and still report "no violations", turning an
 * unavailable check into a pass. We disable it explicitly instead, so the gap
 * is visible rather than silent. Contrast must be verified in a real browser;
 * see the keyboard/meaning assertions below for what is enforced in CI.
 */
const AXE_OPTIONS = {
  rules: {
    "color-contrast": { enabled: false },
  },
} as const;

async function auditable(ui: React.ReactElement) {
  const { container } = render(ui);
  return axe(container, AXE_OPTIONS);
}

describe("axe audit", () => {
  it("QueueTable has no detectable violations", async () => {
    expect(await auditable(<QueueTable cases={MOCK_QUEUE_CASES} />)).toHaveNoViolations();
  });

  it("InvoiceReviewPanel has no detectable violations", async () => {
    expect(
      await auditable(
        <InvoiceReviewPanel fields={DETAIL.invoiceFields} trace={DETAIL.agentTrace} />,
      ),
    ).toHaveNoViolations();
  });

  it("BolReconciliationPanel has no detectable violations", async () => {
    expect(
      await auditable(<BolReconciliationPanel reconciliation={DETAIL.reconciliation} />),
    ).toHaveNoViolations();
  });

  it("IdentityEvidenceDrawer has no detectable violations", async () => {
    expect(
      await auditable(<IdentityEvidenceDrawer parties={DETAIL.identities} />),
    ).toHaveNoViolations();
  });

  it("FindingsWorkflowPanel has no detectable violations", async () => {
    expect(
      await auditable(
        <FindingsWorkflowPanel
          findings={DETAIL.findings}
          makerChecker={DETAIL.makerChecker}
          audit={DETAIL.audit}
        />,
      ),
    ).toHaveNoViolations();
  });

  it("RegWatchPanel has no detectable violations", async () => {
    expect(
      await auditable(<RegWatchPanel events={MOCK_REGWATCH_EVENTS} />),
    ).toHaveNoViolations();
  });
});

describe("keyboard and meaning -- what axe cannot see", () => {
  it("the identity disclosure is a real button, reachable by keyboard", () => {
    const { container } = render(<IdentityEvidenceDrawer parties={DETAIL.identities} />);
    const toggles = container.querySelectorAll("button[aria-expanded]");
    expect(toggles.length).toBe(DETAIL.identities.length);
    for (const toggle of toggles) {
      // A div with onClick would not be focusable; a real button always is.
      expect(toggle.tagName).toBe("BUTTON");
      expect(toggle.getAttribute("type")).toBe("button");
    }
    // The drawer opens the first party by default, so the most relevant
    // evidence is on screen with no interaction at all.
    const expanded = [...toggles].filter(
      (t) => t.getAttribute("aria-expanded") === "true",
    );
    expect(expanded).toHaveLength(1);
    expect(expanded[0]).toBe(toggles[0]);
  });

  it("identity evidence is reachable within one interaction", async () => {
    const { container } = render(<IdentityEvidenceDrawer parties={DETAIL.identities} />);
    const toggle = container.querySelector(
      "button[aria-expanded]",
    ) as HTMLButtonElement;
    const { default: userEvent } = await import("@testing-library/user-event");

    // Every fixture case currently carries a single SELLER party, which the
    // drawer opens by default -- so exercise collapse, then re-expand.
    await userEvent.click(toggle);
    expect(toggle.getAttribute("aria-expanded")).toBe("false");

    await userEvent.click(toggle);
    expect(toggle.getAttribute("aria-expanded")).toBe("true");

    // The raw document name is the evidence a reviewer compares against the
    // normalized one; expanding a party must reveal it.
    expect(container.textContent).toContain(DETAIL.identities[0].rawName);
  });

  it("every status conveys meaning as text, not colour alone", () => {
    const { container } = render(<QueueTable cases={MOCK_QUEUE_CASES} />);
    // Strip every class attribute, i.e. remove all colour, and check the
    // readiness route is still stated in words.
    for (const el of container.querySelectorAll("[class]")) el.removeAttribute("class");
    const text = container.textContent ?? "";
    for (const c of MOCK_QUEUE_CASES) {
      expect(text.toLowerCase()).toContain(
        c.readinessRoute.replaceAll("_", " ").toLowerCase(),
      );
    }
  });
});

describe("keyboard focus is reachable and indicated", () => {
  /**
   * jsdom applies no stylesheet, so it cannot prove the ring *renders*. It can
   * prove the two things that make the ring reachable at all: that controls
   * receive focus by keyboard, and that the global rule exists in the source
   * that ships. Visual confirmation belongs in a real browser.
   */

  it("Tab moves focus onto the identity disclosure control", async () => {
    const { container } = render(<IdentityEvidenceDrawer parties={DETAIL.identities} />);
    const { default: userEvent } = await import("@testing-library/user-event");

    await userEvent.tab();

    const toggle = container.querySelector("button[aria-expanded]");
    expect(document.activeElement).toBe(toggle);
  });

  it("the focused control can be operated with the keyboard alone", async () => {
    const { container } = render(<IdentityEvidenceDrawer parties={DETAIL.identities} />);
    const { default: userEvent } = await import("@testing-library/user-event");
    const toggle = container.querySelector(
      "button[aria-expanded]",
    ) as HTMLButtonElement;

    await userEvent.tab();
    expect(toggle.getAttribute("aria-expanded")).toBe("true");

    await userEvent.keyboard("{Enter}");
    expect(toggle.getAttribute("aria-expanded")).toBe("false");

    await userEvent.keyboard(" ");
    expect(toggle.getAttribute("aria-expanded")).toBe("true");
  });

  it("a focus-visible rule ships in the global stylesheet", async () => {
    const { readFile } = await import("node:fs/promises");
    const { resolve } = await import("node:path");
    const css = await readFile(resolve(process.cwd(), "app/globals.css"), "utf-8");

    // Guards against the ring being deleted or downgraded to :focus, which
    // would flash on every mouse click and get removed again.
    expect(css).toContain(":focus-visible");
    expect(css).toMatch(/outline:\s*2px solid/);
    expect(css).toContain("forced-colors");
    expect(css).not.toMatch(/outline:\s*none/);
  });
});
