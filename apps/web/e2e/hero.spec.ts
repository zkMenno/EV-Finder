import { expect, test } from "@playwright/test";
import { SERVED_ROUTES } from "./langs";
import { HAS_SCORES, HAS_USED_PRICES, NO_SCORES_REASON } from "./release";

// T-080: the landing-page hero ranks the published release for each profile.
const PROFILES: [string, string][] = [
  ["road-tripper", "role=only&trips=monthly&charge=home"],
  ["daily driver", "role=main&trips=never&charge=home"],
  ["runabout", "role=second&charge=home"],
  ["kerbside charger", "role=only&trips=often&charge=public_only&area=city"],
];

for (const [name, qs] of PROFILES) {
  test(`hero: ${name} gets a top 10 with the first 5 as the shortlist`, async ({ page }) => {
    test.skip(!HAS_SCORES, NO_SCORES_REASON);
    await page.goto(`/nl/en?${qs}`);
    await expect(page.getByTestId("hero-card")).toHaveCount(10);
    // Decision 064: the shortlist holds priced cars only (up to 5); unpriced cars follow under "more".
    const short = page.getByTestId("hero-shortlist").getByTestId("hero-card");
    const n = await short.count();
    // The shortlist is as long as the priced cars allow: min(5, priced cards in the top 10), since
    // priced cars come first. With used prices in the release, no profile without a budget is empty.
    const bases = await page.getByTestId("hero-card").evaluateAll((els) => els.map((e) => e.getAttribute("data-price-basis")));
    expect(n).toBe(Math.min(5, bases.filter((b) => b !== "none").length));
    if (HAS_USED_PRICES) expect(n, "a release with used prices has priced cars for this profile").toBeGreaterThan(0);
    for (const basis of await short.evaluateAll((els) => els.map((e) => e.getAttribute("data-price-basis")))) expect(basis).not.toBe("none");
    // After the shortlist: more priced cars ("hero-more"), then unpriced cars without a place number.
    const more = await page.getByTestId("hero-more").getByTestId("hero-card").count();
    const noPrice = page.getByTestId("hero-no-price").getByTestId("hero-card");
    expect(more + (await noPrice.count())).toBe(10 - n);
    for (const c of await noPrice.evaluateAll((els) => els.map((e) => [e.getAttribute("data-price-basis"), e.getAttribute("data-rank")]))) expect(c).toEqual(["none", null]);
    await expect(page.getByTestId("hero-why").first()).not.toBeEmpty();
  });
}

// T-132: one question per screen; the step is in the URL and Back goes to the previous question.
test("hero: one question at a time, from country to the top 10", async ({ page }) => {
  await page.goto("/nl/en");
  const hero = page.getByTestId("hero");
  await expect(hero).toHaveAttribute("data-step", "country");
  await expect(page.getByTestId("hero-road").locator('[aria-current="step"]')).toContainText("Country");
  await expect(page.getByRole("radio", { name: "Netherlands" })).toBeChecked();
  await expect(page.getByRole("group", { name: "Where are you buying?" })).toBeVisible();
  await page.getByText("Netherlands", { exact: true }).click();
  await expect(hero).toHaveAttribute("data-step", "role");
  await expect(page).toHaveURL(/q=role/);
  // The heading of the new question takes focus (screen readers hear it, keyboard starts there).
  await expect(page.getByRole("heading", { name: "What will this car be?" })).toBeFocused();
  await expect(page.getByTestId("hero-trail")).toContainText("Netherlands");
  await page.getByText("Our main car").click();
  await expect(hero).toHaveAttribute("data-step", "trips");
  await expect(page).toHaveURL(/role=main/);
  await expect(page.getByTestId("hero-stepline")).toHaveText("Step 2 of 3 · question 2 of 4");
  // Browser back = previous question, answer kept.
  await page.goBack();
  await expect(hero).toHaveAttribute("data-step", "role");
  await expect(page.getByRole("radio", { name: "Our main car" })).toBeChecked();
  await page.goForward();
  await expect(hero).toHaveAttribute("data-step", "trips");
  await page.getByText("A few times a year").click();
  await expect(hero).toHaveAttribute("data-step", "charge");
  await page.getByText("At home", { exact: true }).click();
  await expect(hero).toHaveAttribute("data-step", "area");
  await page.getByText("Town or suburb").click();
  await expect(hero).toHaveAttribute("data-step", "budget");
  // After the driving questions the trail shows the profile name, not four pills.
  await expect(page.getByTestId("hero-trail-profile")).toContainText("Road-tripper");
  await expect(page.getByTestId("hero-trail").getByRole("button")).toHaveCount(2);
  await page.getByTestId("hero-budget-30000").click();
  await expect(page.getByTestId("hero-budget-30000")).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByTestId("hero-monthly")).toContainText(/≈ .+ a month|official typical loan rate/);
  await page.getByTestId("hero-q-cond").getByText("Used", { exact: true }).click();
  await expect(page.getByTestId("hero-cond-used")).toBeChecked();
  await page.getByTestId("hero-show").click();
  await expect(hero).toHaveAttribute("data-step", "results");
  await expect(page).not.toHaveURL(/[?&]q=/);
  await expect(page).toHaveURL(/budget=30000/);
  await expect(page.getByTestId("hero-summary")).toContainText("Netherlands · used · up to €30,000");
  await expect(page.getByTestId(HAS_SCORES ? "hero-card" : "hero-no-scores").first()).toBeVisible();
  // Edit goes back to the budget question with every answer kept.
  await page.getByTestId("hero-edit").click();
  await expect(hero).toHaveAttribute("data-step", "budget");
  await page.getByTestId("hero-trail-country").click();
  await expect(hero).toHaveAttribute("data-step", "country");
});

