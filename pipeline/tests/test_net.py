"""Safe fetch helper (ev_pipeline.net): allowlist, redirects, SSRF guard, caps. No network."""

from __future__ import annotations

import gzip
from pathlib import Path

import httpcore
import httpx
import pytest
import yaml

from ev_pipeline import net

HOSTS = ("opendata.example.org", "*.cdn.example.org")


def client(handler, **kw) -> httpx.Client:
    return net.safe_client("test", hosts=HOSTS, transport=httpx.MockTransport(handler), **kw)


def ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=b"hello")


# --- allowlist ---------------------------------------------------------------------------


def test_allowed_host_passes():
    with client(ok) as cl:
        assert cl.get("https://opendata.example.org/x.json").content == b"hello"


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example.com/",
        "http://opendata.example.org/",  # plain http
        "https://opendata.example.org:8443/",  # odd port
        "https://user:pw@opendata.example.org/",  # user info
        "https://127.0.0.1/",
        "https://[::1]/",
        "https://169.254.169.254/latest/meta-data/",
        "https://cdn.example.org/",  # wildcard matches subdomains only
        "https://opendata.example.org.evil.com/",
    ],
)
def test_disallowed_urls_are_blocked(url):
    calls: list[httpx.Request] = []

    def handler(request):
        calls.append(request)
        return ok(request)

    with client(handler) as cl, pytest.raises(net.FetchBlocked):
        cl.get(url)
    assert calls == []  # refused before any request left


def test_wildcard_and_case_and_trailing_dot():
    with client(ok) as cl:
        assert cl.get("https://a.b.CDN.example.org./f").status_code == 200


def test_blocked_error_is_an_httpx_error_so_adapters_catch_it():
    with client(ok) as cl, pytest.raises(httpx.HTTPError):
        cl.get("https://evil.example.com/")


# --- redirects ---------------------------------------------------------------------------


def test_redirect_to_allowed_host_is_followed():
    def handler(request):
        if request.url.host == "opendata.example.org":
            return httpx.Response(302, headers={"location": "https://x.cdn.example.org/f"})
        return httpx.Response(200, content=b"file")

    with client(handler) as cl:
        assert cl.get("https://opendata.example.org/f").content == b"file"


@pytest.mark.parametrize(
    "location",
    ["https://evil.example.com/", "http://opendata.example.org/", "https://10.0.0.5/"],
)
def test_redirect_to_disallowed_target_is_blocked(location):
    seen: list[str] = []

    def handler(request):
        seen.append(str(request.url.host))
        return httpx.Response(302, headers={"location": location})

    with client(handler) as cl, pytest.raises(net.FetchBlocked):
        cl.get("https://opendata.example.org/f")
    assert seen == ["opendata.example.org"]


def test_redirect_loop_is_bounded():
    def handler(request):
        return httpx.Response(302, headers={"location": "https://opendata.example.org/again"})

    with client(handler) as cl, pytest.raises(httpx.TooManyRedirects):
        cl.get("https://opendata.example.org/f")


# --- size and time caps ------------------------------------------------------------------


def test_announced_size_over_cap_is_refused():
    def handler(request):
        return httpx.Response(200, headers={"content-length": "2000"}, content=b"x" * 2000)

    with client(handler, max_bytes=1000) as cl, pytest.raises(net.ResponseTooLarge):
        cl.get("https://opendata.example.org/big")


def test_unannounced_stream_over_cap_is_cut_off():
    def handler(request):
        chunks = (b"x" * 400 for _ in range(10))  # no content-length
        return httpx.Response(200, stream=_Iter(chunks))

    with client(handler, max_bytes=1000) as cl, pytest.raises(net.ResponseTooLarge):
        cl.get("https://opendata.example.org/big")


def test_stream_to_disk_respects_cap(tmp_path: Path):
    def handler(request):
        return httpx.Response(200, stream=_Iter(b"y" * 300 for _ in range(10)))

    out = tmp_path / "f.part"
    with (
        client(handler, max_bytes=1000) as cl,
        pytest.raises(net.ResponseTooLarge),
        cl.stream("GET", "https://opendata.example.org/big") as resp,
        out.open("wb") as fh,
    ):
        for chunk in resp.iter_bytes():
            fh.write(chunk)
    assert out.stat().st_size <= 1000


def test_under_cap_streams_fully():
    def handler(request):
        return httpx.Response(200, stream=_Iter(b"z" * 100 for _ in range(5)))

    with client(handler, max_bytes=1000) as cl:
        assert len(cl.get("https://opendata.example.org/f").content) == 500


def test_gzip_is_decoded_and_bomb_is_capped():
    small = gzip.compress(b"a,b\n1,2\n")
    bomb = gzip.compress(b"\0" * 5_000_000)  # ~5 KB on the wire
    assert len(bomb) < 10_000

    def handler(request):
        body = bomb if request.url.path == "/bomb" else small
        return httpx.Response(200, headers={"content-encoding": "gzip"}, content=body)

    with client(handler, max_bytes=100_000) as cl:
        assert cl.get("https://opendata.example.org/ok").text == "a,b\n1,2\n"
        with pytest.raises(net.ResponseTooLarge):
            cl.get("https://opendata.example.org/bomb")


