from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from src.api.anthropic import router


class FakeTaijiClient:
    def __init__(self) -> None:
        self.session_id = 101
        self.created_models: list[str] = []
        self.deleted_sessions: list[int] = []
        self.sent_messages: list[dict[str, Any]] = []
        self.non_stream_response: dict[str, Any] = {
            "text": "hello from taiji",
            "promptTokens": 3,
            "completionTokens": 7,
            "useTokens": 10,
            "model": "claude-opus-4-6",
            "taskId": "task-1",
        }
        self.stream_chunks: list[dict[str, Any]] = []

    async def create_session(self, model: str) -> int:
        self.created_models.append(model)
        return self.session_id

    async def delete_session(self, session_id: int) -> dict[str, Any]:
        self.deleted_sessions.append(session_id)
        return {"code": 0}

    def send_message(
        self,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None = None,
        *,
        stream: bool = False,
    ) -> Any:
        self.sent_messages.append(
            {
                "session_id": session_id,
                "text": text,
                "files": files or [],
                "stream": stream,
            }
        )
        if stream:
            return self._stream_generator()
        return self._non_stream_result()

    async def _non_stream_result(self) -> dict[str, Any]:
        return self.non_stream_response

    async def _stream_generator(self) -> AsyncIterator[dict[str, Any]]:
        for chunk in self.stream_chunks:
            yield chunk


def _build_test_app(fake_client: FakeTaijiClient) -> FastAPI:
    app = FastAPI()
    app.state.taiji_client = fake_client
    app.include_router(router)
    return app


def _parse_anthropic_sse(raw_payload: str) -> list[tuple[str, dict[str, Any]]]:
    entries: list[tuple[str, dict[str, Any]]] = []
    blocks = [block for block in raw_payload.split("\n\n") if block.strip()]
    for block in blocks:
        event_name = ""
        payload: dict[str, Any] | None = None
        for line in block.splitlines():
            if line.startswith("event: "):
                event_name = line[len("event: ") :].strip()
            elif line.startswith("data: "):
                payload = json.loads(line[len("data: ") :])
        if event_name and payload is not None:
            entries.append((event_name, payload))
    return entries


@pytest.mark.asyncio
async def test_messages_non_stream_returns_anthropic_shape() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/messages",
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "message"
    assert body["role"] == "assistant"
    assert body["model"] == "claude-opus-4-6"
    assert body["content"] == [{"type": "text", "text": "hello from taiji"}]
    assert body["stop_reason"] == "end_turn"
    assert body["stop_sequence"] is None
    assert body["usage"] == {
        "input_tokens": 3,
        "output_tokens": 7,
    }
    assert fake_client.created_models == ["claude-opus-4-6"]
    assert fake_client.deleted_sessions == [101]
    assert fake_client.sent_messages[0]["stream"] is False
    assert fake_client.sent_messages[0]["text"] == "hello"


@pytest.mark.asyncio
async def test_messages_stream_returns_anthropic_sse_events() -> None:
    fake_client = FakeTaijiClient()
    fake_client.stream_chunks = [
        {"type": "string", "code": 0, "data": "Hel"},
        {"type": "string", "code": 0, "data": "lo"},
        {
            "type": "object",
            "code": 0,
            "data": {
                "promptTokens": 2,
                "completionTokens": 3,
                "useTokens": 5,
            },
        },
    ]
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        async with client.stream(
            "POST",
            "/v1/messages",
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 4096,
                "stream": True,
                "messages": [{"role": "user", "content": "hello"}],
            },
        ) as response:
            raw_payload = (await response.aread()).decode("utf-8")

    assert response.status_code == 200
    parsed = _parse_anthropic_sse(raw_payload)
    event_names = [event for event, _ in parsed]

    assert "content_block_delta" in event_names
    assert event_names[-1] == "message_stop"

    content = "".join(
        payload["delta"]["text"]
        for event, payload in parsed
        if event == "content_block_delta"
    )
    assert content == "Hello"

    message_delta_payload = [payload for event, payload in parsed if event == "message_delta"]
    assert message_delta_payload[-1]["delta"]["stop_reason"] == "end_turn"
    assert message_delta_payload[-1]["usage"]["output_tokens"] == 3
    assert fake_client.deleted_sessions == [101]
    assert fake_client.sent_messages[0]["stream"] is True


@pytest.mark.asyncio
async def test_messages_stream_peek_first_error_chunk_returns_400() -> None:
    fake_client = FakeTaijiClient()
    fake_client.stream_chunks = [
        {"type": "string", "code": 1001, "msg": "bad request", "data": ""},
    ]
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/messages",
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 4096,
                "stream": True,
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 400
    assert "Taiji error" in response.json()["detail"]
    assert fake_client.deleted_sessions == [101]