test("hero: a second car skips the long-trips question", async ({ page }) => {
  await page.goto("/nl/en?q=role");
  await page.getByText("A second car").click();
  await expect(page.getByTestId("hero")).toHaveAttribute("data-step", "charge");
  await expect(page.getByTestId("hero-stepline")).toHaveText("Step 2 of 3 · question 2 of 3");
  await page.getByTestId("hero-back").click();
  await expect(page.getByTestId("hero")).toHaveAttribute("data-step", "role");
});

test("hero: arrow keys only move the selection; Enter answers and moves on", async ({ page }) => {
  await page.goto("/nl/en?q=charge&role=main&trips=never");
  await page.getByRole("radio", { name: /At home/ }).focus();
  await page.keyboard.press("ArrowDown");
  await expect(page.getByRole("radio", { name: /At work/ })).toBeChecked();
  await page.waitForTimeout(400);
  await expect(page.getByTestId("hero")).toHaveAttribute("data-step", "charge");
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("hero")).toHaveAttribute("data-step", "area");
  await expect(page).toHaveURL(/charge=work/);
});

test("hero: picking another country opens that country at the next question", async ({ page }) => {
  await page.goto("/nl/en?q=country&role=main");
  await page.getByText("Belgium", { exact: true }).click();
  await expect(page).toHaveURL(/\/be\/en\?.*q=role/);
  await expect(page).toHaveURL(/role=main/);
  await expect(page.getByTestId("hero")).toHaveAttribute("data-step", "role");
});

for (const q of ["country", "role", "trips", "charge", "area", "budget"]) {
  test(`hero: the ${q} question fits a 360 px phone`, async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(`/nl/en?q=${q}&role=only&trips=often&charge=home&area=city&budget=25000`);
    await expect(page.getByTestId("hero")).toHaveAttribute("data-step", q);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    // Every answer tile is a big target (AnswerTile: ≥ 56 px, 64 px in one column).
    for (const box of await page.locator(".evs-opt").evaluateAll((els) => els.map((e) => e.getBoundingClientRect().height))) expect(box).toBeGreaterThanOrEqual(56);
    // No answer is cut or split mid-word ("Netherla-nds" at 360 px in the first build).
    for (const [text, over] of await page.locator(".evs-opt b").evaluateAll((els) => els.map((e) => [e.textContent, e.scrollWidth - e.clientWidth] as const))) expect(over, String(text)).toBeLessThanOrEqual(0);
  });
}

test("hero: without release scores it says 'ranking not available yet' and ranks nothing (Decision 065)", async ({ page }) => {
  test.skip(HAS_SCORES, "the release under test has shortlist_scores.json");
  await page.goto("/nl/en?role=only&trips=monthly&charge=home&budget=15000");
  await expect(page.getByTestId("hero-no-scores")).toContainText("Ranking not available yet");
  await expect(page.getByTestId("hero-card")).toHaveCount(0);
  await page.goto("/nl/en?role=second");
  await expect(page.getByTestId("hero-no-scores")).toContainText("Ranglijst nog niet beschikbaar");
});

