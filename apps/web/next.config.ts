import type { NextConfig } from "next";

const config: NextConfig = {
  // @ev/schema ships TypeScript source (type-only imports today).
  transpilePackages: ["@ev/schema"],
  poweredByHeader: false,
  output: "standalone",
  async redirects() {
    return [{ source: "/", destination: "/nl", permanent: false }];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // The browser may only talk to our own origin (no fonts, CDNs or analytics).
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data:",
              "font-src 'self'",
              "connect-src 'self'",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join("; "),
          },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Content-Type-Options", value: "nosniff" },
        ],
      },
    ];
  },
};

export default config;
