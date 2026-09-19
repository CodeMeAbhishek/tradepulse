// The page's hard constraint is that a CXO can read it in about a minute.
// Counting words by eye does not survive a copy edit, so it is asserted here.
//
//   node scripts/words.cjs [url] [limit]
const { chromium } = require("C:/Users/athar/OneDrive/Desktop/d7 work/d7 website/dimension-seven/node_modules/playwright");

const URL = process.argv[2] || "http://localhost:3210/";
const LIMIT = Number(process.argv[3] || 450);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: "networkidle", timeout: 60000 });
  // <details> bodies are part of the reading load even while collapsed.
  await page.evaluate(() => document.querySelectorAll("details").forEach((d) => (d.open = true)));
  const text = await page.evaluate(() => document.body.innerText);
  await browser.close();

  const words = text.split(/\s+/).filter(Boolean);
  const over = words.length > LIMIT;
  console.log(`${words.length} words (limit ${LIMIT})${over ? "  OVER" : "  ok"}`);
  process.exit(over ? 1 : 0);
})();
