from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiAPIError, TaijiClient
from tests.live_config import get_live_config


@pytest.mark.asyncio
async def test_send_message_non_stream_returns_full_response() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)
    session_id: int | None = None

    try:
        await client.login(config.account, config.password)
        session_id = await client.create_session("gpt-4.1-mini")

        response = await client.send_message(
            session_id=session_id,
            text="hello",
            stream=False,
        )
        print(f"text={response.get('text')}")
        print(
            "usage="
            f"{response.get('promptTokens')}/"
            f"{response.get('completionTokens')}/"
            f"{response.get('useTokens')}"
        )

        assert isinstance(response.get("text"), str)
        assert response.get("text")
        assert isinstance(response.get("promptTokens"), int)
        assert isinstance(response.get("completionTokens"), int)
        assert isinstance(response.get("useTokens"), int)
        assert response.get("taskId")
    finally:
        if session_id is not None:
            try:
                await client.delete_session(session_id)
            except TaijiAPIError as exc:
                print(f"cleanup failed for session {session_id}: {exc}")
        await client.close()


@pytest.mark.asyncio
async def test_send_message_stream_returns_ordered_chunks() -> None:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)
    session_id: int | None = None

    try:
        await client.login(config.account, config.password)
        session_id = await client.create_session("gpt-4.1-mini")

        chunks: list[dict[str, object]] = []
        stream = client.send_message(
            session_id=session_id,
            text="hello",
            stream=True,
        )
        async for chunk in stream:
            chunks.append(chunk)

        assert chunks
        assert all(chunk.get("code") == 0 for chunk in chunks)
        assert any(chunk.get("type") == "object" for chunk in chunks)

        text = "".join(str(chunk.get("data", "")) for chunk in chunks if chunk.get("type") == "string")
        print(f"stream_text={text}")
        assert text
    finally:
        if session_id is not None:
            try:
                await client.delete_session(session_id)
            except TaijiAPIError as exc:
                print(f"cleanup failed for session {session_id}: {exc}")
        await client.close()
