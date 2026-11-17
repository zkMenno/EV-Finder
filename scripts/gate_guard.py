#!/usr/bin/env python3
"""Gate guard (T-121, rule G-06): a change can't edit the checks that judge it.

Stdlib only. Usage in CI (pull_request): python3 scripts/gate_guard.py <base_sha> <head_sha>
Env: PR_BODY, PR_LABELS (comma-separated), GITHUB_STEP_SUMMARY.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config" / "gate-files.yaml"


def load_config(text: str) -> dict:
    """Parse the small YAML subset used by config/gate-files.yaml (scalars and string lists)."""
    cfg: dict = {}
    key = None
    for raw in text.splitlines():
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("- ") else raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") or line.startswith("- "):
            val = line.split("- ", 1)[1].strip()
            cfg.setdefault(key, []).append(_unquote(val))
        elif ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            cfg[key] = _unquote(v) if v else []
    return cfg


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
        return v.encode().decode("unicode_escape") if "\\\\" in v else v.replace("\\\\", "\\")
    return v


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Glob with ** (any depth, including none), * (no slash) and ?."""
    i, out = 0, ""
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile("^" + out + "$")


def matches(path: str, patterns: list[str]) -> bool:
    return any(glob_to_regex(p).match(path) for p in patterns)


@dataclass
class Verdict:
    gate: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)


def has_marker(pr_body: str, marker: str) -> bool:
    """True only for a real line starting with the marker plus a reason; template comments don't count."""
    body = re.sub(r"<!--.*?-->", "", pr_body or "", flags=re.S)
    return any(re.match(re.escape(marker) + r"\s*\S", ln.strip()) for ln in body.splitlines())


def judge(changed: list[str], deleted: list[str], added_test_lines: dict[str, list[str]],
          cfg: dict, pr_body: str, labels: list[str]) -> Verdict:
    v = Verdict()
    for p in changed:
        (v.gate if matches(p, cfg.get("gate_files", [])) else v.other).append(p)
    if v.gate and v.other and cfg.get("escape_label", "gate-ok") not in labels:
        v.problems.append(
            "Split the gate change into its own PR: this PR changes gate files "
            f"({', '.join(v.gate[:5])}) and other files ({len(v.other)})."
        )
    marker = cfg.get("test_change_marker", "Test-change:")
    if not has_marker(pr_body, marker):
        tests = cfg.get("test_files", [])
        gone = [p for p in deleted if matches(p, tests)]
        if gone:
            v.problems.append(f"Test files deleted without a '{marker}' line in the PR body: {', '.join(gone[:5])}")
        pats = [re.compile(x) for x in cfg.get("weakening_patterns", [])]
        for path, lines in added_test_lines.items():
            if not matches(path, tests) or matches(path, cfg.get("guard_self_tests", [])):
                continue
            hits = [ln for ln in lines if any(p.search(ln) for p in pats)]
            if hits:
                v.problems.append(f"{path}: adds skip/only/xfail/sleep without a '{marker}' line: {hits[0].strip()[:80]}")
    return v


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def added_lines(base: str, head: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur = None
    for line in _git("diff", "--unified=0", f"{base}...{head}").splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("+") and not line.startswith("+++") and cur:
            out.setdefault(cur, []).append(line[1:])
    return out


def main(argv: list[str]) -> int:
    cfg = load_config(CONFIG.read_text())
    mode = cfg.get("mode", "observe")
    if mode == "off" or len(argv) < 3:
        print("gate-guard: off or not a pull request; nothing to check")
        return 0
    base, head = argv[1], argv[2]
    changed = [p for p in _git("diff", "--name-only", f"{base}...{head}").splitlines() if p]
    deleted = [p for p in _git("diff", "--name-only", "--diff-filter=D", f"{base}...{head}").splitlines() if p]
    labels = [x.strip() for x in os.environ.get("PR_LABELS", "").split(",") if x.strip()]
    v = judge(changed, deleted, added_lines(base, head), cfg, os.environ.get("PR_BODY", ""), labels)
    lines = [f"### gate-guard ({mode})", f"Gate files changed: {len(v.gate)} · other files: {len(v.other)}"]
    if cfg.get("escape_label", "gate-ok") in labels:
        lines.append("Label `gate-ok` present (WS0 escape hatch): mixed change allowed.")
    lines += [f"- {'would block' if mode == 'observe' else 'BLOCKED'}: {p}" for p in v.problems] or ["- nothing to flag"]
    text = "\n".join(lines)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write(text + "\n")
    if v.problems and mode == "enforce":
        for p in v.problems:
            print(f"::error::{p}")
        return 1
    for p in v.problems:
        print(f"::warning::gate-guard (observe): {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
