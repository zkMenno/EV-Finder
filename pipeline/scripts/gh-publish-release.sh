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
# release never changes. Needs GH_TOKEN with contents: write and GITHUB_REPOSITORY.
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

want=$(jq -r '.files[] | "\(.asset)\t\(.bytes)"' "$m" | sort)
existing=0
if have=$(gh release view "$tag" --repo "$repo" --json assets -q '.assets[] | "\(.name)\t\(.size)"' 2>/dev/null); then
  existing=1
  if [ "$(printf '%s\n' "$have" | sort)" = "$want" ]; then
    echo "release $n: unchanged ($tag)"; exit 0  # also fine when the files aren't on disk here
  fi
fi

stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
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

if [ "$existing" = 1 ]; then
  if [ "$replace" != "--replace-unmerged" ]; then
    echo "::error::$tag exists with different assets; a published release never changes"; exit 1
  fi
  # Fail closed: if main can't be read, don't replace anything.
  git fetch --quiet --depth=1 origin "${MAIN_BRANCH:-main}" || { echo "::error::cannot read origin/${MAIN_BRANCH:-main}"; exit 1; }
  if git cat-file -e "FETCH_HEAD:data/releases/$n/manifest.json" 2>/dev/null; then
    echo "::error::release $n is merged on main; refusing to replace $tag"; exit 1
  fi
  gh release delete "$tag" --repo "$repo" --yes --cleanup-tag
fi

notes="$stage/.notes.md"
{
  echo "EV Finder catalogue data release $n (generated $(jq -r .generated_at "$m"))."
  echo
  echo "$(jq -r .counts.rows "$m") variants, $(jq -r .counts.files "$m") files, QA $(jq -r .qa.status "$m")."
  echo "Checksums: \`data/releases/$n/manifest.json\`. Our own output is CC BY 4.0; third-party inputs keep their licences (README.md, open.ATTRIBUTION.md)."
} > "$notes"
gh release create "$tag" --repo "$repo" --title "Data release $n" --notes-file "$notes" \
  --latest=false "$stage"/*
have=$(gh release view "$tag" --repo "$repo" --json assets -q '.assets[] | "\(.name)\t\(.size)"' | sort)
[ "$have" = "$want" ] || { echo "::error::$tag assets don't match the manifest after upload"; exit 1; }
echo "release $n: published ($tag, $(jq '.files|length' "$m") assets)"
