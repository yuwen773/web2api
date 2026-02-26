from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiClient
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_login_returns_jwt_and_session_cookie() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)

    try:
        token = await client.login(config.account, config.password)
        print(f"token_prefix={token[:20]}")
        assert token
        assert token.count(".") == 2
        assert client.server_name_session
    finally:
        await client.close()