test("hero: changing the budget re-ranks without a reload", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly&cond=new");
  await expect(page.getByTestId("hero-card")).toHaveCount(10);
  const marker = await page.evaluate(() => {
    (window as unknown as { __noReload: boolean }).__noReload = true;
    return true;
  });
  expect(marker).toBe(true);
  const before = await page.getByTestId("hero-count").innerText();
  // T-132: the budget is its own question; Edit opens it, "Show my top 10" comes back.
  await page.getByTestId("hero-edit").click();
  await page.getByTestId("hero-budget-40000").click();
  await page.getByTestId("hero-show").click();
  await expect(page.getByTestId("hero-count")).not.toHaveText(before);
  await expect(page).toHaveURL(/budget=40000/);
  expect(await page.evaluate(() => (window as unknown as { __noReload?: boolean }).__noReload)).toBe(true);
  // New cars with a known price stay within budget.
  for (const p of await page.getByTestId("hero-price").allInnerTexts()) {
    const m = /New: €([\d,]+)/.exec(p);
    if (m) expect(Number(m[1]!.replace(/,/g, ""))).toBeLessThanOrEqual(40000);
  }
});

test("hero: removing a profile filter and adding to compare", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly");
  const chips = page.getByTestId("hero-presets").getByRole("button");
  const n = await chips.count();
  await chips.first().click();
  await expect(page.getByTestId("hero-presets").getByRole("button")).toHaveCount(n - 1);
  await expect(page).toHaveURL(/pxoff=/);
  await page.getByTestId("hero-compare").first().click();
  await expect(page.getByTestId("hero-compare").first()).toHaveAttribute("aria-pressed", "true");
});

test("hero: works at 360 px without sideways scrolling, NL in English (Decision 082)", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/nl/en?role=second&budget=20000");
  await expect(page.getByTestId("hero-card")).toHaveCount(10);
  await expect(page.getByTestId("hero-shortlist")).toContainText("Your shortlist");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});

test("hero: Nerd shows how the score is built", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly&level=nerd");
  await expect(page.getByTestId("hero-nerd").first()).toContainText("Score");
  // The scores are the release's own (Decision 065), and Nerd mode says so.
  await expect(page.getByTestId("hero-nerd-source").first()).toContainText("shortlist_scores.json");
});

test("hero: Nerd value column shows the car's own fast-charge figure in km (T-097)", async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.goto("/nl/en?role=only&trips=monthly&level=nerd");
  const card = page.getByTestId("hero-card").first();
  const cell = card.getByTestId("hero-nerd-value-dc-speed");
  await expect(cell).toContainText("km");
  const nerd = (await cell.textContent()) ?? "";
  // Same figure as the card's own "fast charging (N km in 20 min)" line, not the ×3 km/h score unit.
  const why = (await card.getByTestId("hero-why").textContent()) ?? "";
  const own = why.match(/([\d,.]+) km in 20 min/)?.[1];
  expect(own, `card why line: ${why}`).toBeTruthy();
  expect(nerd).toBe(`${own} km in 20 min`);
});

test("hero: links the launch /learn guides that exist", async ({ page }) => {
  await page.goto("/nl/en?role=main&trips=never");
  const learn = page.getByTestId("hero-learn");
  await expect(learn.getByRole("link", { name: "Winter range explained" })).toHaveAttribute("href", "/nl/en/learn/winter-range");
  await expect(learn.getByRole("link")).toHaveCount(3);
  // T-082 published the battery guide as batteries-health.
  await expect(learn.getByRole("link").nth(2)).toHaveAttribute("href", "/nl/en/learn/batteries-health");
});

test("hero: the keep-8 checkbox is named by its label only (the ⓘ sits outside it)", async ({ page }) => {
  await page.goto("/nl/en?role=main&trips=never");
  // T-132: the box moved into Refine (no scores for it yet, so it doesn't take a question slot).
  await page.getByTestId("hero-refine").locator("summary").click();
  await expect(page.getByRole("checkbox", { name: "I want to keep it 8 years or more", exact: true })).toHaveCount(1);
});

