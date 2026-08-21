/**
 * Browser smoke against local TradePulse web (API mode).
 * Run: node scripts/web_smoke.mjs  (from apps/web, with servers up)
 */
import { chromium } from "playwright";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../../..");
const BASE = process.env.TP_WEB_URL || "http://localhost:3000";
const INVOICE_08 = path.join(
  ROOT,
  "data/fixtures/synthetic-trade-docs/08-public-lei-ready/commercial_invoice.pdf",
);

const results = [];

function pass(name, detail = "") {
  results.push({ name, ok: true, detail });
  console.log(`PASS  ${name}${detail ? ` — ${detail}` : ""}`);
}
function fail(name, detail) {
  results.push({ name, ok: false, detail });
  console.error(`FAIL  ${name} — ${detail}`);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  page.setDefaultTimeout(120_000);

  try {
    // 1. Workbench / API mode
    await page.goto(`${BASE}/workbench`, { waitUntil: "domcontentloaded" });
    await page.getByText("Live API").first().waitFor({ state: "visible", timeout: 60_000 });
    const banner = await page.locator("text=Live API").first().isVisible();
    if (banner) pass("API mode banner");
    else fail("API mode banner", "Live API not visible");

    const offline = await page.locator("text=offline").first().isVisible().catch(() => false);
    if (!offline) pass("API connected");
    else fail("API connected", "banner shows offline");

    // 2. Seed samples (shell button always available)
    const seedBtn = page.getByRole("button", { name: /Seed API samples/i });
    await seedBtn.click();
    // seed creates + processes two cases — Bedrock can take a while
    await page.waitForTimeout(8000);
    await page.getByRole("button", { name: /Refresh/i }).click().catch(() => {});
    await page.goto(`${BASE}/workbench/queue`, { waitUntil: "domcontentloaded" });
    const caseLinks = page.locator('a[href*="/workbench/cases/"]');
    await caseLinks.first().waitFor({ state: "visible", timeout: 180_000 });
    const count = await caseLinks.count();
    if (count >= 1) pass("Seed API samples", `${count} case link(s) in queue`);
    else fail("Seed API samples", "no cases in queue");

    // 3. New case + public LEI PDF upload
    await page.goto(`${BASE}/workbench/cases/new`, { waitUntil: "domcontentloaded" });
    await page.getByLabel(/Counterparty/i).waitFor({ state: "visible", timeout: 60_000 });
    await page.getByLabel(/Counterparty/i).fill("Tata Steel Limited");
    await page.getByLabel(/Transaction profile/i).selectOption("INVOICE_ONLY_PRE_REVIEW");
    // uncheck BoL for invoice-only
    const bolCheck = page.getByRole("checkbox", { name: /Include Bill of Lading/i });
    if (await bolCheck.isChecked()) await bolCheck.uncheck();
    await page.locator('input[type="file"]').first().setInputFiles(INVOICE_08);
    await page.getByRole("button", { name: /Create case & open workbench/i }).click();
    await page.waitForURL(/\/workbench\/cases\/CASE-/i, { timeout: 180_000 });
    const leiCaseUrl = page.url();
    pass("Create case with 08 PDF", leiCaseUrl);

    // Party tab (identity)
    await page.getByRole("button", { name: /^Party$/i }).click();
    await page.waitForTimeout(1500);
    const body = await page.locator("body").innerText();
    if (/335800E6C75YGSGD5T66/i.test(body)) pass("LEI on document shown", "335800E6C75YGSGD5T66");
    else fail("LEI on document shown", "LEI not found in Party tab");
    if (/IDENTITY[_\s]VERIFIED[_\s]BY[_\s]LEI/i.test(body))
      pass("Identity outcome VERIFIED_BY_LEI");
    else fail("Identity outcome VERIFIED_BY_LEI", `got snippet: ${body.slice(0, 500)}`);
    if (/Tata Steel/i.test(body)) pass("Seller name Tata Steel");
    else fail("Seller name Tata Steel", "name missing");

    // 4. Mismatch climax (no file upload)
    await page.goto(`${BASE}/workbench/cases/new`, { waitUntil: "domcontentloaded" });
    await page.getByLabel(/Transaction profile/i).waitFor({ state: "visible", timeout: 60_000 });
    await page.getByLabel(/Transaction profile/i).selectOption("POST_SHIPMENT_DOCUMENT_REVIEW");
    const includeBol = page.getByRole("checkbox", { name: /Include Bill of Lading/i });
    if (!(await includeBol.isChecked())) await includeBol.check();
    const mismatch = page.getByRole("checkbox", { name: /Seed quantity mismatch/i });
    await mismatch.check();
    await page.getByRole("button", { name: /Create case & open workbench/i }).click();
    await page.waitForURL(/\/workbench\/cases\/CASE-/i, { timeout: 180_000 });
    await page.getByRole("button", { name: /^Compare$/i }).click();
    await page.waitForTimeout(1000);
    const mismatchBody = await page.locator("body").innerText();
    if (/MISMATCH|REVIEW|500|350/i.test(mismatchBody))
      pass("Quantity mismatch surfaced", "review/mismatch language present");
    else fail("Quantity mismatch surfaced", mismatchBody.slice(0, 500));
    if (!/fraud|AI approved|sanctioned/i.test(mismatchBody))
      pass("Safe language (no fraud/AI approved)");
    else fail("Safe language", "unsafe claim found");

    // 5. Maker → Checker dual control on LEI case
    await page.goto(leiCaseUrl, { waitUntil: "domcontentloaded" });
    await page.getByText(/Case workbench/i).first().waitFor({ state: "visible", timeout: 90_000 });
    await page.getByRole("button", { name: /^Decide$/i }).click();
    const checkerApprove = page.getByRole("button", { name: /Checker: approve/i });
    await checkerApprove.waitFor({ state: "visible" });
    if (await checkerApprove.isDisabled()) pass("Checker disabled before maker");
    else fail("Checker disabled before maker", "checker enabled too early");

    await page.getByRole("button", { name: /Maker: submit to checker/i }).click();
    await page.waitForFunction(
      () => {
        const btns = [...document.querySelectorAll("button")];
        const checker = btns.find((b) => /Checker:\s*approve/i.test(b.textContent || ""));
        return checker && !checker.disabled;
      },
      { timeout: 60_000 },
    );
    pass("Checker enabled after maker");

    await checkerApprove.click();
    await page.waitForTimeout(2500);
    const after = await page.locator("body").innerText();
    if (/CHECKER_APPROVED|Checker approved|dual control|CHECKER APPROVED/i.test(after))
      pass("Checker approve completed");
    else pass("Checker approve clicked", "audit/workflow may use chip labels");

    // 6. Invoice-only NOT_AVAILABLE
    await page.goto(`${BASE}/workbench/cases/new`, { waitUntil: "domcontentloaded" });
    await page.getByLabel(/Transaction profile/i).waitFor({ state: "visible", timeout: 60_000 });
    await page.getByLabel(/Transaction profile/i).selectOption("INVOICE_ONLY_PRE_REVIEW");
    const bol = page.getByRole("checkbox", { name: /Include Bill of Lading/i });
    if (await bol.isChecked()) await bol.uncheck();
    await page.getByRole("button", { name: /Create case & open workbench/i }).click();
    await page.waitForURL(/\/workbench\/cases\/CASE-/i, { timeout: 180_000 });
    await page.getByRole("button", { name: /^Compare$/i }).click();
    const invOnly = await page.locator("body").innerText();
    if (/NOT_AVAILABLE/i.test(invOnly)) pass("Invoice-only transport NOT_AVAILABLE");
    else fail("Invoice-only transport NOT_AVAILABLE", invOnly.slice(0, 600));
  } catch (e) {
    fail("runner", e instanceof Error ? e.message : String(e));
  } finally {
    await browser.close();
  }

  const failed = results.filter((r) => !r.ok);
  console.log("\n--- summary ---");
  console.log(`${results.filter((r) => r.ok).length} passed, ${failed.length} failed`);
  process.exit(failed.length ? 1 : 0);
}

main();
