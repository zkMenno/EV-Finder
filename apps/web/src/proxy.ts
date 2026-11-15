// Resolves the UI language once per request: ?lang= → cookie `lang` → country default.
// Passes it on as a request header (layouts can't read searchParams) and stores ?lang= in the cookie.
import { NextResponse, type NextRequest } from "next/server";
import { resolveLang } from "@/lib/lang";

const LANG_HEADER = "x-ev-lang";

export function proxy(req: NextRequest) {
  const query = req.nextUrl.searchParams.get("lang");
  const cookie = req.cookies.get("lang")?.value;
  const lang = resolveLang(req.nextUrl.pathname, query, cookie);
  const headers = new Headers(req.headers);
  headers.set(LANG_HEADER, lang);
  const res = NextResponse.next({ request: { headers } });
  if (query === lang && cookie !== lang) {
    res.cookies.set("lang", lang, { path: "/", maxAge: 60 * 60 * 24 * 365, sameSite: "lax" });
  }
  return res;
}

export const config = {
  matcher: ["/((?!_next/|data/|favicon.ico).*)"],
};
