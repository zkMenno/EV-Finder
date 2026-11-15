// Request-time routing and security headers (runs before every page).
// 1. Language URLs (Decision 015): redirects only, see src/lib/lang.ts. The page language comes
//    from the URL, so layouts never read request headers and pages can be static.
// 2. Content-Security-Policy without 'unsafe-inline' for scripts, see src/lib/csp.ts: hashes for
//    static pages (manifest from scripts/csp-hashes.mjs), a per-request nonce for the rest.
// 3. Staff pages: HTTP Basic guard when STAFF_PAGES=1 (src/lib/staff-auth.ts).
import { readFileSync } from "node:fs";
import path from "node:path";
import { NextResponse, type NextRequest } from "next/server";
import { buildCsp, cspFor, makeNonce, type CspHashManifest } from "@/lib/csp";
import { LANG_COOKIE, routeLang } from "@/lib/lang";
import { checkStaff } from "@/lib/staff-auth";

const DEV = process.env.NODE_ENV === "development";

let manifest: CspHashManifest | null | undefined;
/** Read once per process; null (logged) when the build step didn't run. */
function hashManifest(): CspHashManifest | null {
  if (manifest !== undefined) return manifest;
  try {
    manifest = JSON.parse(readFileSync(path.join(process.cwd(), ".next/server/csp-hashes.json"), "utf8")) as CspHashManifest;
  } catch {
    if (!DEV) console.error("csp: .next/server/csp-hashes.json missing (run `pnpm build`); falling back to a policy with 'unsafe-inline'");
    manifest = null;
  }
  return manifest;
}

function withCsp(req: NextRequest, extra?: (res: NextResponse) => void): NextResponse {
  const m = hashManifest();
  // Without the manifest static pages carry no nonce or hash, so a nonce policy would break them:
  // keep the old (weaker) policy and say so in the log, rather than a broken site.
  const { csp } = m || DEV ? cspFor(req.nextUrl.pathname, m, { nonce: makeNonce(), dev: DEV }) : { csp: buildCsp({}).replace("script-src 'self'", "script-src 'self' 'unsafe-inline'") };
  const headers = new Headers(req.headers);
  // Next.js reads the nonce from the request's CSP header while rendering dynamic pages.
  headers.set("Content-Security-Policy", csp);
  const res = NextResponse.next({ request: { headers } });
  res.headers.set("Content-Security-Policy", csp);
  extra?.(res);
  return res;
}

export function proxy(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  const route = routeLang(pathname, search, req.cookies.get(LANG_COOKIE)?.value);
  if (route) {
    const url = req.nextUrl.clone();
    const target = new URL(route.redirect, url);
    url.pathname = target.pathname;
    url.search = target.search;
    const res = NextResponse.redirect(url, route.status);
    if (route.status === 307) res.headers.set("Vary", "Cookie");
    return res;
  }
  if (pathname === "/staff" || pathname.startsWith("/staff/")) {
    const s = checkStaff(req.headers.get("authorization"));
    if (s === "challenge") {
      return new NextResponse("Authentication required", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="staff", charset="UTF-8"', "X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store" },
      });
    }
    // "off": the page itself 404s (STAFF_PAGES unset).
    return withCsp(req, (res) => res.headers.set("Cache-Control", "no-store"));
  }
  return withCsp(req);
}

export const config = {
  matcher: [
    {
      source: "/((?!_next/static|_next/image|favicon.ico).*)",
      // Prefetches return RSC payloads, not HTML: no CSP needed, keep them cheap.
      missing: [
        { type: "header", key: "next-router-prefetch" },
        { type: "header", key: "purpose", value: "prefetch" },
      ],
    },
  ],
};
