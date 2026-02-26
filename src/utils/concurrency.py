from __future__ import annotations

import asyncio


DEFAULT_MAX_CONCURRENT = 5
_semaphore: asyncio.Semaphore | None = None


def get_semaphore(limit: int = DEFAULT_MAX_CONCURRENT) -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(limit)
    return _semaphore
