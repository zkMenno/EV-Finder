"""Safe outbound HTTP for the source adapters (A-02 security pass, addendum 5 item 6).

Every adapter that fetches over HTTP builds its client with `safe_client(source_id)`. The
client enforces, on the first request and on every redirect hop:

- **Host allowlist.** Only `https` URLs on the default port whose host is listed under
  `hosts:` for that source in `data/sources.yaml`. `*.example.org` matches subdomains only.
  IP literals and URLs with user info are refused.
- **SSRF guard.** The host is resolved once, every resolved address must be public
  (no private, loopback, link-local, CGNAT, multicast, reserved or unspecified ranges,
  IPv4-mapped IPv6 included), and the socket connects to the checked address itself, so a
  DNS answer can't change between the check and the connect (no rebinding window).
  TLS still verifies the certificate against the hostname.
- **Limits.** Per-operation timeout, a total time budget per response and a size cap per
  response (counted on the wire and after gzip decoding, so a gzip bomb can't get past it).
  Large files (DfT, ~65 MB) should be streamed to disk with `client.stream(...)`; the cap
  applies there too.

Errors are `FetchBlocked` / `ResponseTooLarge`, both `httpx.RequestError` subclasses, so the
adapters' existing `except httpx.HTTPError` handling covers them. Messages never contain the
URL path or query (the Nyland URL is private), only the host or the reason.

Environment proxies are ignored (`trust_env=False`): a proxy would resolve the target itself
and defeat the address check. If production ever needs an egress proxy, add it here on
purpose, with the proxy host pinned.

Tests pass `transport=httpx.MockTransport(...)` (no network); the allowlist, redirect and
size checks still apply. The address check is tested on `PinnedBackend` with a fake resolver.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import time
import zlib
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpcore
import httpx
import yaml

from ev_pipeline.sources import _common as c

MB = 1024 * 1024
DEFAULT_TIMEOUT_S = 60.0
"""Per operation (connect, each read, write, pool wait), not per download."""
DEFAULT_MAX_BYTES = 32 * MB
DEFAULT_MAX_SECONDS = 600.0
"""Total time budget for one response, from headers to last byte (slow-drip guard)."""
MAX_REDIRECTS = 5
CHUNK = 1 << 16

Resolver = Callable[[str, int], list[str]]


class FetchBlocked(httpx.RequestError):
    """The URL, a redirect target or a resolved address is not allowed for this source."""


class ResponseTooLarge(httpx.RequestError):
    """A response went over the source's size cap or total time budget."""


# --- policy -----------------------------------------------------------------------------


@dataclass(frozen=True)
class FetchPolicy:
    source_id: str
    hosts: tuple[str, ...]
    max_bytes: int = DEFAULT_MAX_BYTES
    max_seconds: float = DEFAULT_MAX_SECONDS

    def allows_host(self, host: str) -> bool:
        host = _norm_host(host)
        for entry in self.hosts:
            entry = _norm_host(entry)
            if entry.startswith("*."):
                if host.endswith(entry[1:]) and host != entry[2:]:
                    return True
            elif host == entry:
                return True
        return False

    def check_url(self, url: httpx.URL) -> None:
        """Raise FetchBlocked unless `url` is https, default port, no user info, allowed host."""
        host = url.host
        if url.scheme != "https":
            raise FetchBlocked(f"{self.source_id}: only https is allowed (got {url.scheme!r})")
        if url.port not in (None, 443):
            raise FetchBlocked(f"{self.source_id}: non-default port refused for {host}")
        if url.userinfo:
            raise FetchBlocked(f"{self.source_id}: URLs with user info are refused")
        if _is_ip_literal(host):
            raise FetchBlocked(f"{self.source_id}: IP-literal hosts are refused")
        if not self.allows_host(host):
            raise FetchBlocked(f"{self.source_id}: host {host!r} is not in data/sources.yaml")


def _norm_host(host: str) -> str:
    return host.strip().lower().rstrip(".")


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def sources_yaml_path() -> Path:
    """`sources.yaml` in the data dir (the /data mount in the image), else the repo copy."""
    path = c.data_dir() / "sources.yaml"
    return path if path.exists() else c.REPO_DIR / "data" / "sources.yaml"


def load_hosts(source_id: str, path: Path | None = None) -> tuple[str, ...]:
    """The `hosts:` list of one source in data/sources.yaml. Missing → ValueError (fail closed)."""
    path = path or sources_yaml_path()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for entry in data.get("sources") or []:
        if entry.get("id") == source_id:
            hosts = tuple(str(h) for h in entry.get("hosts") or [])
            if not hosts:
                raise ValueError(
                    f"{source_id}: no `hosts:` in {path.name}; add the hosts it fetches"
                )
            return hosts
    raise ValueError(f"{source_id}: not listed in {path.name}")


# --- address check ----------------------------------------------------------------------