// Every served route, every card: German compounds and units are wider than Dutch (T-097 review
// found 18 px). Routes come from the countries config (Decision 082: /{country}/en for all seven
// now; the other languages join again by themselves when config serves them). The test fails if a
// route redirects.
for (const route of SERVED_ROUTES) test(`hero: ${route} Nerd score table fits a 360 px phone (verify-web found 7 px overflow)`, async ({ page }) => {
  test.skip(!HAS_SCORES, NO_SCORES_REASON);
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto(`/${route}?role=only&trips=monthly&level=nerd`);
  expect(new URL(page.url()).pathname, "route was redirected, so this language isn't really tested").toBe(`/${route}`);
  await expect(page.getByTestId("hero-nerd").first()).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(0);
  // Numbers stay whole ("1.161,6", never "1.161," / "6") and the table isn't cut off in its card.
  // A value's unit may wrap ("387 km" / "in 20 min", T-097), so this measures each number, not each cell.
  const table = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll('[data-testid="hero-nerd"] table')].map((t) => t.parentElement!);
    const cells = boxes.flatMap((box) => [...box.querySelectorAll("td")]).filter((td) => /\d/.test(td.textContent ?? ""));
    let split = 0;
    for (const td of cells) {
      const walker = document.createTreeWalker(td, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        for (const m of (n.textContent ?? "").matchAll(/\d[\d.,\u202f\u00a0]*/g)) {
          const r = document.createRange();
          r.setStart(n, m.index!);
          r.setEnd(n, m.index! + m[0].length);
          if (new Set([...r.getClientRects()].map((x) => Math.round(x.top))).size > 1) split++;
        }
      }
    }
    return { clipped: Math.max(...boxes.map((b) => b.scrollWidth - b.clientWidth)), numberCells: cells.length, split };
  });
  expect(table.numberCells).toBeGreaterThan(0);
  expect(table.split).toBe(0);
  expect(table.clipped).toBeLessThanOrEqual(0);
  // Font-independent: CI's system font rendered DE 16 px wider than a dev machine (T-097 review).
  // Text 12 % wider must still fit, with every number whole.
  await page.addStyleTag({ content: '[data-testid="hero-nerd"] table { letter-spacing: 0.12em }' });
  const wide = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll('[data-testid="hero-nerd"] table')].map((t) => t.parentElement!);
    const nums = [...document.querySelectorAll('[data-testid^="hero-nerd-value-"] span')];
    return {
      clipped: Math.max(...boxes.map((b) => b.scrollWidth - b.clientWidth)),
      split: nums.filter((s) => new Set([...s.getClientRects()].map((x) => Math.round(x.top))).size > 1).length,
      nums: nums.length,
    };
  });
  expect(wide.nums).toBeGreaterThan(0);
  expect(wide.split).toBe(0);
  expect(wide.clipped).toBeLessThanOrEqual(0);
});

// T-115 (Decision 064, A-35 B2): the budget changes the result. Needs a release with used prices and
// shortlist scores (release 2); skipped on release 1.
const ROAD = "/nl/en?role=only&trips=monthly&charge=home";
// The road-tripper's own presets (350+ km real range, 200+ km in 20 min, 380+ l boot) leave no priced
// NL car at €15k in today's data, so the €15k shortlist is checked with them removed (pxoff) and the
// preset run must then explain its empty shortlist instead of silently showing nothing.
const PRESETS_OFF = "pxoff=boot_l,dc_km_per_20min,real_range_km";
test("hero: road-tripper NL at €15k and €35k gives different top 10s; the top 5 stay within budget", async ({ page }) => {
  test.skip(!HAS_SCORES || !HAS_USED_PRICES, "needs a release with shortlist_scores.json and used_prices.json (Decisions 064/065)");
  const top = async (qs: string) => {
    await page.goto(`${ROAD}&${qs}`);
    await expect(page.getByTestId("hero-card").first()).toBeVisible();
    const all = await page.getByTestId("hero-card").evaluateAll((els) => els.map((e) => e.getAttribute("data-variant")));
    const short = await page
      .getByTestId("hero-shortlist")
      .getByTestId("hero-card")
      .evaluateAll((els) => els.map((e) => ({ price: Number(e.getAttribute("data-price")), basis: e.getAttribute("data-price-basis") })));
    // Decision 064 / A-35 B2: no unpriced card carries a place number, so none is in places 1-5.
    const cards = await page.getByTestId("hero-card").evaluateAll((els) => els.map((e) => ({ rank: e.getAttribute("data-rank"), basis: e.getAttribute("data-price-basis") })));
    for (const c of cards) expect(c.rank === null, `rank ${c.rank} with basis ${c.basis}`).toBe(c.basis === "none");
    const ranked = cards.filter((c) => c.rank !== null);
    expect(ranked.map((c) => Number(c.rank))).toEqual(ranked.map((_, i) => i + 1));
    const unpricedCards = cards.filter((c) => c.basis === "none").length;
    // Fewer than 5 priced cars: the unpriced section says plainly that no more priced cars fit.
    if (unpricedCards && ranked.length < 5) await expect(page.getByTestId("hero-no-price").getByRole("heading", { level: 3 })).toHaveText(/No more cars with a known price fit/);
    return { all, short, ranked: ranked.length, noPriced: await page.getByTestId("hero-no-priced").count() };
  };
  const low = await top("budget=15000");
  const lowOff = await top(`budget=15000&${PRESETS_OFF}`);
  const high = await top("budget=35000");
  expect(low.all).not.toEqual(high.all);
  expect(lowOff.all).not.toEqual(high.all);
  // Not an empty pass: the release has priced road-tripper cars within both budgets.
  expect(lowOff.short.length, "€15k shortlist (presets off) is empty").toBeGreaterThan(0);
  expect(high.short.length, "€35k shortlist is empty").toBeGreaterThan(0);
  // An empty shortlist always says why.
  expect(low.noPriced).toBe(low.short.length === 0 ? 1 : 0);
  for (const [r, b] of [[low, 15000], [lowOff, 15000], [high, 35000]] as const) {
    for (const c of r.short) {
      expect(c.basis).not.toBe("none");
      expect(c.price).toBeLessThanOrEqual(b);
    }
  }
  // An unpriced card at €15k may not stand for a generation (else model) whose known prices are all
  // over €15k (T-115 review: unpriced Q6 / ID.7 / Taycan versions leaked into the €15k list).
  for (const qs of ["budget=15000", `budget=15000&${PRESETS_OFF}`]) {
    await page.goto(`${ROAD}&${qs}`);
    const dataUrl = /\/data\/catalogue-\w+\.json/.exec(await page.content())![0];
    type Row = { variant_id: string; generation_id: string; model_id: string; on_sale_new?: boolean; price_new?: Record<string, { amount: number }>; used_bands?: Record<string, [number, number | null, number][]> };
    const rows = ((await (await page.request.get(dataUrl)).json()) as { rows: Row[] }).rows;
    const prices = (r: Row) => [...(r.used_bands?.NL ?? []).map((b) => b[2]), ...(r.on_sale_new && r.price_new?.NL ? [r.price_new.NL.amount] : [])];
    const unpriced = await page.locator('[data-testid="hero-card"][data-price-basis="none"]').evaluateAll((els) => els.map((e) => e.getAttribute("data-variant")));
    expect(unpriced.length, "the release has unpriced cars, so this check runs").toBeGreaterThan(0);
    for (const id of unpriced) {
      const me = rows.find((r) => r.variant_id === id)!;
      const gen = rows.filter((r) => r.generation_id === me.generation_id).flatMap(prices);
      const known = gen.length ? gen : rows.filter((r) => r.model_id === me.model_id).flatMap(prices);
      if (known.length) expect(Math.min(...known), `${id}: every sibling price is over €15k`).toBeLessThanOrEqual(15000);
    }
  }
});

