// T-132: one question per screen; the step lives in the URL (`q`).
import { describe, expect, it } from "vitest";
import { defaultHeroState, drivingQuestion, heroFromSearchParams, heroOwnParams, heroStep, nextStep, prevStep, roadStop, type HeroState } from "./hero-state";
import { EMPTY_ANSWERS, type Answers } from "./shortlist";

const st = (answers: Partial<Answers>, extra: Partial<HeroState> = {}): HeroState => ({
  ...defaultHeroState(),
  answers: { ...EMPTY_ANSWERS, ...answers },
  ...extra,
});

describe("hero steps (T-132)", () => {
  it("a fresh visit starts at the country question", () => {
    expect(heroStep(defaultHeroState())).toBe("country");
  });

  it("old shared links with a full profile open the results", () => {
    expect(heroStep(heroFromSearchParams(new URLSearchParams("role=only&trips=monthly&charge=home")))).toBe("results");
    expect(heroStep(heroFromSearchParams(new URLSearchParams("role=second")))).toBe("results");
  });

  it("without q, a half-answered link opens the first open driving question", () => {
    expect(heroStep(st({ role: "main" }))).toBe("trips");
    expect(heroStep(st({ charge: "home" }))).toBe("role");
    expect(heroStep(st({}, { budget: 20000 }))).toBe("role");
  });

  it("an explicit step wins; results needs a full profile; trips is skipped for a second car", () => {
    expect(heroStep(st({ role: "only", trips: "never" }, { step: "area" }))).toBe("area");
    expect(heroStep(st({ role: "only" }, { step: "results" }))).toBe("trips");
    expect(heroStep(st({ role: "second" }, { step: "trips" }))).toBe("charge");
  });

  it("walks country → role → trips → charge → area → budget → results, and back", () => {
    const a = { ...EMPTY_ANSWERS, role: "main" as const };
    const order = ["country", "role", "trips", "charge", "area", "budget", "results"] as const;
    for (let i = 0; i < order.length - 1; i++) {
      expect(nextStep(order[i]!, a)).toBe(order[i + 1]);
      expect(prevStep(order[i + 1]!, a)).toBe(order[i]);
    }
    expect(prevStep("country", a)).toBe("country");
    expect(nextStep("results", a)).toBe("results");
  });

  it("a second car goes role → charge and back", () => {
    const a = { ...EMPTY_ANSWERS, role: "second" as const };
    expect(nextStep("role", a)).toBe("charge");
    expect(prevStep("charge", a)).toBe("role");
    expect(drivingQuestion("charge", a)).toEqual({ n: 2, of: 3 });
  });

  it("question count and road stop", () => {
    const a = { ...EMPTY_ANSWERS, role: "main" as const };
    expect(drivingQuestion("trips", a)).toEqual({ n: 2, of: 4 });
    expect(drivingQuestion("budget", a)).toBeNull();
    expect(["country", "role", "area", "budget", "results"].map((x) => roadStop(x as never))).toEqual([0, 1, 1, 2, 3]);
  });

  it("q is written for every step but results, and read back", () => {
    expect(heroOwnParams(st({ role: "main" }, { step: "trips" })).get("q")).toBe("trips");
    expect(heroOwnParams(st({ role: "main", trips: "never" }, { step: "results" })).has("q")).toBe(false);
    expect(heroFromSearchParams(new URLSearchParams("q=budget")).step).toBe("budget");
    expect(heroFromSearchParams(new URLSearchParams("q=nonsense")).step).toBeNull();
  });
});
