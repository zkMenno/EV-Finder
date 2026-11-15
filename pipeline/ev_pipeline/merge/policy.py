"""Per-field merge policy from data/field_sources.yaml (Decision 009, provisional).

Each field lists `primary` and `fallbacks` source ids (that order is the priority order), a
`tolerance` ({pct: x} or {abs: x, unit}) and a merge mode:
- priority: the highest-priority source wins; recency breaks ties within one source.
- median:   take the highest-priority value, collect every value within tolerance of it and
            pick their *low median*: a real observed value, never an average.
- newest:   the most recently retrieved value wins (then model year, then priority).

Optional keys: `agreement_wins: false` turns off "agreement beats priority" (merge.py);
`needs_backing: [source ids]`: a value whose agreeing sources are only these is withheld and
sent to review (qa/value_guard.py, A-05 F9); `cited_wins: false` turns off "a cited value
beats a lone source" (merge.py); `mixup_with: [fields]`: a value equal (within 0.5) to one of
those fields on the same row or record is a likely field mix-up and goes to review unless
another source backs it (qa/value_guard.py, e.g. ac_kw that is really the battery size);
`seed_counts_as_backing: true`: for `needs_backing`, an agreeing *uncited* seed-manual value
counts as backing (default false; explicit policy, A-06 F4); `same_origin: {source: origin}`:
for this field, that source's values come from that origin and count once with it towards
"N sources agree" (e.g. OpenEV's EPA range is EPA's own figure, A-06 F8).

Sources not listed for a field rank below every listed one, in the default order
(matcher.SOURCE_PRIORITY). Fields not in the file keep the overnight defaults: majority of 3+
agreeing values, else priority, recency as tie-breaker, 3% tolerance (`mode = "default"`).
Prices map to `price_new_<cc>` when the file has one (e.g. `price_new_fr`), else
`price_new_nl` (NL) and `price_new_other` (other countries).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.match.matcher import priority_of

DEFAULT_TOLERANCE_PCT = 3.0


@dataclass(frozen=True)
class FieldPolicy:
    order: tuple[str, ...] = ()
    mode: str = "default"  # default | priority | median | newest
    tol_pct: float | None = DEFAULT_TOLERANCE_PCT
    tol_abs: float | None = None
    tol_unit: str | None = None
    # A-05 F1 (c): in priority mode, 2+ agreeing independent origins outvote the winner.
    agreement_wins: bool = True
    # A-05 F9: sources whose value is withheld (review) unless another source agrees.
    needs_backing: tuple[str, ...] = ()
    # A cited value (seed `cited:` or a manual fact) outvotes a value only one origin backs.
    cited_wins: bool = True
    # Fields this one must not simply repeat (qa/value_guard.guard_mixups), e.g. ac_kw vs the
    # battery: KilowattApp gives the Zoe R240 23.3 kW AC, which is its battery size.
    mixup_with: tuple[str, ...] = ()
    # A-06 F4: an uncited seed-manual value that agrees counts as backing for needs_backing.
    seed_counts_as_backing: bool = False
    # A-06 F8: field-level same origin, ((source, origin), ...) (a tuple keeps this hashable).
    same_origin: tuple[tuple[str, str], ...] = ()

    def origin(self, source_id: str) -> str | None:
        """The field-level origin of `source_id` (`same_origin:`), else None."""
        return next((o for s, o in self.same_origin if s == source_id), None)

    def priority(self, source_id: str) -> int:
        if source_id in self.order:
            return 1000 - self.order.index(source_id)
        return priority_of(source_id)

    def agree(self, a: object, b: object) -> bool:
        if isinstance(a, bool) or isinstance(b, bool):
            return a == b
        if isinstance(a, int | float) and isinstance(b, int | float):
            if self.tol_abs is not None:
                return abs(a - b) <= self.tol_abs + 1e-9
            scale = max(abs(a), abs(b))
            return scale == 0 or abs(a - b) <= (self.tol_pct or 0) / 100 * scale + 1e-9
        return a == b

    def tolerance_text(self) -> str:
        if self.tol_abs is not None:
            return f"±{self.tol_abs:g}{(' ' + self.tol_unit) if self.tol_unit else ''}"
        return f"±{self.tol_pct:g}%"


DEFAULT_POLICY = FieldPolicy()


@dataclass
class Policies:
    fields: dict[str, FieldPolicy] = field(default_factory=dict)

    def for_field(self, name: str) -> FieldPolicy:
        if name.startswith("price_new."):
            cc = name.split(".", 1)[1].lower()
            if f"price_new_{cc}" in self.fields:  # e.g. price_new_fr (ADEME first)
                return self.fields[f"price_new_{cc}"]
            name = "price_new_nl" if cc == "nl" else "price_new_other"
        return self.fields.get(name, DEFAULT_POLICY)


def parse_policies(data: dict[str, Any]) -> Policies:
    out: dict[str, FieldPolicy] = {}
    for name, spec in (data.get("fields") or {}).items():
        spec = spec or {}
        order = tuple(spec.get("primary") or []) + tuple(spec.get("fallbacks") or [])
        tol = spec.get("tolerance") or {}
        tol_abs = tol.get("abs")
        tol_pct = tol.get("pct")
        if tol_abs is None and tol_pct is None:
            tol_pct = DEFAULT_TOLERANCE_PCT
        out[name] = FieldPolicy(
            order=order,
            mode=spec.get("merge", "priority"),
            tol_pct=None if tol_pct is None else float(tol_pct),
            tol_abs=None if tol_abs is None else float(tol_abs),
            tol_unit=tol.get("unit"),
            agreement_wins=bool(spec.get("agreement_wins", True)),
            needs_backing=tuple(spec.get("needs_backing") or ()),
            cited_wins=bool(spec.get("cited_wins", True)),
            mixup_with=tuple(spec.get("mixup_with") or ()),
            seed_counts_as_backing=bool(spec.get("seed_counts_as_backing", False)),
            same_origin=tuple(sorted((str(k), str(v)) for k, v in _mapping(spec, "same_origin"))),
        )
    return Policies(out)


def _mapping(spec: dict[str, Any], key: str) -> list[tuple[Any, Any]]:
    raw = spec.get(key) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"field_sources.yaml: {key} must map source ids to origins")
    return list(raw.items())


def load_policies(path: Path) -> Policies:
    if not path.exists():
        return Policies()
    return parse_policies(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
