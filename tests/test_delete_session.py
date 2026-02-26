from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiClient
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_delete_session_returns_success_code() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)

    try:
        await client.login(config.account, config.password)
        session_id = await client.create_session("gpt-4.1-mini")
        response = await client.delete_session(session_id)
        assert response.get("code") == 0
    finally:
        await client.close()
