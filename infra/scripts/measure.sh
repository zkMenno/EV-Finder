#!/usr/bin/env bash
# Read-only server measurement for WS4 (Q-001 capacity, T-040 touch points, Postgres checks).
# Menno runs it on the AppInfra server and pastes the output into the WS4 chat:
#
#   bash measure.sh [postgres-container-name] > /tmp/ev-measure.txt 2>&1
#
# It changes nothing: no writes, no restarts, no pulls. Run it once on a busy evening
# (after 19:00 UTC) for Q-001. The output names containers, networks and mounts of the
# real server: paste it in the chat, never commit it to the public repo.
set -u

section() { printf '\n===== %s =====\n' "$1"; }

section "time"
date -u '+%Y-%m-%d %H:%M:%S UTC'

section "host"
uname -m; nproc
uptime
free -m
df -h / /srv 2>/dev/null | sort -u
cat /proc/pressure/memory 2>/dev/null
cat /proc/pressure/cpu 2>/dev/null

section "containers (limits)"
docker ps --format '{{.Names}}' | while read -r c; do
  docker inspect -f '{{.Name}} mem={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}} restart={{.HostConfig.RestartPolicy.Name}} image={{.Config.Image}}' "$c"
done

section "docker stats (one sample)"
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'

section "docker disk"
docker system df

section "networks"
docker network ls --format '{{.Name}}\t{{.Driver}}'

section "caddy (mounts + how it is run)"
for c in $(docker ps --format '{{.Names}}' | grep -i caddy); do
  docker inspect -f '{{.Name}} {{range .Mounts}}{{.Source}}->{{.Destination}} {{end}}' "$c"
  docker inspect -f '{{.Name}} networks: {{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$c"
done
command -v caddy >/dev/null && echo "caddy also installed on the host: $(caddy version)"

section "postgres"
PG="${1:-$(docker ps --format '{{.Names}}' | grep -iE 'postgres|postgis|db' | head -1)}"
if [ -n "$PG" ]; then
  echo "container: $PG"
  docker inspect -f 'networks: {{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$PG"
  docker exec "$PG" psql -U postgres -At -c 'select version();' \
    -c "select name, default_version, installed_version from pg_available_extensions where name in ('pg_trgm','postgis') order by name;" \
    -c "select datname from pg_database where not datistemplate order by 1;" \
    -c "show max_connections;" \
    -c "select count(*) as live_connections from pg_stat_activity;"
else
  echo "no postgres container found; pass its name as the first argument"
fi

section "ev (if present)"
ls -la /srv/ev 2>/dev/null || echo "/srv/ev does not exist yet"