def test_unexpected_content_encoding_is_refused():
    def handler(request):
        return httpx.Response(200, headers={"content-encoding": "br"}, content=b"..")

    with client(handler) as cl, pytest.raises(net.FetchBlocked):
        cl.get("https://opendata.example.org/f")


def test_time_budget_is_enforced(monkeypatch):
    clock = iter([0.0, 0.0, 999.0, 999.0, 999.0])
    monkeypatch.setattr(net.time, "monotonic", lambda: next(clock, 999.0))

    def handler(request):
        return httpx.Response(200, stream=_Iter(b"x" for _ in range(3)))

    with client(handler, max_seconds=10) as cl, pytest.raises(net.ResponseTooLarge):
        cl.get("https://opendata.example.org/slow")


def test_client_defaults():
    with client(ok, timeout=12) as cl:
        assert cl.timeout.read == 12
        assert cl.follow_redirects is True
        assert cl.max_redirects == net.MAX_REDIRECTS
        assert "ev-finder-pipeline" in cl.headers["user-agent"]


# --- address check (SSRF) ----------------------------------------------------------------


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1", "10.1.2.3", "172.16.0.1", "192.168.1.1", "169.254.169.254",
        "100.64.0.1", "0.0.0.0", "224.0.0.1", "240.0.0.1", "192.0.2.10",
        "::1", "fe80::1", "fc00::1", "::ffff:127.0.0.1", "::ffff:10.0.0.1", "::",
        "not-an-ip",
    ],
)  # fmt: skip
def test_non_public_addresses(ip):
    assert not net.is_public_ip(ip)


@pytest.mark.parametrize("ip", ["93.184.215.14", "1.1.1.1", "2606:4700:4700::1111"])
def test_public_addresses(ip):
    assert net.is_public_ip(ip)


class _FakeBackend(httpcore.NetworkBackend):
    def __init__(self, fail: set[str] | None = None) -> None:
        self.connected: list[tuple[str, int]] = []
        self.fail = fail or set()

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        self.connected.append((host, port))
        if host in self.fail:
            raise httpcore.ConnectError("down")
        return object()  # type: ignore[return-value]

    def sleep(self, seconds):
        pass


def test_backend_connects_to_the_checked_ip_not_the_name():
    inner = _FakeBackend()
    backend = net.PinnedBackend(resolver=lambda h, p: ["93.184.215.14"], inner=inner)
    backend.connect_tcp("opendata.example.org", 443)
    assert inner.connected == [("93.184.215.14", 443)]


def test_backend_refuses_if_any_answer_is_private():
    inner = _FakeBackend()
    backend = net.PinnedBackend(resolver=lambda h, p: ["93.184.215.14", "10.0.0.1"], inner=inner)
    with pytest.raises(net.FetchBlocked):
        backend.connect_tcp("opendata.example.org", 443)
    assert inner.connected == []


def test_backend_tries_next_address_on_connect_error():
    inner = _FakeBackend(fail={"1.1.1.1"})
    backend = net.PinnedBackend(resolver=lambda h, p: ["1.1.1.1", "1.0.0.1"], inner=inner)
    backend.connect_tcp("opendata.example.org", 443)
    assert inner.connected == [("1.1.1.1", 443), ("1.0.0.1", 443)]


def test_backend_refuses_unix_sockets():
    with pytest.raises(net.FetchBlocked):
        net.PinnedBackend(resolver=lambda h, p: []).connect_unix_socket("/run/x.sock")


def test_real_transport_uses_pinned_backend_end_to_end():
    """safe_client without a mock goes through PinnedBackend: a host that resolves to
    loopback is refused before any socket opens (proves the pool swap still works)."""
    cl = net.safe_client("test", hosts=HOSTS, resolver=lambda h, p: ["127.0.0.1"])
    with cl, pytest.raises(net.FetchBlocked):
        cl.get("https://opendata.example.org/")


# --- sources.yaml ------------------------------------------------------------------------


def test_load_hosts_and_fail_closed(tmp_path: Path):
    path = tmp_path / "sources.yaml"
    path.write_text(yaml.safe_dump({"sources": [{"id": "a", "hosts": ["x.org"]}, {"id": "b"}]}))
    assert net.load_hosts("a", path) == ("x.org",)
    with pytest.raises(ValueError, match="no `hosts:`"):
        net.load_hosts("b", path)
    with pytest.raises(ValueError, match="not listed"):
        net.load_hosts("c", path)


def test_every_http_source_in_the_repo_registry_has_hosts():
    """The adapters that fetch over HTTP must each have a host list in data/sources.yaml."""
    path = net.sources_yaml_path()
    for source_id in ("rdw", "eea", "kba-fz10", "ademe", "dft-veh", "nyland"):
        hosts = net.load_hosts(source_id, path)
        assert hosts and all("/" not in h and ":" not in h for h in hosts), source_id


class _Iter(httpx.SyncByteStream):
    def __init__(self, chunks) -> None:
        self._chunks = chunks

    def __iter__(self):
        yield from self._chunks
