// /theme-init.js: applies the remembered theme before first paint (no flash of the wrong theme).
// A same-origin file, not an inline script, so the CSP (script-src 'self', no 'unsafe-inline')
// allows it on static and dynamic pages alike. Loaded by the root layout's <head>.
// Default = the system setting (prefers-color-scheme, in tokens.generated.css); the toggle stores
// "light" or "dark" under THEME_KEY. Plain try/catch: storage may throw (same rule as storage.ts).
import { THEME_INIT_JS } from "@/lib/theme";

export const dynamic = "force-static";

export function GET(): Response {
  return new Response(THEME_INIT_JS, {
    headers: { "Content-Type": "text/javascript; charset=utf-8", "Cache-Control": "public, max-age=3600" },
  });
}
