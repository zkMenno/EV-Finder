// Request-time routing and security headers (runs before every page).
// 1. Language URLs (Decision 015): redirects only, see src/lib/lang.ts. The page language comes
//    from the URL, so layouts never read request headers and pages can be static.
// 2. Content-Security-Policy without 'unsafe-inline' for scripts, see src/lib/csp.ts: hashes for
//    static pages (manifest from scripts/csp-hashes.mjs), a per-request nonce for the rest.
// 3. Staff pages: HTTP Basic challenge when STAFF_PAGES=1 (src/lib/staff-auth.ts). Not the only
//    lock: the staff layout and pages check the credentials again (src/lib/staff-guard.ts, A-05 F2).
import { NextResponse, type NextRequest } from "next/server";
import { cspFor, makeNonce } from "@/lib/csp";
import { cspManifest } from "@/lib/csp-manifest";
import { LANG_COOKIE, routeLang } from "@/lib/lang";
import { checkStaff } from "@/lib/staff-auth";

const DEV = process.env.NODE_ENV === "development";

function withCsp(req: NextRequest, extra?: (res: NextResponse) => void): NextResponse {
  // Fail closed (A-05 F10): without the hash manifest cspFor() gives the strict nonce-only policy
  // (no 'unsafe-inline', ever); /health then answers 503 (src/lib/csp-manifest.ts).
  const { csp } = cspFor(req.nextUrl.pathname, cspManifest(), { nonce: makeNonce(), dev: DEV });
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

// Runs on every page request, prefetches included (A-05 F2). No `missing:` header conditions: a
// client-supplied header such as `Purpose: prefetch` or `Next-Router-Prefetch` must never skip the
// CSP, the language redirects or the staff challenge. The cost is one cached manifest lookup and
// a nonce per prefetch.
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
