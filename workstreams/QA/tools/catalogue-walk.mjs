// QA catalogue walk (A-36): provenance in Nerd mode, parked price modes, /learn, languages, themes.
// Usage: copy into apps/web (so @playwright/test resolves), start a production build, then
//   node catalogue-walk.mjs http://localhost:3200 ../../audits/A-36-screens > catalogue.json
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const [base = "http://localhost:3200", out = "screens"] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const report = {};
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));

// 1. Nerd mode on variant + generation pages: how many numbers show their source line, and does it
//    name a licence and a retrieval date (A-35 S3, REVIEW D7)?
const variantPages = [
  "/nl/en/ev/hyundai/ioniq-5/gen1/77kwh-awd",
  "/de/en/ev/tesla/model-y/juniper/long-range-awd",
  "/fr/en/ev/renault/zoe/ph1",
  "/nl/en/ev/kia/ev6/gen1",
  "/it/en/ev/fiat/500e/332",
];
report.nerd = [];
for (const p of variantPages) {
  const res = await page.goto(`${base}${p}?level=nerd`);
  await page.waitForTimeout(400);
  const nerd = await page.getByTestId("num-nerd").allInnerTexts();
  report.nerd.push({
    path: p,
    status: res?.status(),
    nerdNodes: nerd.length,
    withLicence: nerd.filter((t) => /licen[cs]e|CC BY|ODbL|public domain|terms/i.test(t)).length,
    withDate: nerd.filter((t) => /\d{4}-\d{2}-\d{2}|\d{1,2} [A-Z][a-z]{2,8} \d{4}/.test(t)).length,
    sample: nerd.slice(0, 10),
  });
  if (p.includes("ioniq-5")) await page.screenshot({ path: `${out}/cat-variant-ioniq5-nerd.png` });
}

// 2. Parked price modes: Buy / Loan / Lease toggle (A-35 S4).
report.priceModes = [];
for (const p of ["/nl/en", "/nl/en?pay=lease", "/nl/en/ev/hyundai/ioniq-5/gen1", "/nl/en/compare"]) {
  await page.goto(`${base}${p}`);
  await page.waitForTimeout(300);
  const lease = await page.getByText(/^Lease$/).count();
  const radios = await page.getByRole("radio", { name: /lease/i }).count();
  const buttons = await page.getByRole("button", { name: /lease/i }).count();
  report.priceModes.push({ path: p, leaseText: lease, leaseRadios: radios, leaseButtons: buttons });
}

// 3. /learn: which guides are listed, and does each say "draft" (A-35 S5)?
await page.goto(`${base}/nl/en/learn`);
const learnLinks = await page.locator("main a[href*='/learn/']").evaluateAll((els) => [...new Set(els.map((e) => e.getAttribute("href")))]);
report.learn = [];
for (const href of learnLinks) {
  const res = await page.goto(`${base}${href}`);
  const text = await page.locator("main").innerText();
  report.learn.push({ href, status: res?.status(), draft: /draft|review needed/i.test(text), words: text.split(/\s+/).length });
}
await page.goto(`${base}/nl/en/learn`);
await page.screenshot({ path: `${out}/cat-learn.png` });

// 4. Languages (launch scope rev 2, Decision 082: English only): what do non-English routes do,
//    and does the header still offer a language picker?
report.languages = [];
for (const p of ["/nl/nl", "/de/de", "/fr/fr", "/es/es", "/it/it", "/be/fr", "/uk/en", "/be/en", "/es/en", "/it/en"]) {
  const res = await page.goto(`${base}${p}`);
  const lang = await page.locator("html").getAttribute("lang");
  const picker = await page.getByLabel("Language").count();
  report.languages.push({ path: p, status: res?.status(), finalPath: new URL(page.url()).pathname, htmlLang: lang, languagePicker: picker });
}

// 5. Dark theme screenshot of a generation page (Compare + differences only: e2e/diff-only.spec.ts).
await page.emulateMedia({ colorScheme: "dark" });
await page.goto(`${base}/nl/en/ev/hyundai/ioniq-5/gen1`);
await page.screenshot({ path: `${out}/cat-generation-dark.png` });
report.errors = errors;
await browser.close();
console.log(JSON.stringify(report, null, 1));
