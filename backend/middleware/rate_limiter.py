from __future__ import annotations

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def apply_rate_limiter(app: FastAPI) -> Limiter:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, limiter._rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    return limiter
