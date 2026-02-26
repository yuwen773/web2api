from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiClient
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_get_models_contains_expected_entries() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)

    try:
        await client.login(config.account, config.password)
        models = await client.get_models()
        print(f"models_count={len(models)}")

        assert len(models) >= 50
        assert all("label" in model and "value" in model for model in models)

        values = {model["value"] for model in models}
        assert "gpt-4.1-mini" in values
        assert "claude-opus-4-6" in values
    finally:
        await client.close()
