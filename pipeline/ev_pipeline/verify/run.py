"""T-127: `ev verify`: before a commit that changes data, prove the release still matches its
inputs and the numbers still make sense on real rows.

Steps (each one a section in verify-report.md):
1. rebuild: the next release from the recorded staging in a scratch copy of data/ (no
   network; data/releases/<latest> is the N-1 it is compared with). Its QA runs as in a real
   build, including the T-123 release diff.
2. tests: `pytest -q` for the pipeline (skip with --skip-tests).
3. release diff: the scratch release against latest (counts, blocking list, biggest moves).
4. back-tests: every back-test section in the scratch qa.json with its median error and gate.
5. changed rules: rule/parameter files changed against the base ref; their effect on the
   latest rows is the release diff in step 3 (the dry run).
6. spot checks: the tricky cars (tricky_cars.yaml) with old -> new headline numbers.
7. claims: every `key: number` line in the PR body (--pr-body) whose key is one of the
   report's numbers must equal the report (A-20 B1: MORNING.md quoted a number the release
   didn't have).
8. seed check (G-48, T-153): a seed variant built with another drivetrain than its seed, or
   with a WLTP more than 10 % off its own cited WLTP: listed; a mismatch the previous
   release did not have fails the run.
G-49 (T-153): while `ev refresh` holds data/staging (refresh/lock.py) verify refuses to run.
Plus the memory peak. Exit 0 = pass, 1 = fail. Back-test flags are reported, not failures
(they don't block a release either).
"""

from __future__ import annotations

import fnmatch
import json
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ev_pipeline.release.build import REPO_ROOT

TRICKY_FILE = Path(__file__).with_name("tricky_cars.yaml")
SPOT_FIELDS = (
    "battery_kwh_net", "wltp_range_km", "real_range_km", "epa_range_km",
    "consumption_kwh_100km", "dc_km_per_20min",
)  # fmt: skip
RULE_GLOBS = (
    "pipeline/ev_pipeline/derive/*", "pipeline/ev_pipeline/match/*", "pipeline/ev_pipeline/merge/*",
    "*_params.yaml", "*_rules.yaml", "data/editorial/*", "data/taxonomy/*", "data/seed/*",
    "config/approved_changes.yaml",
)  # fmt: skip
BACKTEST_KEYS = ("backtest", "backtest_epa", "backtest_used_prices")
SKIP_COPY = {"releases", "raw", "runs", "review", "local", "staging"}
CLAIM = re.compile(r"^[\s>*-]*`?([a-z][a-z0-9_]*)`?\s*[:=]\s*(-?\d+(?:\.\d+)?)\b", re.M)


@dataclass
class Report:
    status: str = "pass"
    sections: dict[str, dict[str, Any]] = field(default_factory=dict)
    numbers: dict[str, float | int] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    release_diff_csv: str | None = None  # the scratch build's data/review/release_diff.csv

    def fail(self, why: str) -> None:
        self.status = "fail"
        self.failures.append(why)


# --- steps -------------------------------------------------------------------------------


def latest_number(data_dir: Path) -> int | None:
    p = data_dir / "releases" / "latest"
    if not p.exists():
        return None
    t = p.read_text(encoding="utf-8").strip()
    return int(t) if t.isdigit() else None


def scratch_copy(data_dir: Path, dest: Path, latest: int | None) -> Path:
    """A copy of data/ that a build may write into: inputs copied, staging linked (read
    only by the build), and only the latest release (the N-1)."""
    d = dest / "data"
    d.mkdir(parents=True)
    for p in data_dir.iterdir():
        if p.name in SKIP_COPY:
            continue
        if p.is_dir():
            shutil.copytree(p, d / p.name)
        else:
            shutil.copy2(p, d / p.name)
    if (data_dir / "staging").is_dir():
        (d / "staging").symlink_to((data_dir / "staging").resolve(), target_is_directory=True)
    rel = d / "releases"
    rel.mkdir()
    pub = data_dir / "releases" / "publish.yaml"
    if pub.exists():
        shutil.copy2(pub, rel / "publish.yaml")
    if latest is not None:
        from ev_pipeline.release.publish import ensure_local

        ensure_local(data_dir, latest)  # T-064: asset files fetched by sha256 if missing
        shutil.copytree(data_dir / "releases" / str(latest), rel / str(latest))
        (rel / "latest").write_text(f"{latest}\n", encoding="utf-8")
    return d


