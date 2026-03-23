from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(
    operation: Callable[[], T],
    retries: int = 3,
    backoff_seconds: float = 0.5,
) -> T:
    """Execute operation with exponential backoff retry."""
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= retries:
                break
            sleep_for = backoff_seconds * (2**attempt)
            time.sleep(sleep_for)
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry operation failed without exception")
