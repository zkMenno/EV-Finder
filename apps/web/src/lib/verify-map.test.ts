import { existsSync, readdirSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { checkMap, expandSelector, globToRegExp, loadMap, MAP_FILE, plainError, rawKeysIn, selectFeatures } from "../../scripts/verify.mjs";

// T-126: the feature map is the rubric for `pnpm verify` and for reviewers, so it must stay valid
// and its triggers must point at files that exist (a stale trigger silently skips a feature).
const WEB = path.dirname(path.dirname(MAP_FILE));
const map = loadMap();

function walk(dir: string, out: string[] = []): string[] {
  for (const e of readdirSync(path.join(WEB, dir), { withFileTypes: true })) {
    const rel = dir ? `${dir}/${e.name}` : e.name;
    if (e.isDirectory()) walk(rel, out);
    else out.push(rel);
  }
  return out;
}

describe("feature map", () => {
  it("is valid", () => {
    expect(checkMap(map)).toEqual([]);
  });

  it("has a trigger per feature that matches at least one real file", () => {
    const files = [...walk("src"), ...walk("scripts")];
    const dead = map.features.flatMap((f) =>
      f.triggers.filter((t) => !files.some((p) => globToRegExp(t).test(p))).map((t) => `${f.id}: ${t}`),
    );
    expect(dead).toEqual([]);
    const deadShared = (map.defaults?.always_all ?? []).filter((t) => !files.some((p) => globToRegExp(t).test(p)) && !existsSync(path.join(WEB, t)));
    expect(deadShared).toEqual([]);
  });

  it("walks every flow when a shared file changes (Num shows every number on the site)", () => {
    for (const f of ["src/components/Num.tsx", "src/lib/catalogue.ts", "package.json", "src/app/[country]/[lang]/layout.tsx"])
      expect(selectFeatures(map, [f]).features, f).toHaveLength(map.features.length);
  });

  it("covers the launch flows the e2e suite covers", () => {
    const ids = map.features.map((f) => f.id);
    for (const id of ["hero-road-tripper", "explore-filter-url", "explore-compare", "car-pages", "language-switch"]) expect(ids).toContain(id);
    expect(existsSync(MAP_FILE)).toBe(true);
  });

  it("rejects a broken map in plain words", () => {
    const problems = checkMap({ features: [{ id: "Bad Id", steps: [{ click: "x" }], expect: [{ count: "@x" }] }] });
    expect(problems.join("\n")).toMatch(/kebab-case/);
    expect(problems.join("\n")).toMatch(/start with goto/);
    expect(problems.join("\n")).toMatch(/what \+ why/);
    expect(problems.join("\n")).toMatch(/count needs eq, min or max/);
  });
});

describe("globToRegExp", () => {
  it("handles **, * and escaped brackets", () => {
    expect(globToRegExp("src/app/[[]country]/[[]lang]/ev/**").test("src/app/[country]/[lang]/ev/[make]/page.tsx")).toBe(true);
    expect(globToRegExp("src/i18n/*.json").test("src/i18n/nl.json")).toBe(true);
    expect(globToRegExp("src/i18n/*.json").test("src/i18n/sub/nl.json")).toBe(false);
    expect(globToRegExp("src/lib/finance*.ts").test("src/lib/finance.test.ts")).toBe(true);
    expect(globToRegExp("src/**/x.ts").test("src/x.ts")).toBe(true);
  });
});

describe("selectFeatures", () => {
  it("picks only features whose triggers match the diff", () => {
    const { features } = selectFeatures(map, ["src/components/ThemeToggle.tsx"]);
    expect(features.map((f) => f.id)).toEqual(["theme-toggle"]);
    expect(selectFeatures(map, ["README.md"]).features).toEqual([]);
  });
  it("walks everything when an always_all file changes", () => {
    const m = { ...map, defaults: { always_all: ["package.json"] } };
    expect(selectFeatures(m, ["package.json"]).features).toHaveLength(map.features.length);
  });
});

describe("expandSelector", () => {
  it("expands @name outside XPath only", () => {
    expect(expandSelector("@hero-card")).toBe('[data-testid="hero-card"]');
    expect(expandSelector("@hero-shortlist @hero-card")).toBe('[data-testid="hero-shortlist"] [data-testid="hero-card"]');
    expect(expandSelector("label:has(@hero-role-second)")).toBe('label:has([data-testid="hero-role-second"])');
    expect(expandSelector("(//*[@data-testid='x'])[1]")).toBe("(//*[@data-testid='x'])[1]");
  });
});

describe("rawKeysIn", () => {
  it("finds dictionary keys shown as text, not ordinary dotted words", () => {
    const keys = new Set(["hero.card.price", "explore.title"]);
    expect(rawKeysIn("Price hero.card.price · see e.g. ev.example.com", keys)).toEqual(["hero.card.price"]);
  });
});

describe("plainError", () => {
  it("turns Playwright timeouts into plain words", () => {
    expect(plainError("locator.click: Timeout 10000ms exceeded.", { click: "@theme-toggle" })).toBe("waited 10 s for “@theme-toggle”: it never appeared or couldn't be used");
    expect(plainError("page.goto: net::ERR_CONNECTION_REFUSED at x", { goto: "/nl/en" })).toBe("the app didn't answer");
  });
});
