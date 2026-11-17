// One fetch of the compact client catalogue per page, shared by Explore and the hero (T-080).
import type { ClientCatalogue } from "./explore-data";

const pending = new Map<string, Promise<ClientCatalogue | null>>();

/** Fetches `/data/catalogue-<release>.json` once per URL; null when it can't be read. */
export function loadClientCatalogue(url: string): Promise<ClientCatalogue | null> {
  let p = pending.get(url);
  if (!p) {
    p = fetch(url)
      .then((r) => (r.ok ? (r.json() as Promise<ClientCatalogue>) : null))
      .catch(() => null);
    pending.set(url, p);
    // A failed load may be retried later (e.g. offline for a moment).
    void p.then((c) => {
      if (!c) pending.delete(url);
    });
  }
  return p;
}
