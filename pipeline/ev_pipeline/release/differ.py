"""T-123: release diff, release N against N-1, with approved changes.

No release ships a change nobody intended. Every record set in `config/approved_changes.yaml`
(catalogue rows and generations, shortlist scores, used prices, consumption matrix, towns and
stations) is compared per id and field. What doesn't count: key order, floats beyond the set
precision, the ignored keys (generated_at, provenance, ...), and the order of plain lists.

Kinds: added / removed (a record), changed / filled / cleared (a field), source_lost (a
number that still ships but lost its source), file_removed. Status per change:
- blocking: an unapproved removal, a change beyond the field's threshold, a cleared value of a
  thresholded field, any source_lost or file_removed -> the `release_diff` QA check fails
- approved: matched an `approved` entry (reason + "PR #n" / "Decision nnn" required)
- retired: a removed variant id that the new release's retired_ids map redirects (T-062)
- review: everything else (listed, never blocks)
Charging figures (Decision 040 item 4) go through the same report, review only: the rows of
`charging_review_rows` (steps, falls, revisions, dropped dates) become `charging` changes.

Outputs: rows for `data/review/release_diff.csv` and a summary for qa.json `release_diff`.
Pure functions over two release folders; nothing here touches the network.
"""

from __future__ import annotations

import csv
import fnmatch
import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.release.build import REPO_ROOT

CONFIG_FILE = REPO_ROOT / "config" / "approved_changes.yaml"
FORMAT = "approved-changes/v1"
REVIEW_FILE = "release_diff.csv"
COLUMNS = [
    "file", "records", "id", "field", "kind", "old", "new", "delta", "rel_delta",
    "status", "rule", "approval", "reason",
]  # fmt: skip
KINDS = {"changed", "filled", "cleared", "removed", "added", "source_lost", "file_removed"}
CHANGE_SCOPES = KINDS - {"added", "filled"} | {"any"}
BLOCKING_ALWAYS = {"source_lost", "file_removed"}
# Fields that key a list item (first ones present, joined by '/'); otherwise list position.
KEY_FIELDS = (
    "variant_id", "id", "country", "build_year", "kind", "period", "period_end", "road_band",
    "temperature_band_id", "heater_type_id", "source_id", "level",
)  # fmt: skip
SOURCE_KEYS = ("source_ids", "source_id", "source", "list_source_ids", "sources")
APPROVER = re.compile(r"^(PR #\d+|Decision \d{3})\b")
CHARGING_FILE = "charging_stats.json"
TOP = 10
MAX_LISTED = 50


class DiffConfigError(ValueError):
    pass


# --- config ------------------------------------------------------------------------------


@dataclass(frozen=True)
class Threshold:
    file: str
    field: str
    rel: float | None = None
    abs: float | None = None
    any: bool = False

    def label(self) -> str:
        parts = ["any"] if self.any else []
        if self.rel is not None:
            parts.append(f"rel {self.rel:g}")
        if self.abs is not None:
            parts.append(f"abs {self.abs:g}")
        return f"{self.file}:{self.field} ({', '.join(parts)})"


@dataclass(frozen=True)
class Approval:
    index: int
    reason: str
    approved_by: str
    release: tuple[int, ...] | None = None
    file: str = "*"
    id: str = "*"
    field: str = "*"
    change: str = "any"

    def applies_to(self, release: int | None) -> bool:
        return self.release is None or release in self.release

    def matches(self, c: Change) -> bool:
        return (
            fnmatch.fnmatchcase(c.file, self.file)
            and fnmatch.fnmatchcase(c.id, self.id)
            and fnmatch.fnmatchcase(c.field, self.field)
            and (self.change == "any" or self.change == c.kind)
        )

    def label(self) -> str:
        return f"#{self.index} {self.approved_by}"


@dataclass
class Config:
    precision: int = 3
    ignore: frozenset[str] = frozenset()
    files: list[dict[str, Any]] = field(default_factory=list)
    thresholds: list[Threshold] = field(default_factory=list)
    approved: list[Approval] = field(default_factory=list)
    path: str = ""
    sha256: str = ""

    def threshold(self, file: str, fld: str) -> Threshold | None:
        for t in self.thresholds:
            if fnmatch.fnmatchcase(file, t.file) and fnmatch.fnmatchcase(fld, t.field):
                return t
        return None


