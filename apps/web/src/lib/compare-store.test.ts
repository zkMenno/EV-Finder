import { describe, expect, it } from "vitest";
import { addItem, COMPARE_KEY, COMPARE_MAX, compareHref, createCompareStore, parseCompare } from "./compare-store";
import { createFavouriteStore } from "./favourites";
import { memoryStorage, type KeyValueStorage } from "./storage";

const item = (id: string) => ({ id, label: id.toUpperCase() });

describe("compare store", () => {
  it("holds at most 4", () => {
    const mem = memoryStorage();
    const s = createCompareStore(() => mem);
    expect(["a", "b", "c", "d"].map((id) => s.add(item(id)))).toEqual(["added", "added", "added", "added"]);
    expect(s.add(item("e"))).toBe("full");
    expect(s.get()).toHaveLength(COMPARE_MAX);
    expect(s.add(item("a"))).toBe("exists");
  });

  it("persists and survives a 'reload' (new store, same storage)", () => {
    const mem = memoryStorage();
    const s1 = createCompareStore(() => mem);
    s1.add(item("a"));
    s1.add(item("b"));
    const s2 = createCompareStore(() => mem);
    expect(s2.get().map((i) => i.id)).toEqual(["a", "b"]);
    expect(JSON.parse(mem.data.get(COMPARE_KEY)!)).toHaveLength(2);
  });

  it("remove and clear notify subscribers", () => {
    const mem = memoryStorage();
    const s = createCompareStore(() => mem);
    let calls = 0;
    const off = s.subscribe(() => calls++);
    s.add(item("a"));
    s.add(item("b"));
    s.remove("a");
    expect(s.get().map((i) => i.id)).toEqual(["b"]);
    s.clear();
    expect(s.get()).toEqual([]);
    expect(calls).toBe(4);
    off();
  });

  it("survives broken or throwing storage", () => {
    const mem = memoryStorage();
    mem.setItem(COMPARE_KEY, "{garbage");
    expect(createCompareStore(() => mem).get()).toEqual([]);
    const throwing: KeyValueStorage = {
      getItem: () => {
        throw new Error("denied");
      },
      setItem: () => {
        throw new Error("quota");
      },
    };
    const s = createCompareStore(() => throwing);
    expect(s.add(item("a"))).toBe("added");
    expect(s.get()).toHaveLength(1);
    expect(createCompareStore(() => null).get()).toEqual([]);
  });

  it("parse drops duplicates, junk and anything past 4", () => {
    expect(parseCompare([item("a"), item("a"), { id: 3 }, null, item("b"), item("c"), item("d"), item("e")]).map((i) => i.id)).toEqual(["a", "b", "c", "d"]);
    expect(parseCompare({})).toEqual([]);
    expect(parseCompare([{ id: "x" }])).toEqual([{ id: "x", label: "x" }]);
  });

  it("pure add never mutates", () => {
    const before = [item("a")];
    addItem(before, item("b"));
    expect(before).toHaveLength(1);
  });

  it("builds the compare link", () => {
    expect(compareHref("/nl/nl", [item("a"), item("b")])).toBe("/nl/nl/compare?ids=a,b");
  });
});

describe("favourites", () => {
  it("toggles and persists", () => {
    const mem = memoryStorage();
    const s = createFavouriteStore(() => mem);
    expect(s.toggle("x")).toBe(true);
    expect(createFavouriteStore(() => mem).get()).toEqual(["x"]);
    expect(s.toggle("x")).toBe(false);
    expect(s.get()).toEqual([]);
  });
});
