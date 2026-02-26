from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiClient, TaijiAPIError
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_phase1_login_models_and_sessions() -> None:
    """Integration test for phase 1.1~1.3 with safer error handling."""
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)
    created_session_ids: list[int] = []

    try:
        token = await client.login(config.account, config.password)
        assert token
        assert token.count(".") == 2
        assert client.server_name_session

        models = await client.get_models()
        assert len(models) >= 50
        assert all("label" in model and "value" in model for model in models)
        values = {model["value"] for model in models}
        assert "gpt-4.1-mini" in values
        assert "claude-opus-4-6" in values

        for _ in range(3):
            created_session_ids.append(await client.create_session("gpt-4.1-mini"))
        assert len(set(created_session_ids)) == 3
    finally:
        for session_id in created_session_ids:
            try:
                await client.delete_session(session_id)
            except TaijiAPIError as exc:
                print(f"cleanup failed for session {session_id}: {exc}")
        await client.close()