def _num_or_none(entry: dict[str, Any], key: str, where: str) -> float | None:
    v = entry.get(key)
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, int | float) or v < 0:
        raise DiffConfigError(f"{where}: {key} must be a number >= 0")
    return float(v)


def parse_config(doc: dict[str, Any], path: str = "", sha256: str = "") -> Config:
    if not isinstance(doc, dict) or doc.get("schema") != FORMAT:
        raise DiffConfigError(f"{path or 'config'}: schema must be {FORMAT}")
    files = doc.get("files") or []
    for i, f in enumerate(files):
        if not isinstance(f, dict) or not f.get("file") or not f.get("records"):
            raise DiffConfigError(f"files[{i}]: needs file and records")
    thresholds = []
    for i, t in enumerate(doc.get("thresholds") or []):
        where = f"thresholds[{i}]"
        if not isinstance(t, dict) or not t.get("file") or not t.get("field"):
            raise DiffConfigError(f"{where}: needs file and field")
        th = Threshold(
            str(t["file"]),
            str(t["field"]),
            _num_or_none(t, "rel", where),
            _num_or_none(t, "abs", where),
            bool(t.get("any")),
        )
        if not th.any and th.rel is None and th.abs is None:
            raise DiffConfigError(f"{where}: needs rel, abs or any: true")
        thresholds.append(th)
    approved = []
    for i, a in enumerate(doc.get("approved") or []):
        where = f"approved[{i}]"
        if not isinstance(a, dict):
            raise DiffConfigError(f"{where}: must be a mapping")
        reason, by = str(a.get("reason") or "").strip(), str(a.get("approved_by") or "").strip()
        if not reason:
            raise DiffConfigError(f"{where}: reason is required")
        if not APPROVER.match(by):
            raise DiffConfigError(
                f"{where}: approved_by must start with 'PR #<n>' or 'Decision <nnn>'"
            )
        change = str(a.get("change") or "any")
        if change not in CHANGE_SCOPES:
            raise DiffConfigError(f"{where}: change must be one of {sorted(CHANGE_SCOPES)}")
        rel = a.get("release")
        if rel is None:
            releases = None
        else:
            items = rel if isinstance(rel, list) else [rel]
            if not items or not all(isinstance(x, int) and not isinstance(x, bool) for x in items):
                raise DiffConfigError(f"{where}: release must be a number or a list of numbers")
            releases = tuple(items)
        approved.append(
            Approval(
                i,
                reason,
                by,
                releases,
                str(a.get("file") or "*"),
                str(a.get("id") or "*"),
                str(a.get("field") or "*"),
                change,
            )  # fmt: skip
        )
    precision = doc.get("precision", 3)
    if not isinstance(precision, int) or isinstance(precision, bool) or not 0 <= precision <= 9:
        raise DiffConfigError("precision must be a whole number 0..9")
    return Config(
        precision,
        frozenset(str(k) for k in doc.get("ignore") or []),
        list(files),
        thresholds,
        approved,
        path,
        sha256,
    )


def load_config(path: Path = CONFIG_FILE) -> Config:
    if not path.exists():
        raise DiffConfigError(f"release diff config not found: {path}")
    raw = path.read_bytes()
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise DiffConfigError(f"{path}: {e}") from e
    shown = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else path.name
    return parse_config(doc, shown, hashlib.sha256(raw).hexdigest())


# --- flattening --------------------------------------------------------------------------


def _is_num(v: object) -> bool:
    return isinstance(v, int | float) and not isinstance(v, bool) and math.isfinite(v)


def _norm(v: Any, precision: int) -> Any:
    if isinstance(v, float):
        if not math.isfinite(v):
            return str(v)
        r = round(v, precision)
        return int(r) if r.is_integer() else r
    return v


def _scalar(v: Any) -> bool:
    return v is None or isinstance(v, str | int | float | bool)


def _item_key(item: dict[str, Any]) -> str:
    return "/".join(str(item[k]) for k in KEY_FIELDS if k in item and _scalar(item[k]))