def rebuild(data_dir: Path, scratch: Path, now: datetime) -> dict[str, Any]:
    from ev_pipeline.release.build import build_release, write_release
    from ev_pipeline.release.validate import ReleaseError

    if not any((data_dir / "staging").glob("*.jsonl")):
        return {
            "status": "fail",
            "error": "no recorded staging in data/staging: run `uv run ev refresh --no-release` "
            "(network) once, then verify again",
        }
    res = None
    try:
        res = build_release(scratch, now=now)
        out = write_release(res, scratch)
    except ReleaseError as e:
        qa = scratch / "review" / "qa.json"
        return {  # a QA block still has a built catalogue: spot checks need it most then
            "status": "fail",
            "error": str(e).splitlines()[0],
            "release": res.release if res else None,
            "qa": json.loads(qa.read_text(encoding="utf-8")) if qa.exists() else None,
            "catalogue": res.catalogue if res else None,
        }
    qa = json.loads((out / "qa.json").read_text(encoding="utf-8"))
    cat = json.loads((out / "catalogue.json").read_text(encoding="utf-8"))
    return {"status": "pass", "release": res.release, "dir": str(out), "qa": qa, "catalogue": cat}


def run_tests(pipeline_dir: Path) -> dict[str, Any]:
    cp = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=pipeline_dir, capture_output=True, text=True, check=False,
    )  # fmt: skip
    tail = [x for x in cp.stdout.splitlines() if x.strip()][-1:] or [cp.stderr.strip()[-200:]]
    m = re.search(r"(\d+) passed", tail[0])
    f = re.search(r"(\d+) failed", tail[0])
    return {
        "status": "pass" if cp.returncode == 0 else "fail",
        "summary": tail[0],
        "passed": int(m.group(1)) if m else 0,
        "failed": int(f.group(1)) if f else 0,
    }