// Nerd mode names how each price was made from the release row's own fields (Decision 064).
test("hero: Nerd price text comes from the used price row (curve, countries, source, date), not a fixed citation", async ({ page }) => {
  test.skip(!HAS_SCORES || !HAS_USED_PRICES, "needs a release with shortlist_scores.json and used_prices.json (Decisions 064/065)");
  await page.goto(`${ROAD}&budget=35000&level=nerd`);
  const est = page.locator('[data-testid="hero-card"][data-price-basis="estimate"]').first();
  await expect(est).toBeVisible();
  const how = est.getByTestId("hero-price-how");
  await expect(how).toContainText(/depreciation curve/);
  await expect(how).toContainText(/\(\d{4}-\d{2}-\d{2}\)/);
  await expect(how).not.toContainText("R-40");
  const band = page.locator('[data-testid="hero-card"][data-price-basis="band"]').first();
  await expect(band.getByTestId("hero-price-how")).toContainText(/counted listings/);
});

// Depth + parallax (UX, Menno 2026-11-17): layers drift with scroll; reduced motion keeps the flat scene.
test("landing: highway band layers slide sideways as you scroll", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/nl/nl");
  const band = page.getByTestId("band-highway");
  await band.scrollIntoViewIfNeeded();
  await expect(band).toHaveAttribute("data-live", "1");
  const fg = band.locator(".evs-scene--day [data-depth]").last();
  await expect(fg).toHaveAttribute("style", /translate3d/);
  const before = await fg.evaluate((e) => e.style.transform);
  await page.mouse.wheel(0, 300);
  await expect.poll(() => fg.evaluate((e) => e.style.transform)).not.toBe(before);
  expect(await band.locator(".evs-scene--day [data-depth]").count()).toBe(9);
});

test("landing: reduced motion shows the flat scenes and no moving layers", async ({ browser }) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.goto("/nl/nl");
  await expect(page.getByTestId("hero-scene")).toHaveAttribute("data-live", "0");
  await expect(page.locator("[data-depth]")).toHaveCount(0);
  await expect(page.getByTestId("hero-scene").locator(".evs-scene--day img")).toBeVisible();
  await ctx.close();
});
