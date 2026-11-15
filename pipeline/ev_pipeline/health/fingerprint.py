"""Schema fingerprint of a raw folder (addendum 6 P3): column names and types per file group.

What it reads (streamed or bounded, never a whole registry in memory):
- **CSV**: the header row and the first 200 data rows (delimiter sniffed, `;` or `,`).
- **XLSX**: sheet names and the label cells of the first 15 rows of each sheet (ALL-CAPS
  cells such as makes and models are data, not labels, and are left out).
- **JSON / JSONL**: every key path (`.a.b[].c`) with the value types seen and how often.
  Dicts with more than 50 keys are treated as maps (`{*}`), so data keys don't count as
  columns. Files over 64 MB are listed but not parsed.

Files are grouped by a **pattern**: digits become `#` (`page-001.json` → `page-#.json`,
`fz10_2026_10.xlsx` → `fz10_#_#.xlsx`) and folders with many files collapse to
`dir/*.json` (or `top/**/*.json` for deep trees like the OpenEV clone). Column names get the
same digit rule (`2026 Q2` → `# Q#`) and German/English month names become `<month>`, so a new
quarter or month is not drift.

`compare(old, new)` says what changed. **Breaking** (fails closed for that source): a file
group disappeared, or a column / key path that was common before (seen 20+ times) is gone.
**Additive** (reported only): new groups, new columns, value types that changed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from ev_pipeline.snapshot.store import iter_tree

CSV_SAMPLE_ROWS = 200
XLSX_HEADER_ROWS = 15
JSON_MAX_BYTES = 64 * 1024 * 1024
MAP_KEYS = 50
MAX_DEPTH = 8
COLLAPSE_FILES = 20
MIN_KEEP = 3
"""Key paths seen fewer times than this are not stored (rare optional fields)."""
MIN_COMMON = 20
"""Only key paths seen at least this often count as removed when they disappear."""

DIGITS = re.compile(r"\d+")
MONTHS = re.compile(
    r"\b(januar|februar|märz|maerz|april|mai|juni|juli|august|september|oktober|november|"
    r"dezember|january|february|march|may|june|july|october|december)\b",
    re.IGNORECASE,
)
SPACE = re.compile(r"\s+")


def norm_name(text: str) -> str:
    text = MONTHS.sub("<month>", str(text))
    text = DIGITS.sub("#", text)
    return SPACE.sub(" ", text).strip()


# --- per file type ----------------------------------------------------------------------


def _value_type(v: str) -> str:
    s = v.strip()
    if not s:
        return ""
    try:
        float(s.replace(",", "."))
    except ValueError:
        return "str"
    return "num"


def csv_columns(path: Path) -> dict[str, list[Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        head = fh.read(8192)
        fh.seek(0)
        try:
            dialect: Any = csv.Sniffer().sniff(head, delimiters=";,\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(fh, dialect)
        header = next(reader, [])
        names = [norm_name(h) for h in header]
        types: dict[str, set[str]] = {n: set() for n in names}
        for i, row in enumerate(reader):
            if i >= CSV_SAMPLE_ROWS:
                break
            for name, value in zip(names, row, strict=False):
                t = _value_type(value)
                if t:
                    types[name].add(t)
    return {n: ["|".join(sorted(t)), MIN_COMMON] for n, t in types.items() if n}


def _header_cell(v: object) -> bool:
    """Text that looks like a label, not data: ALL-CAPS cells (makes, models) and short
    codes are data rows that happen to sit in the first rows."""
    if not isinstance(v, str):
        return False
    s = v.strip()
    letters = [ch for ch in s if ch.isalpha()]
    return len(letters) >= 3 and not s.isupper()


def xlsx_columns(path: Path) -> dict[str, list[Any]]:
    import openpyxl

    out: dict[str, list[Any]] = {}
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for ws in wb.worksheets:
            sheet = norm_name(ws.title)
            out[f"{sheet}!"] = ["sheet", MIN_COMMON]
            for row in ws.iter_rows(max_row=XLSX_HEADER_ROWS, values_only=True):
                for v in row:
                    if _header_cell(v):
                        out[f"{sheet}!{norm_name(v)}"] = ["str", MIN_COMMON]
    finally:
        wb.close()
    return out


def _json_type(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int | float):
        return "num"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "arr"
    return "obj"


def _walk(v: Any, path: str, acc: dict[str, list[Any]], depth: int) -> None:
    t = _json_type(v)
    slot = acc.setdefault(path or "$", [set(), 0])
    slot[0].add(t)
    slot[1] += 1
    if depth >= MAX_DEPTH:
        return
    if isinstance(v, dict):
        if len(v) > MAP_KEYS:
            for child in v.values():
                _walk(child, f"{path}{{*}}", acc, depth + 1)
        else:
            for k, child in v.items():
                _walk(child, f"{path}.{norm_name(k)}", acc, depth + 1)
    elif isinstance(v, list):
        for child in v:
            _walk(child, f"{path}[]", acc, depth + 1)


def json_columns(path: Path, acc: dict[str, list[Any]] | None = None) -> dict[str, list[Any]]:
    acc = {} if acc is None else acc
    if path.stat().st_size > JSON_MAX_BYTES:
        acc.setdefault("(not parsed: over 64 MB)", [{"skipped"}, MIN_COMMON])
        return acc
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.strip():
                    try:
                        _walk(json.loads(line), "", acc, 0)
                    except json.JSONDecodeError:
                        acc.setdefault("(invalid json line)", [{"error"}, 0])[1] += 1
        return acc
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        acc.setdefault("(invalid json)", [{"error"}, 0])[1] += 1
        return acc
    _walk(data, "", acc, 0)
    return acc


# --- grouping ---------------------------------------------------------------------------

KINDS = {".csv": "csv", ".xlsx": "xlsx", ".json": "json", ".jsonl": "json"}


IGNORED_FILES = {"package.json", "package-lock.json"}


def _counts(rel: str) -> bool:
    """Tooling files in cloned repos (dot folders, npm manifests) are not data."""
    parts = rel.split("/")
    return not any(p.startswith(".") for p in parts) and parts[-1] not in IGNORED_FILES


def group_keys(rel_paths: list[str]) -> dict[str, str]:
    """rel path -> group key (pattern), collapsing folders with many files."""
    pattern = {p: norm_name(p) for p in rel_paths}
    by_parent: dict[tuple[str, str], set[str]] = defaultdict(set)
    for p, pat in pattern.items():
        parent = pat.rsplit("/", 1)[0] if "/" in pat else ""
        by_parent[(parent, Path(p).suffix)].add(pat)
    key = {}
    for p, pat in pattern.items():
        parent = pat.rsplit("/", 1)[0] if "/" in pat else ""
        suffix = Path(p).suffix
        if len(by_parent[(parent, suffix)]) > COLLAPSE_FILES:
            key[p] = f"{parent}/*{suffix}" if parent else f"*{suffix}"
        else:
            key[p] = pat
    by_top: dict[tuple[str, str], set[str]] = defaultdict(set)
    for p, k in key.items():
        if "/" in k:
            by_top[(k.split("/", 1)[0], Path(p).suffix)].add(k)
    for p, k in key.items():
        if "/" in k:
            top, suffix = k.split("/", 1)[0], Path(p).suffix
            if len(by_top[(top, suffix)]) > COLLAPSE_FILES:
                key[p] = f"{top}/**/*{suffix}"
    return key


def fingerprint_tree(root: Path) -> dict[str, Any]:
    files = [
        p
        for p in iter_tree(root)
        if p.suffix.lower() in KINDS and _counts(p.relative_to(root).as_posix())
    ]
    rels = [p.relative_to(root).as_posix() for p in files]
    keys = group_keys(rels)
    raw: dict[str, dict[str, list[Any]]] = {}
    counts: dict[str, int] = defaultdict(int)
    for path, rel in zip(files, rels, strict=True):
        g = keys[rel]
        counts[g] += 1
        kind = KINDS[path.suffix.lower()]
        acc = raw.setdefault(g, {})
        try:
            if kind == "json":
                json_columns(path, acc)
                continue
            cols = csv_columns(path) if kind == "csv" else xlsx_columns(path)
        except Exception as exc:  # a broken file is itself a fingerprint signal
            cols = {f"(unreadable: {type(exc).__name__})": ["error", MIN_COMMON]}
        for name, (types, n) in cols.items():
            slot = acc.setdefault(name, [set(), 0])
            slot[0].update(t for t in str(types).split("|") if t)
            slot[1] += n
    groups: dict[str, Any] = {}
    for g in sorted(raw):
        cols = {}
        for name in sorted(raw[g]):
            types, n = raw[g][name]
            if n < MIN_KEEP:
                continue
            cols[name] = {"types": "|".join(sorted(t for t in types if t != "null")), "n": n}
        groups[g] = {"files": counts[g], "columns": cols}
    return {"hash": fingerprint_hash(groups), "groups": groups}


def fingerprint_hash(groups: dict[str, Any]) -> str:
    h = hashlib.sha256()
    for g in sorted(groups):
        h.update(f"{g}\n".encode())
        for name in sorted(groups[g]["columns"]):
            h.update(f"  {name}\n".encode())
    return "fp:" + h.hexdigest()[:16]


def compare(old: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """Differences between two fingerprints; `breaking` lists what fails closed."""
    if not old or not old.get("groups"):
        return {"same": False, "first": True, "breaking": [], "additive": []}
    if old.get("hash") == new.get("hash"):
        return {"same": True, "first": False, "breaking": [], "additive": []}
    breaking: list[str] = []
    additive: list[str] = []
    og, ng = old["groups"], new.get("groups") or {}
    for g in sorted(set(og) - set(ng)):
        breaking.append(f"file group gone: {g}")
    for g in sorted(set(ng) - set(og)):
        additive.append(f"new file group: {g}")
    for g in sorted(set(og) & set(ng)):
        oc, nc = og[g]["columns"], ng[g]["columns"]
        for name in sorted(set(oc) - set(nc)):
            if int(oc[name].get("n", 0)) >= MIN_COMMON:
                breaking.append(f"{g}: column gone: {name}")
        for name in sorted(set(nc) - set(oc)):
            additive.append(f"{g}: new column: {name}")
        for name in sorted(set(oc) & set(nc)):
            a, b = (
                set(filter(None, oc[name]["types"].split("|"))),
                set(filter(None, nc[name]["types"].split("|"))),
            )
            if a and b and not (a & b):
                additive.append(f"{g}: {name} type {'|'.join(sorted(a))} -> {'|'.join(sorted(b))}")
    return {"same": False, "first": False, "breaking": breaking, "additive": additive}


def summary(fp: dict[str, Any]) -> dict[str, Any]:
    """Short form for tables: hash, groups, columns."""
    groups = fp.get("groups") or {}
    return {
        "hash": fp.get("hash"),
        "groups": len(groups),
        "columns": sum(len(g["columns"]) for g in groups.values()),
    }
