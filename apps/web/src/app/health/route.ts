// Liveness/readiness probe for the AppInfra watchdog, Docker HEALTHCHECK and Caddy (T-013, Decision 006).
// Returns only status, the published catalogue release number (null while the dev fixture is in use)
// and the server time. Never env values, paths or error details.
import { getCatalogue } from "@/lib/catalogue";

export const dynamic = "force-dynamic";

export interface HealthBody {
  status: "ok";
  release: number | null;
  time: string;
}

export function GET(): Response {
  const cat = getCatalogue();
  const body: HealthBody = {
    status: "ok",
    release: cat.origin() === "release" ? cat.release() : null,
    time: new Date().toISOString(),
  };
  return Response.json(body, {
    status: 200,
    headers: { "cache-control": "no-store, max-age=0" },
  });
}
