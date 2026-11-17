import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.E2E_PORT ?? 3100);
/** Test-only staff credentials (not a secret; the e2e server is local). */
export const E2E_STAFF_AUTH = "e2e:e2e-only-not-a-secret";
// Runs on the published release (data/releases/latest), the same data `pnpm build` bakes into the
// static model / generation / variant / learn pages (Decision 015). E2E_CATALOGUE_DIR overrides.

// Runs against a production build: `pnpm build` first (CI does), then `pnpm e2e`.
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `pnpm exec next start -p ${PORT}`,
    url: `http://localhost:${PORT}/health`,
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
    // Same catalogue at build and run time: static pages and Explore must agree.
    // TRIP_FIT=1 so e2e/trip.spec.ts can test the trip check (E2E_TRIP_FIT=0 to run with it off);
    // charging link-outs come from a fixture until T-024 fills config/countries (T-026).
    // Staff pages on with throw-away test credentials, so e2e/security.spec.ts can prove the guard
    // holds against prefetch headers (A-05 F2). APP_URL: the same placeholder origin as the image
    // build (build with APP_URL=https://ev.example.com, or in CI, where the build is a test build).
    env: {
      APP_URL: process.env.APP_URL ?? "https://ev.example.com",
      STAFF_PAGES: "1",
      STAFF_BASIC_AUTH: E2E_STAFF_AUTH,
      CATALOGUE_DIR: process.env.E2E_CATALOGUE_DIR ?? "../../data/releases",
      TRIP_FIT: process.env.E2E_TRIP_FIT ?? "1",
      // Parked features (Decision 051): E2E_PARKED=1 runs against a build made with PARKED=1.
      PARKED: process.env.E2E_PARKED === "1" ? "1" : "0",
      CHARGING_LINKS_FILE: process.env.E2E_CHARGING_LINKS_FILE ?? "e2e/fixtures/charging-links.json",
    },
  },
});
