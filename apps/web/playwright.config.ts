import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.E2E_PORT ?? 3100);
// Set E2E_CATALOGUE_DIR=../../data/releases to smoke-test against the real published release.

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
    url: `http://localhost:${PORT}/nl`,
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
    // Deterministic data: a releases dir with no release → the app serves the dev fixture.
    env: { CATALOGUE_DIR: process.env.E2E_CATALOGUE_DIR ?? "e2e/no-release" },
  },
});
