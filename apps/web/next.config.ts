import type { NextConfig } from "next";

const config: NextConfig = {
  // @ev/schema ships TypeScript source (type-only imports today).
  transpilePackages: ["@ev/schema"],
  poweredByHeader: false,
  output: "standalone",
  // Several root layouts (/{country}/{lang} and /staff): 404s outside them use app/global-not-found.tsx.
  experimental: { globalNotFound: true },
  // `/`, `/{country}` and old `/{country}/…` URLs redirect in src/proxy.ts (Decision 015).
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Content-Security-Policy is set per request in src/proxy.ts (nonce or hashes, src/lib/csp.ts).
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
        ],
      },
      // Staff pages (404 unless STAFF_PAGES=1) are never indexed.
      { source: "/staff/:path*", headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }] },
    ];
  },
};

export default config;
