// Compact client catalogue for Explore: /data/catalogue-<release>.json (immutable, cacheable forever)
// or /data/catalogue-dev.json while the dev fixture is in use (no-cache).
import { clientCatalogueKey, getCatalogue, type Catalogue } from "@/lib/catalogue";
import { toClientCatalogue } from "@/lib/explore-data";

export const dynamic = "force-dynamic";

const bodies = new WeakMap<Catalogue, string>();

export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const m = /^catalogue-(\d+|dev)\.json$/.exec(file);
  const cat = getCatalogue();
  const key = clientCatalogueKey(cat);
  if (!m || m[1] !== key) {
    return new Response("Not found", { status: 404, headers: { "cache-control": "no-store" } });
  }
  let body = bodies.get(cat);
  if (!body) {
    body = JSON.stringify(toClientCatalogue(cat.release(), cat.sources(), cat.rows()));
    bodies.set(cat, body);
  }
  return new Response(body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": key === "dev" ? "no-cache" : "public, max-age=31536000, immutable",
    },
  });
}