def backtests(qa: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Every back-test in qa.json; sections made of parts (EPA: range, consumption,
    consumption_oos) are listed per part as `name.part`."""
    out = []

    def add(name: str, b: dict[str, Any]) -> None:
        med = {k: v for k, v in b.items() if "median" in k and isinstance(v, int | float)}
        out.append(
            {"name": name, "status": b.get("status"), "gate": b.get("gate"), "medians": med,
             "n": b.get("n"), "note": b.get("note")}
        )  # fmt: skip

    for key in BACKTEST_KEYS:
        b = (qa or {}).get(key)
        if not isinstance(b, dict):
            continue
        parts = {k: v for k, v in b.items() if isinstance(v, dict) and "status" in v}
        if "status" in b or not parts:
            add(key, b)
        for part, v in sorted(parts.items()):
            add(f"{key}.{part}", v)
    return out


def changed_rules(repo: Path, base: str) -> list[str] | None:
    cp = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", f"{base}...HEAD"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    if cp.returncode != 0:
        return None
    names = [n for n in cp.stdout.splitlines() if n]
    return [n for n in names if any(fnmatch.fnmatchcase(n, g) for g in RULE_GLOBS)]


def load_tricky(path: Path = TRICKY_FILE) -> list[dict[str, str]]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if doc.get("schema") != "tricky-cars/v1":
        raise ValueError(f"{path}: schema must be tricky-cars/v1")
    return [{"id": str(c["id"]), "why": str(c.get("why") or "")} for c in doc.get("cars") or []]


def spot_checks(
    new: dict[str, Any] | None, old: dict[str, Any] | None, tricky: list[dict[str, str]]
) -> list[dict[str, Any]]:
    nr = {r["variant_id"]: r for r in (new or {}).get("rows") or []}
    orows = {r["variant_id"]: r for r in (old or {}).get("rows") or []}
    out = []
    for car in tricky:
        ids = sorted(i for i in set(nr) | set(orows) if fnmatch.fnmatchcase(i, car["id"]))
        if not ids:
            out.append({"pattern": car["id"], "variant_id": None, "why": car["why"]})
        for vid in ids:
            a, b = orows.get(vid) or {}, nr.get(vid) or {}
            values = {f: (a.get(f), b.get(f)) for f in SPOT_FIELDS}
            notes = []
            if vid not in nr:
                notes.append("gone")
            elif vid not in orows:
                notes.append("new")
            w, rr = b.get("wltp_range_km"), b.get("real_range_km")
            if isinstance(w, int | float) and isinstance(rr, int | float) and rr > w * 1.1:
                notes.append("real range > WLTP x 1.1")
            if vid in nr and b.get("battery_kwh_net") is None:
                notes.append("no battery")
            changed = [f for f, (x, y) in values.items() if x != y and vid in nr and vid in orows]
            out.append(
                {"pattern": car["id"], "variant_id": vid, "values": values,
                 "changed": changed, "notes": notes}
            )  # fmt: skip
    return out


SEED_WLTP_REL = 0.10  # G-48: built WLTP more than 10 % off the variant's own cited WLTP


def seed_mismatches(new: dict[str, Any] | None, seed_doc: dict[str, Any] | None) -> list[str]:
    """Messages of `seed_mismatch_items` (see there)."""
    return [m for _, m in seed_mismatch_items(new, seed_doc)]


def seed_mismatch_items(
    new: dict[str, Any] | None, seed_doc: dict[str, Any] | None
) -> list[tuple[tuple[str, str], str]]:
    """G-48 (T-153): seed variants whose built row (or year band `<id>-<yyyy>`) disagrees
    with the seed: another drivetrain than the seed's, or a WLTP more than SEED_WLTP_REL off
    the seed's own cited WLTP (a reviewer caught Kia EV3 built as AWD / 583 km twice).
    Each item is ((row id, "drivetrain" | "wltp"), message): the key stays the same when a
    built value drifts with fresh data."""
    rows = (new or {}).get("rows") or []
    out: list[tuple[tuple[str, str], str]] = []
    for v in (seed_doc or {}).get("variants") or []:
        vid = str(v.get("id") or "")
        band = re.compile(rf"^{re.escape(vid)}(-\d{{4}})?$")
        cited = ((v.get("cited") or {}).get("wltp_range_km") or {}).get("value")
        for r in rows:
            rid = str(r.get("variant_id") or "")
            if not band.match(rid):
                continue
            dt, sdt = r.get("drivetrain"), v.get("drivetrain")
            if dt and sdt and dt != sdt:
                out.append(((rid, "drivetrain"), f"{rid}: drivetrain {dt}, seed says {sdt}"))
            w = r.get("wltp_range_km")
            if (
                isinstance(cited, int | float)
                and isinstance(w, int | float)
                and abs(w - cited) > SEED_WLTP_REL * cited
            ):
                msg = f"{rid}: WLTP {w:g} km, its cited WLTP is {cited:g} km (> 10 % off)"
                out.append(((rid, "wltp"), msg))
    return out


def check_claims(body: str, numbers: dict[str, float | int]) -> list[str]:
    """`key: number` lines in a PR body whose key is a report number must match it."""
    bad = []
    for key, val in CLAIM.findall(body):
        if key in numbers and abs(float(val) - float(numbers[key])) > 1e-9:
            bad.append(f"{key}: PR body says {val}, report says {numbers[key]}")
    return bad


def peak_mb() -> float:
    self_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    child_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return round(max(self_kb, child_kb) / 1024, 1)


# --- the whole run -----------------------------------------------------------------------


def verify(
    data_dir: Path,
    *,
    repo: Path = REPO_ROOT,
    base: str = "origin/main",
    skip_tests: bool = False,
    pr_body: str | None = None,
    tricky: list[dict[str, str]] | None = None,
    now: datetime | None = None,
) -> Report:
    rep = Report()
    now = now or datetime.now(UTC)
    from ev_pipeline.refresh.lock import refusal

    busy = refusal(data_dir)
    if busy is not None:  # G-49: never rebuild from a staging that refresh is still writing
        rep.sections["rebuild"] = {"status": "refused", "error": busy}
        rep.fail(busy)
        return rep
    latest = latest_number(data_dir)
    old_cat = None
    if latest is not None:
        from ev_pipeline.release.publish import local_catalogue

        p = local_catalogue(data_dir, latest)
        old_cat = json.loads(p.read_text(encoding="utf-8")) if p else None
    with tempfile.TemporaryDirectory(prefix="ev-verify-") as tmp:
        scratch = scratch_copy(data_dir, Path(tmp), latest)
        built = rebuild(data_dir, scratch, now)
        csv_path = scratch / "review" / "release_diff.csv"
        if csv_path.exists():
            rep.release_diff_csv = csv_path.read_text(encoding="utf-8")
    late = refusal(data_dir)
    if late is not None:  # G-49: a refresh started while we rebuilt; the rebuild may be mixed
        rep.fail(f"a refresh started during the rebuild: {late}")
    qa = built.get("qa")
    rep.sections["rebuild"] = {
        k: v for k, v in built.items() if k in ("status", "error", "release")
    } | {"previous_release": latest}
    if built["status"] != "pass":
        rep.fail(f"rebuild: {built.get('error')}")
    if skip_tests:
        rep.sections["tests"] = {"status": "skipped", "summary": "--skip-tests"}
    else:
        t = run_tests(repo / "pipeline")
        rep.sections["tests"] = t
        rep.numbers["tests_passed"] = t["passed"]
        if t["status"] != "pass":
            rep.fail(f"tests: {t['summary']}")
    rd = (qa or {}).get("release_diff") or {}
    rep.sections["release_diff"] = rd
    if rd.get("counts") is not None:
        for k in ("blocking", "approved", "retired", "review"):
            rep.numbers[f"release_diff_{k}"] = int(rd["counts"].get(k, 0))
        if rd.get("status") == "fail":
            rep.fail(f"release diff: {rd['counts'].get('blocking', 0)} blocking change(s)")
    cat = built.get("catalogue")
    if cat is not None:
        rep.numbers["variants"] = len(cat.get("rows") or [])
    if old_cat is not None:
        rep.numbers["variants_previous"] = len(old_cat.get("rows") or [])
    bts = backtests(qa)
    rep.sections["backtests"] = {"items": bts}
    for b in bts:
        for k, v in b["medians"].items():
            rep.numbers[f"{b['name'].replace('.', '_')}_{k}"] = v
    rules = changed_rules(repo, base)
    rep.sections["changed_rules"] = {"files": rules, "base": base}
    rep.sections["spot_checks"] = {"rows": spot_checks(cat, old_cat, tricky or load_tricky())}
    seed_file = data_dir / "seed" / "variants.yaml"
    if cat is not None and seed_file.exists():
        seed_doc = yaml.safe_load(seed_file.read_text(encoding="utf-8"))
        items = seed_mismatch_items(cat, seed_doc)
        bad = [m for _, m in items]
        # Already in the previous release (same row and kind, whatever the value now): listed,
        # not a failure of this change (the owner lane fixes the seed); a mismatch the
        # previous release did not have fails the run. Baseline = release N-1, not main.
        before = {k for k, _ in seed_mismatch_items(old_cat, seed_doc)} if old_cat else set()
        new = [m for k, m in items if k not in before]
        rep.sections["seed_check"] = {
            "status": "fail" if new else "pass", "mismatches": new,
            "pre_existing": [m for k, m in items if k in before], "baseline": latest,
        }  # fmt: skip
        rep.numbers["seed_mismatches"] = len(bad)
        rep.numbers["seed_mismatches_new"] = len(new)
        for b in new:
            rep.fail(f"seed check (G-48): {b}")
    if pr_body is not None:
        bad = check_claims(pr_body, rep.numbers)
        rep.sections["claims"] = {"status": "fail" if bad else "pass", "mismatches": bad}
        for b in bad:
            rep.fail(f"claim: {b}")
    rep.numbers["memory_peak_mb"] = peak_mb()
    return rep


# --- report ------------------------------------------------------------------------------


def _fmt(v: Any) -> str:
    return "-" if v is None else f"{v:g}" if isinstance(v, float) else str(v)


def report_md(rep: Report) -> str:
    s = rep.sections
    out = [f"# verify-pipeline report: **{rep.status}**", ""]
    out += [f"- {f}" for f in rep.failures] + ([""] if rep.failures else [])
    rb = s.get("rebuild", {})
    out += [
        "## Rebuild from recorded staging",
        f"{rb.get('status')}: release {rb.get('release', '-')} against {rb.get('previous_release')}"
        + (f" ({rb['error']})" if rb.get("error") else ""),
        "",
        "## Tests",
        f"{s.get('tests', {}).get('status')}: {s.get('tests', {}).get('summary')}",
    ]
    from ev_pipeline.release.differ import summary_md

    rd = s.get("release_diff") or {}
    out += summary_md(rd) if rd.get("counts") is not None else ["", "## Release diff", "not run"]
    out += ["", "## Back-tests (report only)", ""]
    items = s.get("backtests", {}).get("items") or []
    if items:
        out += ["| back-test | status | n | medians | gate |", "|---|---|---|---|---|"]
        for b in items:
            med = ", ".join(f"{k} {_fmt(v)}" for k, v in b["medians"].items()) or "-"
            out.append(
                f"| {b['name']} | {b['status']} | {_fmt(b.get('n'))} | {med} | "
                f"{b.get('gate') or '-'} |"
            )
    else:
        out.append("none in qa.json")
    cr = s.get("changed_rules", {})
    out += ["", f"## Changed rules vs {cr.get('base')}", ""]
    files = cr.get("files")
    if files is None:
        out.append("git diff unavailable")
    elif not files:
        out.append("none")
    else:
        out += [f"- `{f}`" for f in files]
        out.append("Dry run: their effect on the latest rows is the release diff above.")
    out += ["", "## Spot checks (tricky cars: old -> new)", ""]
    out.append("| variant | " + " | ".join(SPOT_FIELDS) + " | notes |")
    out.append("|---" * (len(SPOT_FIELDS) + 2) + "|")
    for r in s.get("spot_checks", {}).get("rows") or []:
        if r["variant_id"] is None:
            out.append(f"| `{r['pattern']}`: no rows |" + " |" * (len(SPOT_FIELDS) + 1))
            continue
        cells = []
        for f in SPOT_FIELDS:
            a, b = r["values"][f]
            cells.append(_fmt(b) if a == b else f"**{_fmt(a)} -> {_fmt(b)}**")
        out.append(f"| {r['variant_id']} | " + " | ".join(cells) + f" | {', '.join(r['notes'])} |")
    if "seed_check" in s:
        out += ["", "## Seed vs built (G-48: drivetrain, WLTP vs cited)", ""]
        sc = s["seed_check"]
        out += [f"- **new:** {m}" for m in sc["mismatches"]]
        out += [
            f"- already in release {sc.get('baseline')}: {m}" for m in sc.get("pre_existing") or []
        ]
        if not sc["mismatches"] and not sc.get("pre_existing"):
            out.append("all match")
    if "claims" in s:
        out += ["", "## PR body claims", ""]
        out += [f"- {m}" for m in s["claims"]["mismatches"]] or ["all match"]
    out += ["", "## Numbers (paste into the PR body; `ev verify --pr-body` checks them)", "", "```"]
    out += [f"{k}: {_fmt(v)}" for k, v in sorted(rep.numbers.items())]
    out += ["```", "", "Commit stamp: `Verified: verify-pipeline`", ""]
    return "\n".join(out)
