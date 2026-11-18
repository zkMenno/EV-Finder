#!/usr/bin/env bash
# Upload one release folder as GitHub Release assets (T-064, Decision 035).
#
#   pipeline/scripts/gh-publish-release.sh <release-folder> [--replace-unmerged]
#
# Shell + jq + gh + sha256sum only, so a workflow's write job can run it without installing
# or running pipeline code. Every file is checked against manifest.json (size + sha256) before
# upload. An existing tag whose assets already match is left alone ("unchanged"). With
# --replace-unmerged an existing tag with different assets is replaced, but only when
# origin/main has no manifest for this release yet (an unmerged "Data release N" PR): a merged
# release never changes. Uploads go into a draft in paced batches with back-off and only a
# complete, manifest-matching draft is published, so a stopped run resumes on re-run
# (UPLOAD_BATCH, UPLOAD_PAUSE_S, UPLOAD_RETRIES, UPLOAD_BACKOFF_S tune it). Needs GH_TOKEN with
# contents: write and GITHUB_REPOSITORY.
set -euo pipefail

dir=${1:?usage: gh-publish-release.sh <release-folder> [--replace-unmerged]}
replace=${2:-}
repo=${GITHUB_REPOSITORY:?GITHUB_REPOSITORY not set}
m="$dir/manifest.json"
[ -f "$m" ] || { echo "::error::$m missing"; exit 1; }
[ "$(jq -r .schema "$m")" = "ev-release-manifest/1" ] || { echo "::error::unknown manifest schema"; exit 1; }
n=$(jq -r .release "$m")
case "$n" in ''|*[!0-9]*) echo "::error::bad release number '$n'"; exit 1;; esac
tag=$(jq -r .storage.tag "$m")
[ "$tag" = "data-v$n" ] || { echo "::error::tag '$tag' is not data-v$n"; exit 1; }

# Assets are compared by GitHub's sha256 digest against the manifest (size only for an asset
# GitHub gives no digest for), and only fully uploaded ones count (#162 review).
declare -A want_sha want_bytes have_digest have_size have_state
while IFS=$'\t' read -r asset bytes sha; do
  want_sha[$asset]=$sha; want_bytes[$asset]=$bytes
done < <(jq -r '.files[] | [.asset, (.bytes|tostring), .sha256] | @tsv' "$m")

load_assets() {  # fills have_*; returns 1 when the release does not exist
  local out err
  have_digest=(); have_size=(); have_state=()
  if ! out=$(gh release view "$tag" --repo "$repo" --json assets \
      -q '.assets[] | [.name, (.digest // "-"), (.size|tostring), .state] | @tsv' 2>"$errf"); then
    err=$(cat "$errf")
    case "$err" in *"release not found"*|*"Not Found"*) return 1;; esac
    echo "::error::cannot read release $tag: $err"; exit 1  # never guess "new" on an error
  fi
  while IFS=$'\t' read -r a d s st; do
    [ -n "$a" ] || continue
    have_digest[$a]=$d; have_size[$a]=$s; have_state[$a]=$st
  done <<< "$out"
}
asset_ok() {  # $1 = asset name: uploaded and identical to the manifest's file
  local a=$1
  [ "${have_state[$a]:-}" = uploaded ] || return 1
  if [ "${have_digest[$a]:--}" != - ]; then [ "${have_digest[$a]}" = "sha256:${want_sha[$a]}" ]
  else [ "${have_size[$a]:-}" = "${want_bytes[$a]}" ]; fi
}
all_ok() {
  local a
  [ "${#have_state[@]}" = "${#want_sha[@]}" ] || return 1
  for a in "${!want_sha[@]}"; do asset_ok "$a" || return 1; done
}

errf=$(mktemp)
existing=0
draft=false
if load_assets; then
  existing=1
  draft=$(gh release view "$tag" --repo "$repo" --json isDraft -q .isDraft)
  if [ "$draft" != true ] && all_ok; then
    echo "release $n: unchanged ($tag)"; exit 0  # also fine when the files aren't on disk here
  fi
fi

