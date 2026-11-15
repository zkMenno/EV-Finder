// Tiny persisted list store (no library): localStorage + in-memory cache + subscribers,
// synced across tabs via the `storage` event. Used by the compare tray and favourites.
import { browserStorage, readStorage, writeStorage, type KeyValueStorage } from "./storage";

export interface ListStore<T> {
  get(): readonly T[];
  set(next: readonly T[]): void;
  subscribe(fn: () => void): () => void;
}

const EMPTY: readonly never[] = Object.freeze([]);

export function createListStore<T>(opts: {
  key: string;
  parse: (raw: unknown) => T[];
  storage?: () => KeyValueStorage | null;
}): ListStore<T> {
  const storage = opts.storage ?? browserStorage;
  let cache: readonly T[] | null = null;
  const subs = new Set<() => void>();

  const load = (): readonly T[] => {
    const raw = readStorage(opts.key, storage());
    if (!raw) return EMPTY;
    try {
      return Object.freeze(opts.parse(JSON.parse(raw) as unknown));
    } catch {
      return EMPTY;
    }
  };
  const notify = () => subs.forEach((fn) => fn());

  let listening = false;
  const onStorage = (e: StorageEvent) => {
    if (e.key === opts.key) {
      cache = load();
      notify();
    }
  };

  return {
    get() {
      if (cache === null) cache = load();
      return cache;
    },
    set(next) {
      cache = Object.freeze([...next]);
      writeStorage(opts.key, JSON.stringify(cache), storage());
      notify();
    },
    subscribe(fn) {
      subs.add(fn);
      if (!listening && typeof window !== "undefined") {
        window.addEventListener("storage", onStorage);
        listening = true;
      }
      return () => {
        subs.delete(fn);
        if (!subs.size && listening) {
          window.removeEventListener("storage", onStorage);
          listening = false;
        }
      };
    },
  };
}

export function getEmpty<T>(): readonly T[] {
  return EMPTY;
}
