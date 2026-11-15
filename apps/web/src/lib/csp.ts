// Content-Security-Policy (A-01 / A-02, ADDENDUM-5 item 6). No 'unsafe-inline' for scripts.
// - Dynamic pages (Explore, compare, staff): a fresh nonce per request; Next.js reads it from the
//   request's CSP header and puts it on its own scripts.
// - Static pages (model / generation / variant / learn / rankings / about, Decision 015): no
//   request at render time, so no nonce. scripts/csp-hashes.mjs hashes each prerendered page's
//   inline scripts after `next build`; the proxy sends those sha256 hashes for that path.
// Both: the browser may talk only to our own origin (no fonts, CDNs, analytics; e2e checks it).
// Styles keep 'unsafe-inline' (style attributes); the rule targets scripts.

/** Inline-script hashes per static path (written by scripts/csp-hashes.mjs into .next/server). */
export interface CspHashManifest {
  /** Hashes of the static 404 page, allowed everywhere (any request can end in a 404). */
  notFound: string[];
  pages: Record<string, string[]>;
}

export function buildCsp({ nonce, hashes = [], dev = false }: { nonce?: string; hashes?: readonly string[]; dev?: boolean }): string {
  const script = ["'self'", ...(nonce ? [`'nonce-${nonce}'`] : []), ...hashes.map((h) => `'${h}'`), ...(dev ? ["'unsafe-eval'"] : [])];
  return [
    "default-src 'self'",
    `script-src ${script.join(" ")}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join("; ");
}

/** 16 random bytes, base64: unguessable, fresh per request. */
export function makeNonce(): string {
  const b = new Uint8Array(16);
  crypto.getRandomValues(b);
  return btoa(String.fromCharCode(...b));
}

/** Path as the manifest stores it: no trailing slash, decoded. */
export function manifestKey(pathname: string): string {
  let p = pathname;
  try {
    p = decodeURIComponent(pathname);
  } catch {
    // keep as is
  }
  return p.length > 1 ? p.replace(/\/+$/, "") : p;
}

/** The policy for one request: static path → its hashes; anything else → nonce (+ 404 hashes). */
export function cspFor(
  pathname: string,
  manifest: CspHashManifest | null,
  opts: { nonce: string; dev?: boolean },
): { csp: string; nonce: string | null } {
  const page = manifest?.pages[manifestKey(pathname)];
  if (page) return { csp: buildCsp({ hashes: page, dev: opts.dev }), nonce: null };
  return { csp: buildCsp({ nonce: opts.nonce, hashes: manifest?.notFound ?? [], dev: opts.dev }), nonce: opts.nonce };
}