def flatten(obj: Any, ignore: frozenset[str], precision: int, prefix: str = "") -> dict[str, Any]:
    """{dotted path: normalised scalar} for one record. Dict keys join with '.', keyed list
    items as `[key]`, plain lists become one sorted JSON value (their order is noise)."""
    out: dict[str, Any] = {}

    def walk(o: Any, p: str) -> None:
        if isinstance(o, dict):
            for k in sorted(o, key=str):
                if str(k) in ignore:
                    continue
                walk(o[k], f"{p}.{k}" if p else str(k))
        elif isinstance(o, list):
            if o and all(isinstance(x, dict) for x in o):
                seen: Counter[str] = Counter()
                for i, x in enumerate(o):
                    key = _item_key(x) or str(i)
                    seen[key] += 1
                    if seen[key] > 1:
                        key = f"{key}#{seen[key]}"
                    walk(x, f"{p}[{key}]")
            elif all(_scalar(x) for x in o):
                vals = sorted((_norm(x, precision) for x in o), key=lambda x: json.dumps(x))
                out[p] = json.dumps(vals, ensure_ascii=False)
            else:
                for i, x in enumerate(o):
                    walk(x, f"{p}[{i}]")
        else:
            out[p] = _norm(o, precision)

    walk(obj, prefix)
    return out


def field_class(path: str) -> str:
    """Path with list keys generalised: `bands.NL[2021].median` -> `bands.NL[*].median`."""
    return re.sub(r"\[[^\]]*\]", "[*]", path)


# --- comparing ---------------------------------------------------------------------------


@dataclass
class Change:
    file: str
    records: str
    id: str
    field: str
    kind: str
    old: Any = None
    new: Any = None
    status: str = "review"
    rule: str = ""
    approval: str = ""
    reason: str = ""

    def delta(self) -> tuple[float | None, float | None]:
        if not (_is_num(self.old) and _is_num(self.new)):
            return None, None
        d = float(self.new) - float(self.old)
        rel = d / abs(float(self.old)) if self.old else (math.inf if d else 0.0)
        return d, rel

    def csv_row(self) -> dict[str, str]:
        d, rel = self.delta()
        return {
            "file": self.file,
            "records": self.records,
            "id": self.id,
            "field": self.field,
            "kind": self.kind,
            "old": "" if self.old is None else str(self.old),
            "new": "" if self.new is None else str(self.new),
            "delta": "" if d is None else f"{d:g}",
            "rel_delta": "" if rel is None or math.isinf(rel) else f"{rel:.4f}",
            "status": self.status,
            "rule": self.rule,
            "approval": self.approval,
            "reason": self.reason,
        }


def _beyond(t: Threshold, old: Any, new: Any) -> bool:
    if t.any:
        return True
    if not (_is_num(old) and _is_num(new)):
        return False  # a rel/abs rule says nothing about text changes: review
    d = abs(float(new) - float(old))
    over_abs = t.abs is None or d > t.abs + 1e-9
    over_rel = t.rel is None or (d > t.rel * abs(float(old)) + 1e-9 if old else d > 0)
    return over_abs and over_rel


def _records(doc: Any, spec: dict[str, Any]) -> dict[str, Any] | None:
    recs = (doc or {}).get(spec["records"]) if isinstance(doc, dict) else None
    if recs is None:
        return None
    if isinstance(recs, dict):
        return {str(k): v for k, v in recs.items()}
    key = spec.get("id")
    out: dict[str, Any] = {}
    for i, r in enumerate(recs):
        rid = str(r.get(key)) if key and isinstance(r, dict) and r.get(key) is not None else str(i)
        out[rid] = r
    return out


def _source_paths(flat: dict[str, Any]) -> dict[str, Any]:
    """parent path -> source value, for every source key in a flattened record."""
    out = {}
    for p, v in flat.items():
        head, _, last = p.rpartition(".")
        if last in SOURCE_KEYS and v not in (None, "", "[]"):
            out[head] = v
    return out


def _has_value_under(flat: dict[str, Any], parent: str) -> bool:
    if not parent:
        return any(_is_num(v) for v in flat.values())
    pre = (parent + ".", parent + "[")
    return any(p.startswith(pre) and _is_num(v) for p, v in flat.items())


def compare_records(
    file: str,
    records: str,
    old: dict[str, Any],
    new: dict[str, Any],
    cfg: Config,
) -> list[Change]:
    out: list[Change] = []
    for rid in sorted(set(old) - set(new)):
        out.append(Change(file, records, rid, "", "removed"))
    for rid in sorted(set(new) - set(old)):
        out.append(Change(file, records, rid, "", "added"))
    for rid in sorted(set(old) & set(new)):
        a = flatten(old[rid], cfg.ignore, cfg.precision)
        b = flatten(new[rid], cfg.ignore, cfg.precision)
        for p in sorted(set(a) | set(b)):
            va, vb = a.get(p), b.get(p)
            if va == vb:
                continue
            kind = "filled" if va is None else "cleared" if vb is None else "changed"
            out.append(Change(file, records, rid, p, kind, va, vb))
        sa, sb = _source_paths(a), _source_paths(b)
        for parent in sorted(set(sa) - set(sb)):
            if _has_value_under(b, parent):
                out.append(Change(file, records, rid, parent or "*", "source_lost", sa[parent]))
        if records == "rows" and isinstance(old[rid], dict) and isinstance(new[rid], dict):
            out += _catalogue_source_lost(file, rid, old[rid], new[rid])
    return out