def is_public_ip(addr: str) -> bool:
    """True only for globally routable unicast addresses."""
    try:
        ip = ipaddress.ip_address(addr.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return bool(ip.is_global and not (ip.is_multicast or ip.is_reserved or ip.is_unspecified))


def system_resolver(host: str, port: int) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise httpcore.ConnectError(f"cannot resolve {host}") from exc
    seen: list[str] = []
    for info in infos:
        ip = str(info[4][0])
        if ip not in seen:
            seen.append(ip)
    return seen


class PinnedBackend(httpcore.NetworkBackend):
    """Resolves, checks every address, then connects to the checked address itself."""

    def __init__(
        self, resolver: Resolver | None = None, inner: httpcore.NetworkBackend | None = None
    ) -> None:
        self._resolve = resolver or system_resolver
        self._inner = inner or httpcore.SyncBackend()

    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[Any] | None = None,
    ) -> httpcore.NetworkStream:
        ips = self._resolve(host, port)
        if not ips:
            raise httpcore.ConnectError(f"cannot resolve {host}")
        if any(not is_public_ip(ip) for ip in ips):
            # Refuse the host if *any* answer is internal: mixed answers are a rebinding trick.
            raise FetchBlocked(f"{host} resolves to a non-public address; refused")
        last: Exception | None = None
        for ip in ips:
            try:
                return self._inner.connect_tcp(
                    ip,
                    port,
                    timeout=timeout,
                    local_address=local_address,
                    socket_options=socket_options,
                )
            except (httpcore.ConnectError, httpcore.ConnectTimeout) as exc:
                last = exc
        assert last is not None
        raise last

    def connect_unix_socket(
        self, path: str, timeout: float | None = None, socket_options: Iterable[Any] | None = None
    ) -> httpcore.NetworkStream:
        raise FetchBlocked("unix sockets are refused")

    def sleep(self, seconds: float) -> None:
        self._inner.sleep(seconds)


def pinned_transport(resolver: Resolver | None = None) -> httpx.HTTPTransport:
    """An HTTPTransport whose connection pool uses PinnedBackend (no env proxy, verify on)."""
    transport = httpx.HTTPTransport(trust_env=True)  # trust_env here: SSL_CERT_FILE only
    # httpx 0.28 has no public hook for the network backend; swap the pool it built.
    # httpx is pinned in uv.lock and tests/test_net.py fails if this stops working.
    transport._pool = httpcore.ConnectionPool(  # noqa: SLF001
        ssl_context=httpx.create_ssl_context(trust_env=True),
        network_backend=PinnedBackend(resolver),
        http1=True,
        http2=False,
    )
    return transport


# --- limits -----------------------------------------------------------------------------


class _CappedStream(httpx.SyncByteStream):
    """Counts wire bytes, decodes gzip itself (capped), enforces the time budget."""

    def __init__(
        self, raw: httpx.SyncByteStream, policy: FetchPolicy, host: str, gzip: bool
    ) -> None:
        self._raw = raw
        self._policy = policy
        self._host = host
        self._gzip = gzip

    def _too_large(self, what: str) -> ResponseTooLarge:
        return ResponseTooLarge(
            f"{self._policy.source_id}: response from {self._host} {what}; aborted"
        )

    def __iter__(self) -> Iterator[bytes]:
        cap, deadline = self._policy.max_bytes, time.monotonic() + self._policy.max_seconds
        wire = out = 0
        dec = zlib.decompressobj(16 + zlib.MAX_WBITS) if self._gzip else None
        for chunk in self._raw:
            wire += len(chunk)
            if wire > cap:
                raise self._too_large(f"is over {cap} bytes")
            if time.monotonic() > deadline:
                raise self._too_large(f"took over {self._policy.max_seconds:.0f}s")
            if dec is None:
                out += len(chunk)
                yield chunk
                continue
            buf = chunk
            while buf and not dec.eof:
                part = dec.decompress(buf, CHUNK)
                buf = dec.unconsumed_tail
                out += len(part)
                if out > cap:
                    raise self._too_large(f"decodes to over {cap} bytes")
                if part:
                    yield part
        if dec is not None and (tail := dec.flush()):
            out += len(tail)
            if out > cap:
                raise self._too_large(f"decodes to over {cap} bytes")
            yield tail

    def close(self) -> None:
        self._raw.close()


