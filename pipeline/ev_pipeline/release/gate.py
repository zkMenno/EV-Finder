"""Licence gate (Decision 009): which sources may reach a public release.

A source is releasable only when data/sources.yaml lists it with `status: active` AND a named
licence (not empty, "none" or "unknown"). Anything else, including sources missing from the
registry, is dropped before matching and guarded again before writing. `nyland` is always
excluded (matcher.EXCLUDED_SOURCES), registry or not.

Licences marked "(to confirm)" on an active source (EEA tonight) pass the gate: the status is
the explicit switch; see QUESTIONS.md Q-022.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.match.matcher import EXCLUDED_SOURCES

_NO_LICENCE = {"", "none", "unknown", "n/a"}


@dataclass
class SourceEntry:
    id: str
    name: str
    licence: str
    status: str
    owner: str = ""
    terms: str = ""


@dataclass
class Registry:
    sources: dict[str, SourceEntry] = field(default_factory=dict)
    loaded: bool = False

    def reason_blocked(self, source_id: str) -> str | None:
        """None when releasable, else why not."""
        if source_id in EXCLUDED_SOURCES:
            return "permission pending (hard exclusion)"
        if not self.loaded:
            return None  # no registry file: only the hard floor applies
        entry = self.sources.get(source_id)
        if entry is None:
            return "not in data/sources.yaml"
        if entry.status != "active":
            return f"status {entry.status}"
        lic = entry.licence.split("(")[0].strip().lower()
        if lic in _NO_LICENCE or lic.startswith("unknown") or lic.startswith("none"):
            return f"no named licence ({entry.licence})"
        return None

    def releasable(self, source_id: str) -> bool:
        return self.reason_blocked(source_id) is None

    def source_object(self, source_id: str) -> dict[str, Any] | None:
        e = self.sources.get(source_id)
        if e is None:
            return None
        return {"id": e.id, "name": e.name, "licence": e.licence.split("(")[0].strip()}


def parse_registry(data: dict[str, Any]) -> Registry:
    out: dict[str, SourceEntry] = {}
    for s in data.get("sources") or []:
        out[s["id"]] = SourceEntry(
            id=s["id"],
            name=str(s.get("name", s["id"])),
            licence=str(s.get("licence") or ""),
            status=str(s.get("status") or ""),
            owner=str(s.get("owner") or ""),
            terms=str(s.get("terms") or ""),
        )
    return Registry(out, loaded=True)


def load_registry(path: Path) -> Registry:
    if not path.exists():
        return Registry()
    return parse_registry(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
