"""Cheap "has it changed?" checks before a full download (addendum 6 P1: skip unchanged).

- **Git sources** (adapter has `REPO_URL`, previous fetch recorded a `commit`):
  `git ls-remote <repo> HEAD` and compare the commit.
- **HTTP sources**: if every data response of the previous snapshot carried an ETag or
  Last-Modified, send a conditional `HEAD` for each (If-None-Match / If-Modified-Since,
  through `net.safe_client`). All `304`, or the same validator back: unchanged.

Anything else (no validators, too many URLs, an error, HEAD refused) is `unknown`, and the
source is downloaded and compared by content hash instead. A probe never writes anything.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from ev_pipeline import net

MAX_PROBES = 25
GIT_TIMEOUT_S = 60

GitRunner = Callable[[list[str]], str]


@dataclass
class ProbeResult:
    status: str  # unchanged | changed | unknown
    detail: str


def _git_runner(cmd: list[str]) -> str:
    out = subprocess.run(
        cmd, capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=True, env=net.git_env()
    )
    return out.stdout


def probe_git(
    repo_url: str, commit: str, run: GitRunner | None = None, source_id: str | None = None
) -> ProbeResult:
    """`source_id` given: the URL must pass `net.check_git_url` first (A-05 L6, fail closed)."""
    cmd = ["git", "ls-remote", repo_url, "HEAD"]
    if source_id is not None:
        try:
            cmd = net.git_ls_remote_cmd(source_id, repo_url)
        except (net.FetchBlocked, ValueError) as exc:
            return ProbeResult("unknown", f"git URL refused: {exc}")
    try:
        out = (run or _git_runner)(cmd)
    except (subprocess.SubprocessError, OSError) as exc:
        return ProbeResult("unknown", f"git ls-remote failed: {type(exc).__name__}")
    head = out.split()[0] if out.split() else ""
    if not head:
        return ProbeResult("unknown", "git ls-remote returned nothing")
    if head == commit:
        return ProbeResult("unchanged", f"HEAD still {commit[:12]}")
    return ProbeResult("changed", f"HEAD moved {commit[:12]} -> {head[:12]}")


def data_responses(responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        r
        for r in responses
        if r.get("method", "GET") == "GET" and 200 <= int(r.get("status", 0)) < 300
    ]


def probe_http(
    responses: list[dict[str, Any]], client_factory: Callable[[], httpx.Client]
) -> ProbeResult:
    data = data_responses(responses)
    if not data:
        return ProbeResult("unknown", "no recorded responses")
    if len(data) > MAX_PROBES:
        return ProbeResult("unknown", f"{len(data)} URLs (probe limit {MAX_PROBES})")
    if any(not (r.get("etag") or r.get("last_modified")) for r in data):
        return ProbeResult("unknown", "some responses had no ETag/Last-Modified")
    try:
        client = client_factory()
    except (ValueError, OSError) as exc:
        return ProbeResult("unknown", f"no client: {exc}")
    try:
        for r in data:
            headers = {}
            if r.get("etag"):
                headers["If-None-Match"] = r["etag"]
            if r.get("last_modified"):
                headers["If-Modified-Since"] = r["last_modified"]
            resp = client.head(r["url"], headers=headers)
            if resp.status_code == 304:
                continue
            if resp.status_code >= 400:
                return ProbeResult("unknown", f"HEAD refused ({resp.status_code})")
            same_etag = r.get("etag") and resp.headers.get("etag") == r["etag"]
            same_lm = (
                not r.get("etag")
                and r.get("last_modified")
                and resp.headers.get("last-modified") == r["last_modified"]
            )
            if not (same_etag or same_lm):
                return ProbeResult("changed", f"validator changed ({resp.status_code})")
    except httpx.HTTPError as exc:
        return ProbeResult("unknown", f"probe failed: {type(exc).__name__}")
    finally:
        client.close()
    return ProbeResult("unchanged", f"{len(data)} URL(s) not modified")
