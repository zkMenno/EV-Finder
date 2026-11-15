// Liveness/readiness probe for the AppInfra watchdog, Docker HEALTHCHECK and Caddy (T-013, Decision 006).
// Returns only status, the published catalogue release number (null while the dev fixture is in use)
// and the server time. Never env values, paths or error details.
// 503 "unhealthy" in production when the CSP hash manifest is missing (A-05 F10): a build step
// was skipped, so the deploy must fail its health check instead of running with a weaker policy.
import { getCatalogue } from "@/lib/catalogue";
import { cspManifest, cspReady } from "@/lib/csp-manifest";

export const dynamic = "force-dynamic";

export interface HealthBody {
  status: "ok" | "unhealthy";
  release: number | null;
  time: string;
}

export function GET(): Response {
  const cat = getCatalogue();
  const ok = cspReady(cspManifest());
  const body: HealthBody = {
    status: ok ? "ok" : "unhealthy",
    release: cat.origin() === "release" ? cat.release() : null,
    time: new Date().toISOString(),
  };
  return Response.json(body, {
    status: ok ? 200 : 503,
    headers: { "cache-control": "no-store, max-age=0" },
  });
}
