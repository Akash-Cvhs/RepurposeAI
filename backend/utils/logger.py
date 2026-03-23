from __future__ import annotations

from loguru import logger


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


def get_logger():
    return logger
