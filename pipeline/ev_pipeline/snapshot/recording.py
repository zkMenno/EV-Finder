"""Record what each HTTP response said about itself (URL, status, ETag, Last-Modified).

`ev refresh` wraps every adapter fetch in `recording()`. While it is active, every client made
by `net.safe_client(...)` gets a response hook that appends one entry per response (redirect
hops included) to the recorder. The adapter code does not change: the wrapper swaps
`net.safe_client` for the duration of the fetch and puts it back afterwards.

Adapters that want to be explicit (or that run outside `ev refresh`) can instead call
`record_client(client, recorder)` on the client they built: a one-line change, documented in
pipeline/README.md. Response bodies are never touched here.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx

from ev_pipeline import net

KEPT_HEADERS = ("etag", "last-modified", "content-length", "content-type")


@dataclass
class Recorder:
    source: str
    responses: list[dict[str, Any]] = field(default_factory=list)

    def hook(self, response: httpx.Response) -> None:
        entry: dict[str, Any] = {
            "url": str(response.request.url),
            "method": response.request.method,
            "status": response.status_code,
        }
        for h in KEPT_HEADERS:
            v = response.headers.get(h)
            if v:
                entry[h.replace("-", "_")] = v
        self.responses.append(entry)


def record_client(client: httpx.Client, recorder: Recorder) -> httpx.Client:
    hooks = client.event_hooks
    hooks.setdefault("response", [])
    if recorder.hook not in hooks["response"]:
        hooks["response"].append(recorder.hook)
    client.event_hooks = hooks
    return client


@contextlib.contextmanager
def recording(source: str) -> Iterator[Recorder]:
    """Record responses of every `net.safe_client` built inside the block."""
    recorder = Recorder(source)
    original = net.safe_client

    def wrapped(*args: Any, **kwargs: Any) -> httpx.Client:
        return record_client(original(*args, **kwargs), recorder)

    net.safe_client = wrapped  # type: ignore[assignment]
    try:
        yield recorder
    finally:
        net.safe_client = original  # type: ignore[assignment]


def validators(responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The final (non-redirect) GET responses that carry an ETag or Last-Modified."""
    out = []
    for r in responses:
        if r.get("method", "GET") != "GET" or not 200 <= int(r.get("status", 0)) < 300:
            continue
        if r.get("etag") or r.get("last_modified"):
            out.append(r)
    return out