stage=$(mktemp -d)
trap 'rm -rf "$stage" "$errf"' EXIT
# Flat copies named like the assets, each verified against the manifest.
while IFS=$'\t' read -r path asset bytes sha; do
  case "$path" in /*|*..*|*\\*) echo "::error::unsafe path '$path'"; exit 1;; esac
  case "$asset" in */*|.*) echo "::error::unsafe asset name '$asset'"; exit 1;; esac
  f="$dir/$path"
  [ -f "$f" ] && [ ! -L "$f" ] || { echo "::error::$path missing"; exit 1; }
  [ "$(wc -c < "$f" | tr -d ' ')" = "$bytes" ] || { echo "::error::$path size differs from manifest"; exit 1; }
  [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$sha" ] || { echo "::error::$path sha256 differs from manifest"; exit 1; }
  cp "$f" "$stage/$asset"
done < <(jq -r '.files[] | [.path, .asset, (.bytes|tostring), .sha256] | @tsv' "$m")

notes="$stage/.notes.md"
{
  echo "EV Finder catalogue data release $n (generated $(jq -r .generated_at "$m"))."
  echo
  echo "$(jq -r .counts.rows "$m") variants, $(jq -r .counts.files "$m") files, QA $(jq -r .qa.status "$m")."
  echo "Checksums: \`data/releases/$n/manifest.json\`. Our own output is CC BY 4.0; third-party inputs keep their licences (README.md, open.ATTRIBUTION.md)."
} > "$notes"

if [ "$existing" = 1 ] && [ "$draft" != true ]; then
  if [ "$replace" != "--replace-unmerged" ]; then
    echo "::error::$tag exists with different assets; a published release never changes"; exit 1
  fi
  # Fail closed: if main can't be read, don't replace anything.
  git fetch --quiet --depth=1 origin "${MAIN_BRANCH:-main}" || { echo "::error::cannot read origin/${MAIN_BRANCH:-main}"; exit 1; }
  if git cat-file -e "FETCH_HEAD:data/releases/$n/manifest.json" 2>/dev/null; then
    echo "::error::release $n is merged on main; refusing to replace $tag"; exit 1
  fi
  # An unmerged release is replaced whole (title, notes and tag target included), as before.
  gh release delete "$tag" --repo "$repo" --yes --cleanup-tag
  existing=0
fi
# A draft is an earlier upload of this release that stopped part-way (e.g. GitHub's secondary
# rate limit): it was never published, so it is resumed, not refused.
if [ "$existing" = 0 ]; then
  gh release create "$tag" --repo "$repo" --title "Data release $n" --notes-file "$notes" \
    --latest=false --draft
  have_digest=(); have_size=(); have_state=()
fi

# Resume: drop assets that are not in the manifest or differ from it, upload the rest in small
# paced batches with back-off. Uploading every asset at once trips GitHub's secondary rate
# limit once a release carries photos (release 3: ~650 assets).
for a in "${!have_state[@]}"; do
  if [ -z "${want_sha[$a]:-}" ] || ! asset_ok "$a"; then
    gh release delete-asset "$tag" "$a" --repo "$repo" --yes
  fi
done
todo=()
for a in $(printf '%s\n' "${!want_sha[@]}" | sort); do
  asset_ok "$a" || todo+=("$stage/$a")
done
batch=${UPLOAD_BATCH:-10} pause=${UPLOAD_PAUSE_S:-10} retries=${UPLOAD_RETRIES:-6} backoff=${UPLOAD_BACKOFF_S:-60}
echo "release $n: uploading ${#todo[@]} of $(jq '.files|length' "$m") assets in batches of $batch"
for ((i = 0; i < ${#todo[@]}; i += batch)); do
  chunk=("${todo[@]:i:batch}")
  for ((try = 1; ; try++)); do
    if gh release upload "$tag" --repo "$repo" --clobber "${chunk[@]}"; then break; fi
    if [ "$try" -ge "$retries" ]; then
      echo "::error::upload failed $retries times; re-run the job to resume (the draft keeps what is up)"; exit 1
    fi
    echo "upload failed (try $try), waiting $((backoff * try)) s"; sleep $((backoff * try))
  done
  [ $((i + batch)) -lt ${#todo[@]} ] && sleep "$pause"
done

load_assets || { echo "::error::$tag disappeared during the upload"; exit 1; }
all_ok || { echo "::error::$tag assets don't match the manifest after upload"; exit 1; }
gh release edit "$tag" --repo "$repo" --draft=false --latest=false
echo "release $n: published ($tag, $(jq '.files|length' "$m") assets)"