def _catalogue_source_lost(
    file: str, rid: str, old: dict[str, Any], new: dict[str, Any]
) -> list[Change]:
    """Catalogue rows keep sources in `provenance` (ignored above): a number that is still
    published but whose provenance lost every source id."""
    from ev_pipeline.qa.checks import row_values

    po, pn = old.get("provenance") or {}, new.get("provenance") or {}
    out = []
    for key, value in row_values(new):
        if value is None:
            continue
        had = (po.get(key) or {}).get("source_ids")
        has = (pn.get(key) or {}).get("source_ids")
        if had and not has:
            out.append(Change(file, "rows", rid, key, "source_lost", ",".join(had), value))
    return out


def classify(
    changes: list[Change], cfg: Config, release: int | None, retired: dict[str, Any]
) -> set[int]:
    """Sets status/rule/approval on each change; returns the indexes of approvals used."""
    used: set[int] = set()
    live = [a for a in cfg.approved if a.applies_to(release)]
    for c in changes:
        if c.kind == "added" or c.kind == "filled":
            c.status = "review"
        elif c.kind in BLOCKING_ALWAYS:
            c.status = "blocking"
        elif c.kind == "removed":
            if c.id in retired:  # any variant-keyed file: the id redirects (T-062)
                c.status, c.reason = "retired", f"retired_ids -> {retired[c.id] or '410'}"
            else:
                c.status = "blocking"
        elif c.kind == "charging":
            c.status = "review"
        else:
            t = cfg.threshold(c.file, c.field)
            if t is not None:
                c.rule = t.label()
                if c.kind == "cleared" or _beyond(t, c.old, c.new):
                    c.status = "blocking"
        for a in live:
            if a.matches(c):
                used.add(a.index)
                c.status, c.approval = "approved", a.label()
                c.reason = c.reason or a.reason
                break
    return used


# --- release folders ---------------------------------------------------------------------


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _files(release_dir: Path, pattern: str) -> dict[str, Path]:
    return {
        str(p.relative_to(release_dir)): p for p in sorted(release_dir.glob(pattern)) if p.is_file()
    }


def retired_map(release_dir: Path) -> dict[str, Any]:
    out: dict[str, Any] = {}
    p = release_dir / "retired_ids.json"
    if p.exists():
        out.update(_load(p).get("retired_ids") or {})
    cat = release_dir / "catalogue.json"
    if cat.exists():
        out.update(_load(cat).get("retired_ids") or {})
    return out


@dataclass
class DiffResult:
    previous_release: int | None
    release: int | None
    changes: list[Change] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    stale_approvals: list[dict[str, Any]] = field(default_factory=list)
    config: dict[str, str] = field(default_factory=dict)

    @property
    def blocking(self) -> list[Change]:
        return [c for c in self.changes if c.status == "blocking"]


def _release_no(release_dir: Path) -> int | None:
    return int(release_dir.name) if release_dir.name.isdigit() else None


