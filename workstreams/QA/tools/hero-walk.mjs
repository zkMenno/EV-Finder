// QA hero walk (A-35, A-36): every country × profile × budget at 360 and 1280 px.
// Usage: copy into apps/web (so @playwright/test resolves), start a production build, then
//   node hero-walk.mjs http://localhost:3200 ../../audits/A-36-screens > walk.json
// Prints one JSON record per run; screenshots are small PNGs (top of the result list only).
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const [base = "http://localhost:3200", out = "screens", countries = "nl,de,fr,es,it", lang = "en"] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const PROFILES = {
  roadtripper: "role=only&trips=monthly&charge=home",
  daily: "role=main&trips=never&charge=home",
  runabout: "role=second&charge=home",
  kerbside: "role=only&trips=often&charge=public_only&area=city",
};
const BUDGETS = [15000, 35000];

const browser = await chromium.launch();
const runs = [];
for (const cc of countries.split(",")) {
  for (const [name, qs] of Object.entries(PROFILES)) {
    for (const budget of BUDGETS) {
      for (const width of [1280, 360]) {
        const page = await browser.newPage({ viewport: { width, height: 900 } });
        const errors = [];
        page.on("pageerror", (e) => errors.push(String(e)));
        const url = `${base}/${cc}/${lang}?${qs}&budget=${budget}`;
        const res = await page.goto(url);
        await page.getByTestId("hero-results").first().waitFor();
        await page.waitForTimeout(300);
        const cards = await page.getByTestId("hero-card").evaluateAll((els) =>
          els.map((e) => {
            const q = (id) => e.querySelector(`[data-testid="${id}"]`);
            const link = q("hero-listings");
            return {
              rank: e.getAttribute("data-rank"),
              variant: e.getAttribute("data-variant"),
              price: e.getAttribute("data-price"),
              basis: e.getAttribute("data-price-basis"),
              title: (e.querySelector("h3, h4")?.textContent ?? "").trim(),
              why: (q("hero-why")?.textContent ?? "").trim(),
              winter: (q("hero-winter")?.textContent ?? "").trim(),
              priceText: (q("hero-price")?.textContent ?? "").trim(),
              monthly: (q("hero-monthly")?.textContent ?? "").trim(),
              listings: link?.getAttribute("href") ?? null,
              inShortlist: !!e.closest('[data-testid="hero-shortlist"]'),
            };
          }),
        );
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        const empty = await page.getByTestId("hero-no-priced").count();
        // The result list, not the top of the page: scroll it into view and capture one screen of it.
        const results = page.getByTestId("hero-count").first();
        await results.evaluate((el) => el.scrollIntoView({ block: "start" }));
        await page.screenshot({ path: `${out}/hero-${cc}-${name}-${budget / 1000}k-${width}.png`, fullPage: false });
        const monthlyAnywhere = await page.getByTestId("hero-monthly").allInnerTexts();
        runs.push({ cc, profile: name, budget, width, status: res?.status(), finalPath: new URL(page.url()).pathname, overflow, errors, noPricedNotice: empty, monthlyAnywhere, cards });
        await page.close();
      }
    }
  }
}
await browser.close();
console.log(JSON.stringify(runs));
