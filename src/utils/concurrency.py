from __future__ import annotations

import asyncio


DEFAULT_MAX_CONCURRENT = 5
_semaphore: asyncio.Semaphore | None = None
_configured_limit = DEFAULT_MAX_CONCURRENT


def _validate_limit(limit: int) -> int:
    if limit < 1:
        raise ValueError("max_concurrent must be greater than 0.")
    return limit


def configure_semaphore(limit: int) -> None:
    global _configured_limit
    global _semaphore
    _configured_limit = _validate_limit(limit)
    _semaphore = asyncio.Semaphore(_configured_limit)


def get_semaphore(limit: int = DEFAULT_MAX_CONCURRENT) -> asyncio.Semaphore:
    global _semaphore
    global _configured_limit

    if _semaphore is None:
        _configured_limit = _validate_limit(limit)
        _semaphore = asyncio.Semaphore(_configured_limit)
    return _semaphore
