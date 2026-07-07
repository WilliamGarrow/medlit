// MedLit screenshot pipeline: retina captures of the key screens.
// Usage: node capture.js <output-dir>
const { chromium } = require("playwright");
const path = require("path");

const BASE = "https://medlit.williamgarrow.com";
const OUT = process.argv[2] || ".";

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });
  const page = await ctx.newPage();

  // 1. Landing (public)
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(OUT, "landing.png") });
  console.log("landing.png");

  // 2. Enter the demo -> dashboard
  await page.click("text=Enter the demo");
  await page.waitForURL(`${BASE}/`, { timeout: 15000 });
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: path.join(OUT, "dashboard.png") });
  console.log("dashboard.png");

  // 3. Patient detail (David Thompson: complex elderly patient)
  await page.goto(`${BASE}/patients/david_thompson`, {
    waitUntil: "networkidle",
  });
  await page.screenshot({ path: path.join(OUT, "patient-detail.png") });
  console.log("patient-detail.png");

  // 4. Medication explanation with reading levels (real LLM call, patient)
  const learnMore = page.locator("text=Learn more").first();
  if (await learnMore.isVisible().catch(() => false)) {
    await learnMore.click();
    // Wait for generation to finish (spinner detaches), not just begin
    await page
      .waitForSelector("text=Generating explanation", {
        state: "detached",
        timeout: 90000,
      })
      .catch(() => {});
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: path.join(OUT, "explanation.png"),
      fullPage: false,
    });
    console.log("explanation.png");
  } else {
    console.log("explanation skipped: no Learn more button found");
  }

  // 5. About / how-it-works (public)
  await page.goto(`${BASE}/about`, { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(OUT, "about.png"), fullPage: false });
  console.log("about.png");

  await browser.close();
})();
