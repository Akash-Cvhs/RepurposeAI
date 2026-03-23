from __future__ import annotations

from typing import Any

import backend.utils.http_client as http_client


class _DummyResponse:
    def __init__(self, payload: dict[str, Any], should_fail: bool = False) -> None:
        self._payload = payload
        self._should_fail = should_fail

    def raise_for_status(self) -> None:
        if self._should_fail:
            raise RuntimeError("http error")

    def json(self) -> dict[str, Any]:
        return self._payload


def test_request_json_retries_then_succeeds(monkeypatch) -> None:
    http_client._CIRCUITS.clear()

    calls = {"count": 0}

    def fake_request(**kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("temporary failure")
        return _DummyResponse({"ok": True})

    monkeypatch.setattr(http_client.requests, "request", fake_request)
    monkeypatch.setattr(http_client.time, "sleep", lambda *_args, **_kwargs: None)

    payload = http_client.request_json(
        service="retry_service",
        method="GET",
        url="https://example.org",
        timeout=5,
    )

    assert payload["ok"] is True
    assert calls["count"] == 3


def test_request_json_opens_circuit_after_threshold(monkeypatch) -> None:
    http_client._CIRCUITS.clear()

    calls = {"count": 0}

    def always_fail(**kwargs):
        calls["count"] += 1
        raise RuntimeError("downstream failure")

    monkeypatch.setattr(http_client.requests, "request", always_fail)
    monkeypatch.setattr(http_client.time, "sleep", lambda *_args, **_kwargs: None)

    try:
        http_client.request_json(
            service="breaker_service",
            method="GET",
            url="https://example.org",
            timeout=5,
        )
    except RuntimeError:
        pass

    # Second call should fail fast because circuit is open.
    try:
        http_client.request_json(
            service="breaker_service",
            method="GET",
            url="https://example.org",
            timeout=5,
        )
        assert False, "Expected circuit-open failure"
    except RuntimeError as exc:
        assert "Circuit open" in str(exc)

    assert calls["count"] == http_client.HTTP_MAX_RETRIES + 1
