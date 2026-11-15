// Basic guard for staff pages until real auth exists (Q-035, A-01 "before staging").
// STAFF_PAGES=1 turns the pages on; STAFF_BASIC_AUTH="user:pass" (env only, never in the repo)
// is then required as HTTP Basic credentials. Fails closed: on without credentials = no access.
import { createHash, timingSafeEqual } from "node:crypto";

export type StaffCheck = "off" | "ok" | "challenge";

function digest(s: string): Buffer {
  return createHash("sha256").update(s, "utf8").digest();
}

/** Constant-time string compare (hash first so lengths always match). */
export function safeEqual(a: string, b: string): boolean {
  return timingSafeEqual(digest(a), digest(b));
}

/** "off": pages disabled (404). "challenge": send 401. "ok": let the request through. */
export function checkStaff(authorization: string | null, env: Record<string, string | undefined> = process.env): StaffCheck {
  if (env.STAFF_PAGES !== "1") return "off";
  const expected = env.STAFF_BASIC_AUTH;
  if (!expected || !expected.includes(":")) return "challenge";
  const m = /^Basic\s+([A-Za-z0-9+/=]+)$/i.exec(authorization ?? "");
  if (!m) return "challenge";
  let given: string;
  try {
    given = Buffer.from(m[1]!, "base64").toString("utf8");
  } catch {
    return "challenge";
  }
  return safeEqual(given, expected) ? "ok" : "challenge";
}
