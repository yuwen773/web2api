from __future__ import annotations

import pytest

from src.client.taiji_client import TaijiAPIError, TaijiClient
from src.utils.message_converter import convert_openai_messages
from tests.live_config import get_live_config


async def _new_logged_in_client() -> TaijiClient:
    config = get_live_config()
    client = TaijiClient(base_url=config.api_base, app_version=config.app_version)
    await client.login(config.account, config.password)
    return client


@pytest.mark.asyncio
async def test_phase1_4_delete_session() -> None:
    client = await _new_logged_in_client()
    session_id: int | None = None
    try:
        session_id = await client.create_session("gpt-4.1-mini")
        response = await client.delete_session(session_id)
        assert response.get("code") == 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_phase1_5_message_converter() -> None:
    case_1 = await convert_openai_messages(
        messages=[{"role": "user", "content": "你好"}],
        model="gpt-4.1-mini",
    )
    assert case_1 == {"text": "你好", "files": []}

    case_2 = await convert_openai_messages(
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好呀"},
            {"role": "user", "content": "今天天气怎么样？"},
        ],
        model="gpt-4.1-mini",
    )
    assert case_2["text"] == "系统提示：你是一个助手\n用户：你好\n助手：你好呀\n用户：今天天气怎么样？"
    assert case_2["files"] == []

    case_3 = await convert_openai_messages(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这是什么？"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,aGVsbG8="}},
                ],
            }
        ],
        model="gpt-4.1-mini",
    )
    assert case_3["text"] == "这是什么？"
    assert len(case_3["files"]) == 1
    assert case_3["files"][0]["data"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_phase1_6_send_message_non_stream() -> None:
    client = await _new_logged_in_client()
    session_id: int | None = None
    try:
        session_id = await client.create_session("gpt-4.1-mini")
        response = await client.send_message(
            session_id=session_id,
            text="你好，请用一句话介绍你自己",
            stream=False,
        )
        assert isinstance(response.get("text"), str) and response.get("text")
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
async def test_phase1_7_send_message_stream() -> None:
    client = await _new_logged_in_client()
    session_id: int | None = None
    try:
        session_id = await client.create_session("gpt-4.1-mini")
        stream = client.send_message(
            session_id=session_id,
            text="请数到5",
            stream=True,
        )
        chunks: list[dict[str, object]] = []
        async for chunk in stream:
            chunks.append(chunk)

        assert chunks
        assert all(chunk.get("code") == 0 for chunk in chunks)
        assert any(chunk.get("type") == "string" for chunk in chunks)
        assert any(chunk.get("type") == "object" for chunk in chunks)
    finally:
        if session_id is not None:
            try:
                await client.delete_session(session_id)
            except TaijiAPIError as exc:
                print(f"cleanup failed for session {session_id}: {exc}")
        await client.close()