class GuardedTransport(httpx.BaseTransport):
    """Checks each request (first hop and every redirect) and caps each response."""

    def __init__(self, policy: FetchPolicy, inner: httpx.BaseTransport) -> None:
        self.policy = policy
        self._inner = inner

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        try:
            self.policy.check_url(request.url)
        except FetchBlocked as exc:
            exc.request = request
            raise
        response = self._inner.handle_request(request)
        host = request.url.host
        length = response.headers.get("content-length", "")
        if length.isdigit() and int(length) > self.policy.max_bytes:
            response.close()
            raise ResponseTooLarge(
                f"{self.policy.source_id}: {host} announced {length} bytes, "
                f"cap is {self.policy.max_bytes}",
                request=request,
            )
        encoding = response.headers.get("content-encoding", "identity").strip().lower()
        if encoding not in ("", "identity", "gzip"):
            response.close()
            raise FetchBlocked(
                f"{self.policy.source_id}: unexpected content-encoding {encoding!r} from {host}",
                request=request,
            )
        headers = response.headers.copy()
        gzip = encoding == "gzip"
        if gzip:
            # We decode here (capped) so httpx doesn't decode again without a cap.
            del headers["content-encoding"]
            headers.pop("content-length", None)
        assert isinstance(response.stream, httpx.SyncByteStream)
        return httpx.Response(
            status_code=response.status_code,
            headers=headers,
            stream=_CappedStream(response.stream, self.policy, host, gzip),
            extensions=response.extensions,
            request=request,
        )

    def close(self) -> None:
        self._inner.close()


# --- the one entry point ----------------------------------------------------------------


def safe_client(
    source_id: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_S,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_seconds: float = DEFAULT_MAX_SECONDS,
    transport: httpx.BaseTransport | None = None,
    resolver: Resolver | None = None,
    sources_path: Path | None = None,
    hosts: Iterable[str] | None = None,
) -> httpx.Client:
    """An httpx.Client for one source: allowlisted hosts, SSRF guard, timeouts, size cap.

    `hosts` overrides data/sources.yaml (tests only). `transport` replaces the network layer
    (tests pass httpx.MockTransport); the allowlist and limits still apply on top of it.
    """
    policy = FetchPolicy(
        source_id=source_id,
        hosts=tuple(hosts) if hosts is not None else load_hosts(source_id, sources_path),
        max_bytes=max_bytes,
        max_seconds=max_seconds,
    )
    inner = transport if transport is not None else pinned_transport(resolver)
    return httpx.Client(
        transport=GuardedTransport(policy, inner),
        timeout=httpx.Timeout(timeout),
        follow_redirects=True,
        max_redirects=MAX_REDIRECTS,
        trust_env=False,
        headers={"User-Agent": c.USER_AGENT, "Accept-Encoding": "gzip"},
    )


# --- git sources (A-05 L6) --------------------------------------------------------------

GIT_REPO_PART = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})$")
GIT_SAFE_FLAGS = ("-c", "protocol.allow=never", "-c", "protocol.https.allow=always")
"""Only https may be used by git, also for submodules and redirects git itself follows."""


def check_git_url(
    source_id: str,
    url: str,
    *,
    sources_path: Path | None = None,
    hosts: Iterable[str] | None = None,
) -> str:
    """Return `url` if it is `https://github.com/<owner>/<repo>` and allowed, else raise.

    Git clones don't go through `safe_client`, so this is their gate: the URL must be plain
    https on the default port, no user info, query or fragment, exactly two path parts
    (an optional `.git` suffix is allowed), and its host must be listed under `hosts:` for
    `source_id` in data/sources.yaml. Fails closed with `FetchBlocked` (or `ValueError` from
    `load_hosts` when the source has no hosts). `hosts` overrides sources.yaml (tests only).
    """
    policy = FetchPolicy(
        source_id=source_id,
        hosts=tuple(hosts) if hosts is not None else load_hosts(source_id, sources_path),
    )
    try:
        parsed = httpx.URL(url)
    except (httpx.InvalidURL, TypeError) as exc:
        raise FetchBlocked(f"{source_id}: git URL does not parse") from exc
    policy.check_url(parsed)
    if parsed.host != "github.com":
        raise FetchBlocked(f"{source_id}: git sources must be on github.com (got {parsed.host!r})")
    if parsed.query or parsed.fragment or "?" in url or "#" in url:
        raise FetchBlocked(f"{source_id}: git URL must not carry a query or fragment")
    parts = parsed.path.split("/")
    if len(parts) != 3 or parts[0] != "":
        raise FetchBlocked(f"{source_id}: git URL must be https://github.com/<owner>/<repo>")
    owner, repo = parts[1], parts[2].removesuffix(".git")
    for part in (owner, repo):
        if not GIT_REPO_PART.match(part) or part in {".", ".."}:
            raise FetchBlocked(f"{source_id}: git URL must be https://github.com/<owner>/<repo>")
    return url


def git_clone_cmd(source_id: str, url: str, dest: str, **kwargs: Any) -> list[str]:
    """`git clone --depth 1` argv for a checked git source URL (see `check_git_url`)."""
    check_git_url(source_id, url, **kwargs)
    return ["git", *GIT_SAFE_FLAGS, "clone", "--depth", "1", "--quiet", "--", url, dest]


def git_ls_remote_cmd(source_id: str, url: str, **kwargs: Any) -> list[str]:
    """`git ls-remote <url> HEAD` argv for a checked git source URL."""
    check_git_url(source_id, url, **kwargs)
    return ["git", *GIT_SAFE_FLAGS, "ls-remote", "--", url, "HEAD"]
