"""Licence gate (Decision 009): which sources may reach a public release.

Fails closed (T-006 review):
- No data/sources.yaml -> the release FAILS (`ReleaseError` in build_release); nothing is
  released on the strength of a missing registry.
- A source is releasable only when the registry lists it with `status: active` (or
  `active_pending_confirmation`, Decision 037) AND either a
  named, confirmed licence or `permission: written` (explicit written permission, logged).
- A licence that is empty, "none", "unknown", "n/a" or still marked "(to confirm)" is not a
  named licence. That matches data/sources.yaml: "(to confirm)" licences stay blocked until
  checked. `permission: written` is the only override; no source sets it tonight.
- `nyland` is always excluded (matcher.EXCLUDED_SOURCES), whatever the registry says.
- `aliases` (Q-075): a source may list other ids it is known by (e.g. `bnetza` carries
  `bnetza-ladesaeulenregister`, the id the charging taxonomies use). An alias is gated exactly
  like its registry entry; an alias that clashes with another entry or alias is ignored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.match.matcher import EXCLUDED_SOURCES

_NO_LICENCE = {"", "none", "unknown", "n/a"}
# Statuses that may reach a release. `active_pending_confirmation` (Decision 037): in use
# now, credited, reuse terms being confirmed in writing; a "no" removes it next release.
RELEASABLE_STATUSES = frozenset({"active", "active_pending_confirmation"})
WRITTEN_PERMISSION = "written"
MISSING_REGISTRY = "no data/sources.yaml (licence registry missing; release blocked)"


@dataclass
class SourceEntry:
    id: str
    name: str
    licence: str
    status: str
    owner: str = ""
    terms: str = ""
    permission: str = ""  # "written" = explicit written permission from the owner


def licence_problem(licence: str) -> str | None:
    """None when `licence` names a confirmed licence, else why not."""
    text = licence.strip().lower()
    base = text.split("(")[0].strip()
    if base in _NO_LICENCE or base.startswith(("unknown", "none")):
        return f"no named licence ({licence})"
    if "to confirm" in text or "unconfirmed" in text:
        return f"licence not confirmed ({licence})"
    return None


@dataclass
class Registry:
    sources: dict[str, SourceEntry] = field(default_factory=dict)
    loaded: bool = False
    aliases: dict[str, str] = field(default_factory=dict)  # alias id -> registry id

    def canonical(self, source_id: str) -> str:
        """The registry id for `source_id` (itself unless it is a known alias)."""
        return source_id if source_id in self.sources else self.aliases.get(source_id, source_id)

    def reason_blocked(self, source_id: str) -> str | None:
        """None when releasable, else why not."""
        if source_id in EXCLUDED_SOURCES:
            return "permission pending (hard exclusion)"
        if not self.loaded:
            return MISSING_REGISTRY
        source_id = self.canonical(source_id)
        if source_id in EXCLUDED_SOURCES:
            return "permission pending (hard exclusion)"
        entry = self.sources.get(source_id)
        if entry is None:
            return "not in data/sources.yaml"
        if entry.status not in RELEASABLE_STATUSES:
            return f"status {entry.status}"
        if entry.permission == WRITTEN_PERMISSION:
            return None
        return licence_problem(entry.licence)

    def releasable(self, source_id: str) -> bool:
        return self.reason_blocked(source_id) is None

    def source_object(self, source_id: str) -> dict[str, Any] | None:
        e = self.sources.get(self.canonical(source_id))
        if e is None:
            return None
        return {"id": e.id, "name": e.name, "licence": e.licence.split("(")[0].strip()}


def parse_registry(data: dict[str, Any]) -> Registry:
    out: dict[str, SourceEntry] = {}
    alias_of: dict[str, set[str]] = {}
    for s in data.get("sources") or []:
        for a in s.get("aliases") or []:
            alias_of.setdefault(str(a), set()).add(s["id"])
        out[s["id"]] = SourceEntry(
            id=s["id"],
            name=str(s.get("name", s["id"])),
            licence=str(s.get("licence") or ""),
            status=str(s.get("status") or ""),
            owner=str(s.get("owner") or ""),
            terms=str(s.get("terms") or ""),
            permission=str(s.get("permission") or "").strip().lower(),
        )
    aliases = {a: next(iter(ids)) for a, ids in alias_of.items() if len(ids) == 1 and a not in out}
    return Registry(out, loaded=True, aliases=aliases)


def load_registry(path: Path) -> Registry:
    if not path.exists():
        return Registry()
    return parse_registry(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
