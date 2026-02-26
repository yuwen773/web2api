from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiClient
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_create_session_returns_numeric_and_unique_ids() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)

    try:
        await client.login(config.account, config.password)

        session_ids = [
            await client.create_session("gpt-4.1-mini"),
            await client.create_session("gpt-4.1-mini"),
            await client.create_session("gpt-4.1-mini"),
        ]
        print(f"session_ids={session_ids}")

        assert all(isinstance(session_id, int) for session_id in session_ids)
        assert len(set(session_ids)) == 3
    finally:
        await client.close()
