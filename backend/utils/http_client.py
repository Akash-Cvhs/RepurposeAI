from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from backend.config import (
    HTTP_CIRCUIT_BREAKER_THRESHOLD,
    HTTP_CIRCUIT_RESET_SECONDS,
    HTTP_MAX_RETRIES,
    HTTP_RETRY_BACKOFF_SECONDS,
)


@dataclass
class _CircuitState:
    failures: int = 0
    open_until_epoch: float = 0.0


_CIRCUITS: Dict[str, _CircuitState] = {}


def _get_circuit(service: str) -> _CircuitState:
    state = _CIRCUITS.get(service)
    if state is None:
        state = _CircuitState()
        _CIRCUITS[service] = state
    return state


def _ensure_circuit_closed(service: str) -> None:
    state = _get_circuit(service)
    now = time.time()
    if state.open_until_epoch > now:
        retry_after = int(state.open_until_epoch - now)
        raise RuntimeError(f"Circuit open for service '{service}', retry after {retry_after}s")


def _record_success(service: str) -> None:
    state = _get_circuit(service)
    state.failures = 0
    state.open_until_epoch = 0.0


def _record_failure(service: str) -> None:
    state = _get_circuit(service)
    state.failures += 1
    if state.failures >= HTTP_CIRCUIT_BREAKER_THRESHOLD:
        state.open_until_epoch = time.time() + HTTP_CIRCUIT_RESET_SECONDS


def request_json(
    *,
    service: str,
    method: str,
    url: str,
    timeout: int,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Resilient HTTP JSON request with retry and circuit breaker semantics."""
    _ensure_circuit_closed(service)

    last_error: Exception | None = None
    for attempt in range(HTTP_MAX_RETRIES + 1):
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_body,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError("Expected JSON object response")
            _record_success(service)
            return payload
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            _record_failure(service)
            if attempt >= HTTP_MAX_RETRIES:
                break
            time.sleep(max(0, HTTP_RETRY_BACKOFF_SECONDS * (attempt + 1)))

    raise RuntimeError(f"HTTP request failed for service '{service}': {last_error}")
