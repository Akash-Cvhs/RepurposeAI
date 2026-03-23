from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception):  # noqa: ANN001
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Unhandled server error",
                "error": str(exc),
                "path": str(request.url.path),
            },
        )
