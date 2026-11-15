// A-05 F2: staff pages check the credentials themselves, independent of the proxy.
import { afterEach, describe, expect, it, vi } from "vitest";

const h = vi.hoisted(() => ({ auth: null as string | null }));
vi.mock("next/headers", () => ({ headers: async () => new Headers(h.auth ? { authorization: h.auth } : {}) }));
vi.mock("next/navigation", () => ({
  notFound: () => {
    throw new Error("NEXT_NOT_FOUND");
  },
}));

const { requireStaff, staffGate } = await import("./staff-guard");

const basic = (s: string) => `Basic ${Buffer.from(s).toString("base64")}`;
const ON = { STAFF_PAGES: "1", STAFF_BASIC_AUTH: "u:secretpw" };

afterEach(() => {
  vi.unstubAllEnvs();
  h.auth = null;
});

describe("staffGate", () => {
  it("ok only when the pages are on and the credentials match", () => {
    expect(staffGate(basic("u:secretpw"), ON)).toBe("ok");
    expect(staffGate(basic("u:wrong"), ON)).toBe("deny");
    expect(staffGate(basic("u:secretpw "), ON)).toBe("deny");
    expect(staffGate(null, ON)).toBe("deny");
    expect(staffGate("Bearer x", ON)).toBe("deny");
  });

  it("fails closed: pages off, credentials missing or malformed → deny", () => {
    expect(staffGate(basic("u:secretpw"), { STAFF_BASIC_AUTH: "u:secretpw" })).toBe("deny");
    expect(staffGate(basic("u:secretpw"), { STAFF_PAGES: "1" })).toBe("deny");
    expect(staffGate(basic("nocolon"), { STAFF_PAGES: "1", STAFF_BASIC_AUTH: "nocolon" })).toBe("deny");
    expect(staffGate(basic(":"), { STAFF_PAGES: "1", STAFF_BASIC_AUTH: "" })).toBe("deny");
  });
});

describe("requireStaff (layout + page)", () => {
  it("404s without credentials even when the proxy did not run", async () => {
    vi.stubEnv("STAFF_PAGES", "1");
    vi.stubEnv("STAFF_BASIC_AUTH", "u:secretpw");
    await expect(requireStaff()).rejects.toThrow("NEXT_NOT_FOUND");
    h.auth = basic("u:nope");
    await expect(requireStaff()).rejects.toThrow("NEXT_NOT_FOUND");
  });

  it("renders with the right credentials", async () => {
    vi.stubEnv("STAFF_PAGES", "1");
    vi.stubEnv("STAFF_BASIC_AUTH", "u:secretpw");
    h.auth = basic("u:secretpw");
    await expect(requireStaff()).resolves.toBeUndefined();
  });

  it("404s when staff pages are off", async () => {
    h.auth = basic("u:secretpw");
    await expect(requireStaff()).rejects.toThrow("NEXT_NOT_FOUND");
  });
});
