// Canonical origin for absolute URLs (canonical, hreflang, sitemap, robots): APP_URL (A-05 F3).
// Static pages bake it in at build time, so a production build without it would ship
// http://localhost:3000 canonicals. Rules:
//   - APP_URL set: must be an http(s) origin (no path, query or hash). In a production build that
//     is not a test build it must also be https and not a local host.
//   - APP_URL unset: allowed in dev, unit tests and test builds (CI=true or APP_URL_TEST_BUILD=1:
//     CI's build + e2e jobs, which never ship), where it falls back to http://localhost:3000.
//     A production build otherwise fails loudly.
// The Docker image gets it as a build arg (apps/web/Dockerfile, .github/workflows/images.yml);
// the placeholder is https://ev.example.com until the real domain exists (infra/README.md).
// Pure (no Node APIs, no imports): src/lib/site-paths.ts imports it, and it may end up in the
// client bundle. `pnpm build` runs scripts/check-app-url.mjs first.
/* global URL */

export const DEV_APP_URL = "http://localhost:3000";

const LOCAL = /^(localhost|127(\.\d+){3}|0\.0\.0\.0|\[::1?\])$/i;

/** CI's own build/e2e jobs, or an explicit opt-in: builds that are tested, never deployed. */
export function isTestBuild(env) {
  return env.CI === "true" || env.CI === "1" || env.APP_URL_TEST_BUILD === "1";
}

/** The origin to use (no trailing slash); throws when production would get a wrong one. */
export function resolveAppUrl(env) {
  const strict = env.NODE_ENV === "production" && !isTestBuild(env);
  const raw = (env.APP_URL ?? "").trim();
  if (!raw) {
    if (strict)
      throw new Error(
        "APP_URL is not set. A production build bakes it into canonical, hreflang and sitemap URLs; set APP_URL (e.g. https://ev.example.com) or, for a throw-away test build, APP_URL_TEST_BUILD=1.",
      );
    return DEV_APP_URL;
  }
  let u;
  try {
    u = new URL(raw);
  } catch {
    throw new Error(`APP_URL is not a valid URL: ${JSON.stringify(raw)}`);
  }
  if (u.protocol !== "https:" && u.protocol !== "http:") throw new Error(`APP_URL must be http(s): ${raw}`);
  if ((u.pathname !== "/" && u.pathname !== "") || u.search || u.hash || u.username || u.password)
    throw new Error(`APP_URL must be an origin only (no path, query, hash or user info): ${raw}`);
  if (strict && (u.protocol !== "https:" || LOCAL.test(u.hostname)))
    throw new Error(`APP_URL must be a public https origin in a production build, got ${raw}`);
  return u.origin;
}