def diff_releases(
    old_dir: Path,
    new_dir: Path,
    cfg: Config,
    *,
    release: int | None = None,
    cache: dict[str, Any] | None = None,
) -> DiffResult:
    """Compare two release folders. `release`: N (defaults to the new folder's name; a
    temporary build folder passes it). `cache`: already-loaded documents by relative path for
    the new release, so a build doesn't parse its own 7 MB catalogue twice."""
    cache = cache or {}
    res = DiffResult(_release_no(old_dir), release if release is not None else _release_no(new_dir))
    res.config = {"path": cfg.path, "sha256": cfg.sha256}
    seen_files: set[tuple[str, str]] = set()
    for spec in cfg.files:
        old_files, new_files = _files(old_dir, spec["file"]), _files(new_dir, spec["file"])
        for rel in sorted(set(old_files) | set(new_files)):
            if rel not in new_files:
                if (rel, "file") not in seen_files:
                    res.changes.append(Change(rel, "", "", "", "file_removed"))
                    seen_files.add((rel, "file"))
                continue
            if rel not in old_files:
                if (rel, "new") not in seen_files:
                    res.skipped.append({"file": rel, "reason": "new in this release"})
                    seen_files.add((rel, "new"))
                continue
            a = _load(old_files[rel])
            b = cache[rel] if rel in cache else _load(new_files[rel])
            ra, rb = _records(a, spec), _records(b, spec)
            if ra is None and rb is None:
                continue
            if rb is None:
                res.changes.append(Change(rel, spec["records"], "", "", "file_removed"))
                continue
            if ra is None:
                res.skipped.append(
                    {"file": rel, "reason": f"{spec['records']} new in this release"}
                )
                continue
            res.changes += compare_records(rel, spec["records"], ra, rb, cfg)
    res.changes += charging_changes(old_dir, new_dir, cache)
    used = classify(res.changes, cfg, res.release, retired_map(new_dir))
    res.stale_approvals = [
        {"index": a.index, "approved_by": a.approved_by, "reason": a.reason}
        for a in cfg.approved
        if a.applies_to(res.release) and a.index not in used
    ]
    return res


def charging_changes(old_dir: Path, new_dir: Path, cache: dict[str, Any]) -> list[Change]:
    """Decision 040 item 4 through the same report: review only, never blocking."""
    from ev_pipeline.release.charging_stats import charging_review_rows

    po, pn = old_dir / CHARGING_FILE, new_dir / CHARGING_FILE
    if not po.exists() or not (pn.exists() or CHARGING_FILE in cache):
        return []
    cur = cache.get(CHARGING_FILE) or _load(pn)
    out = []
    for r in charging_review_rows(_load(po), cur):
        out.append(
            Change(
                CHARGING_FILE,
                "series",
                str(r.get("record_key") or ""),
                "value",
                "charging",
                _maybe_num(r.get("previous_value")),
                _maybe_num(r.get("value")),
                reason=str(r.get("reason") or ""),
            )  # fmt: skip
        )
    return out


def _maybe_num(v: Any) -> Any:
    if isinstance(v, str) and v:
        try:
            return float(v)
        except ValueError:
            return v
    return v if v != "" else None


# --- outputs -----------------------------------------------------------------------------


