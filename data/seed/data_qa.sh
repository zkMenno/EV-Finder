#!/bin/sh
# WS3 pre-push data QA: the four data-qa steps CI runs (.github/workflows/ci.yml, job data-qa),
# in the same order, so a seed / taxonomy / editorial change is green before it is pushed.
# Retro 2026-11-17 (WS3 3rd chat): two of four validators run by hand, CI caught the third.
#
# Usage (from anywhere in the repo):   sh data/seed/data_qa.sh
# Exit 0 = all four pass; otherwise the first failing step's exit code. Needs uv (pipeline env).
set -u
root=$(git rev-parse --show-toplevel) || exit 1
cd "$root/pipeline" || exit 1
fail=0
step() {
  name=$1; shift
  printf '== %s\n' "$name"
  if ! "$@"; then
    printf 'FAIL: %s\n' "$name"
    [ "$fail" -eq 0 ] && fail=1
  fi
}
step "validate seed models" uv run python -I ../data/seed/validate_seed.py ../data/seed/models.yaml
step "validate seed variants" uv run python -I ../data/seed/validate_variants.py
step "validate taxonomy, platforms, packs, links" uv run python -I ../data/taxonomy/validate_taxonomy.py
step "back-test shortlist rules (Decision 038)" uv run python -I ../data/editorial/backtest_rules.py
if [ "$fail" -ne 0 ]; then
  echo "data QA: FAILED (see above)"; exit 1
fi
echo "data QA: all four steps pass"
