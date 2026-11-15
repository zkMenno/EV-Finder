# syntax=docker/dockerfile:1
# EV Finder web image (T-013, Decisions 005, 006, 008).
# Build context = repo root:
#   docker buildx build --platform linux/arm64 -f apps/web/Dockerfile -t ev-finder-web .
# Built in CI (.github/workflows/images.yml) for linux/arm64; never on the shared server.

ARG NODE_VERSION=22

# ---- base: Node + pnpm (version from "packageManager" in package.json, via corepack) ----
FROM node:${NODE_VERSION}-slim AS base
ENV PNPM_HOME=/pnpm \
    PATH=/pnpm:$PATH \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    NEXT_TELEMETRY_DISABLED=1
RUN corepack enable
WORKDIR /repo

# ---- deps: install only what @ev/web needs, from the workspace lockfile ----
FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc tsconfig.base.json ./
COPY apps/web/package.json apps/web/
COPY packages/schema/package.json packages/schema/
# Optional secret `extra_ca`: a CA bundle for builds behind a TLS-intercepting proxy
# (`--secret id=extra_ca,src=ca.crt`). Not needed in CI; never stored in a layer.
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    --mount=type=secret,id=extra_ca,required=false \
    NODE_EXTRA_CA_CERTS=$([ -f /run/secrets/extra_ca ] && echo /run/secrets/extra_ca) \
    pnpm install --frozen-lockfile --filter "@ev/web..."

# ---- build: Next standalone output ----
FROM deps AS build
COPY packages/schema packages/schema
# config/countries/ is not in the build context (.dockerignore); scripts/listings.mjs then keeps the
# committed src/config/listings.generated.json, which a unit test keeps in step with the YAML.
COPY apps/web apps/web
RUN pnpm --filter @ev/web build

# ---- catalogue: copy only the latest published release (data/releases/<latest>) ----
FROM busybox:stable AS catalogue
COPY data/releases /src
RUN set -eu; \
    n="$(tr -d '[:space:]' < /src/latest)"; \
    case "$n" in ''|*[!0-9]*) echo "data/releases/latest must hold a release number, got '$n'" >&2; exit 1;; esac; \
    test -f "/src/$n/catalogue.json" || { echo "data/releases/$n/catalogue.json missing" >&2; exit 1; }; \
    mkdir -p "/out/$n"; \
    cp "/src/$n/catalogue.json" "/out/$n/"; \
    if [ -f "/src/$n/README.md" ]; then cp "/src/$n/README.md" "/out/$n/"; fi; \
    printf '%s\n' "$n" > /out/latest

# ---- runtime: standalone server, non-root, read-only friendly ----
FROM node:${NODE_VERSION}-slim AS runtime
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0 \
    CATALOGUE_DIR=/app/data/releases
WORKDIR /app

# Files stay root-owned (read-only for the app user); only .next/cache is writable,
# so the container also runs with a read-only root filesystem plus a tmpfs there.
COPY --from=build /repo/apps/web/.next/standalone ./
COPY --from=build /repo/apps/web/.next/static ./apps/web/.next/static
COPY --from=catalogue /out ./data/releases
RUN mkdir -p apps/web/.next/cache && chown node:node apps/web/.next/cache

USER node
EXPOSE 3000

# node:*-slim has no curl/wget, so probe /health with Node's fetch.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]

CMD ["node", "apps/web/server.js"]