def write_csv(res: DiffResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    order = {"blocking": 0, "approved": 1, "retired": 2, "review": 3}
    rows = sorted(res.changes, key=lambda c: (order.get(c.status, 9), c.file, c.id, c.field))
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for c in rows:
            w.writerow(c.csv_row())


def summary(res: DiffResult) -> dict[str, Any]:
    files: dict[str, Counter[str]] = {}
    fields: Counter[str] = Counter()
    status: Counter[str] = Counter()
    for c in res.changes:
        key = f"{c.file}:{c.records}" if c.records else c.file
        files.setdefault(key, Counter())[c.kind] += 1
        status[c.status] += 1
        if c.field and c.kind not in ("added", "removed"):
            fields[f"{c.file}:{field_class(c.field)}"] += 1
    moves = []
    for c in res.changes:
        d, rel = c.delta()
        if rel is not None and c.kind in ("changed", "charging"):
            moves.append((abs(rel), c, d, rel))
    moves.sort(key=lambda m: (-m[0], m[1].file, m[1].id, m[1].field))
    return {
        "previous_release": res.previous_release,
        "release": res.release,
        "config": res.config,
        "status": "fail" if status["blocking"] else "pass",
        "counts": dict(sorted(status.items())),
        "files": {k: dict(sorted(v.items())) for k, v in sorted(files.items())},
        "fields": dict(fields.most_common(20)),
        "biggest_moves": [
            {
                "file": c.file,
                "id": c.id,
                "field": c.field,
                "old": c.old,
                "new": c.new,
                "delta": round(d, 3),
                "rel_delta": None if math.isinf(rel) else round(rel, 4),
                "status": c.status,
            }  # fmt: skip
            for _, c, d, rel in moves[:TOP]
        ],
        "blocking": [
            {k: v for k, v in c.csv_row().items() if v}
            for c in res.changes
            if c.status == "blocking"
        ][:MAX_LISTED],
        "skipped": res.skipped,
        "stale_approvals": res.stale_approvals,
        "csv": f"data/review/{REVIEW_FILE}",
    }


def summary_md(s: dict[str, Any] | None) -> list[str]:
    if not s:
        return []
    c = s.get("counts") or {}
    lines = [
        "",
        f"## Release diff {s.get('previous_release')} -> {s.get('release')} (T-123)",
        "",
        f"Status **{s.get('status')}**: {c.get('blocking', 0)} blocking, "
        f"{c.get('approved', 0)} approved, {c.get('retired', 0)} retired, "
        f"{c.get('review', 0)} review. Full list: `{s.get('csv')}`.",
    ]
    if s.get("files"):
        lines += ["", "| file | " + " | ".join(sorted(KINDS | {"charging"})) + " |"]
        lines.append("|---" * (len(KINDS) + 2) + "|")
        for f, k in s["files"].items():
            lines.append(
                f"| {f} | "
                + " | ".join(str(k.get(x, "")) for x in sorted(KINDS | {"charging"}))
                + " |"
            )
    if s.get("blocking"):
        lines += ["", "Blocking (approve in config/approved_changes.yaml or fix the data):"]
        for b in s["blocking"][:15]:
            what = " ".join(x for x in (b.get("file"), b.get("id"), b.get("field")) if x)
            move = f": {b.get('old', '')} -> {b.get('new', '')}" if "old" in b or "new" in b else ""
            rule = f" [{b['rule']}]" if b.get("rule") else ""
            lines.append(f"- {what} {b.get('kind')}{move}{rule}")
    if s.get("biggest_moves"):
        lines += ["", "Biggest moves:"]
        for m in s["biggest_moves"]:
            rel = "new" if m["rel_delta"] is None else f"{100 * m['rel_delta']:+.1f} %"
            lines.append(f"- {m['file']} {m['id']} {m['field']}: {m['old']} -> {m['new']} ({rel})")
    if s.get("stale_approvals"):
        lines += ["", f"Stale approvals (matched nothing): {len(s['stale_approvals'])}"]
    return lines


def diff_check_args(res: DiffResult | None, note: str = "") -> tuple[str, str, dict[str, Any]]:
    """(status, summary, details) for the `release_diff` QA check."""
    if res is None:
        return "skipped", note or "first release: nothing to compare", {}
    s = summary(res)
    c = s["counts"]
    text = (
        f"vs release {res.previous_release}: {c.get('blocking', 0)} blocking, "
        f"{c.get('approved', 0)} approved, {c.get('review', 0)} review"
    )
    return s["status"], text, s


# --- QA hook -----------------------------------------------------------------------------


def config_path() -> Path:
    import os

    env = os.environ.get("EV_RELEASE_DIFF_CONFIG")
    return Path(env) if env else CONFIG_FILE


def previous_release_dir(data_dir: Path, n: int) -> Path | None:
    releases = data_dir / "releases"
    nums = sorted(
        int(p.name)
        for p in (releases.iterdir() if releases.is_dir() else [])
        if p.is_dir() and p.name.isdigit() and int(p.name) < n
    )
    return releases / str(nums[-1]) if nums else None


def release_diff_check(
    data_dir: Path,
    new_dir: Path,
    release: int,
    cache: dict[str, Any] | None = None,
    write_review: bool = True,
    fetch_new: bool = False,
) -> tuple[Any, DiffResult | None]:
    """The blocking `release_diff` QA check for release N in `new_dir` (fail closed: a bad
    config or an N-1 whose files can't be had fails the check, it never passes silently)."""
    from ev_pipeline.qa.checks import Check
    from ev_pipeline.release.publish import PublishError, ensure_local

    title = "Release diff vs previous release (T-123)"
    prev = previous_release_dir(data_dir, release)
    if prev is None:
        status, text, details = diff_check_args(None)
        return Check("release_diff", title, True, status, text, details), None
    try:
        cfg = load_config(config_path())
        ensure_local(data_dir, int(prev.name))
        if fetch_new:  # a committed release: its asset files may not be on disk yet
            ensure_local(data_dir, release)
        res = diff_releases(prev, new_dir, cfg, release=release, cache=cache)
    except (DiffConfigError, PublishError, OSError, json.JSONDecodeError) as e:
        return Check(
            "release_diff", title, True, "fail", f"cannot diff: {e}", {"error": str(e)}
        ), None
    if write_review:
        write_csv(res, data_dir / "review" / REVIEW_FILE)
    status, text, details = diff_check_args(res)
    return Check("release_diff", title, True, status, text, details), res
