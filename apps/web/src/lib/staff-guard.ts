// Server-side staff gate for the staff layout and every staff page (A-05 F2). The proxy
// (src/proxy.ts) sends the HTTP Basic challenge, but the pages must not depend on it: a proxy
// that is skipped (matcher change, prefetch header, misconfiguration) must never expose the
// review queue. So each staff layout and page checks the credentials again, here, with the same
// constant-time compare (src/lib/staff-auth.ts), and fails closed with a 404.
//
// Why both the layout and the page: on client-side navigation Next.js can re-render only the page
// segment and reuse the layout, so a layout-only check is not enough.
import { headers } from "next/headers";
import { notFound } from "next/navigation";
import { checkStaff } from "./staff-auth";

/** "ok" only with STAFF_PAGES=1 and matching credentials; anything else is "deny" (404). */
export function staffGate(authorization: string | null, env: Record<string, string | undefined> = process.env): "ok" | "deny" {
  return checkStaff(authorization, env) === "ok" ? "ok" : "deny";
}

/** Call at the top of every staff layout and page. Renders the 404 unless the request is authorised. */
export async function requireStaff(): Promise<void> {
  const h = await headers();
  if (staffGate(h.get("authorization")) !== "ok") notFound();
}
