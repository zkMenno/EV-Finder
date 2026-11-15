// Pre-build check (A-05 F3): fail `pnpm build` loudly when a production build would bake a
// missing or local APP_URL into canonical, hreflang and sitemap URLs (rules: scripts/app-url.mjs).
//
//   node scripts/check-app-url.mjs
/* global console, process */
import { isTestBuild, resolveAppUrl } from "./app-url.mjs";

try {
  const url = resolveAppUrl({ ...process.env, NODE_ENV: "production" });
  console.log(`app-url: canonical origin ${url}${isTestBuild(process.env) ? " (test build)" : ""}`);
} catch (e) {
  console.error(`app-url: ${e instanceof Error ? e.message : String(e)}`);
  process.exit(1);
}
