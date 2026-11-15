"""ev_pipeline.net edge cases (overnight coverage pass): system resolver, empty answers,
every address failing, and sleep delegation. No network: socket.getaddrinfo is replaced
and the inner backend is a fake.
"""

from __future__ import annotations

import socket

import httpcore
import pytest

from ev_pipeline import net


class _Inner(httpcore.NetworkBackend):
    def __init__(self, fail: set[str] | None = None) -> None:
        self.connected: list[str] = []
        self.slept: list[float] = []
        self.fail = fail or set()

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        self.connected.append(host)
        if host in self.fail:
            raise httpcore.ConnectTimeout("slow")
        return object()  # type: ignore[return-value]

    def sleep(self, seconds):
        self.slept.append(seconds)


def test_system_resolver_dedupes_answers(monkeypatch) -> None:
    def fake(host, port, type=0):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", port)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2606:2800::1", port, 0, 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.215.14", port)),
        ]

    monkeypatch.setattr(net.socket, "getaddrinfo", fake)
    assert net.system_resolver("opendata.example.org", 443) == ["93.184.215.14", "2606:2800::1"]


def test_system_resolver_failure_is_a_connect_error(monkeypatch) -> None:
    def fail(host, port, type=0):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(net.socket, "getaddrinfo", fail)
    with pytest.raises(httpcore.ConnectError, match="cannot resolve nowhere.example"):
        net.system_resolver("nowhere.example", 443)


def test_no_answers_is_a_connect_error() -> None:
    backend = net.PinnedBackend(resolver=lambda h, p: [], inner=_Inner())
    with pytest.raises(httpcore.ConnectError, match="cannot resolve"):
        backend.connect_tcp("opendata.example.org", 443)


def test_every_address_failing_raises_the_last_error() -> None:
    inner = _Inner(fail={"1.1.1.1", "1.0.0.1"})
    backend = net.PinnedBackend(resolver=lambda h, p: ["1.1.1.1", "1.0.0.1"], inner=inner)
    with pytest.raises(httpcore.ConnectTimeout):
        backend.connect_tcp("opendata.example.org", 443)
    assert inner.connected == ["1.1.1.1", "1.0.0.1"]


def test_sleep_is_delegated() -> None:
    inner = _Inner()
    net.PinnedBackend(resolver=lambda h, p: [], inner=inner).sleep(0.5)
    assert inner.slept == [0.5]


@pytest.mark.parametrize("addr", ["", "not-an-ip", "fe80::1%eth0", "::ffff:10.0.0.1"])
def test_odd_addresses_are_not_public(addr: str) -> None:
    assert net.is_public_ip(addr) is False
