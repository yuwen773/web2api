from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from src.api.openai import router


class FakeTaijiClient:
    def __init__(self) -> None:
        self.session_id = 101
        self.created_models: list[str] = []
        self.deleted_sessions: list[int] = []
        self.sent_messages: list[dict[str, Any]] = []
        self.models: list[dict[str, str]] = []
        self.non_stream_response: dict[str, Any] = {
            "text": "hello from taiji",
            "promptTokens": 3,
            "completionTokens": 7,
            "useTokens": 10,
            "model": "gpt-4.1-mini",
            "taskId": "task-1",
        }
        self.stream_chunks: list[dict[str, Any]] = []

    async def create_session(self, model: str) -> int:
        self.created_models.append(model)
        return self.session_id

    async def delete_session(self, session_id: int) -> dict[str, Any]:
        self.deleted_sessions.append(session_id)
        return {"code": 0}

    async def get_models(self) -> list[dict[str, str]]:
        return self.models

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


@pytest.mark.asyncio
async def test_responses_create_non_stream_basic() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "input": "hello",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["model"] == "gpt-4.1-mini"
    assert body["status"] == "completed"
    # Codex 格式: output 是 message 数组
    assert body["output"][0]["type"] == "message"
    assert body["output"][0]["role"] == "assistant"
    assert body["output"][0]["content"][0]["type"] == "output_text"
    assert body["output"][0]["content"][0]["text"] == "hello from taiji"
    assert body["usage"] == {
        "prompt_tokens": 3,
        "completion_tokens": 7,
        "total_tokens": 10,
    }
    assert fake_client.created_models == ["gpt-4.1-mini"]
    assert fake_client.deleted_sessions == [101]
    assert fake_client.sent_messages[0]["stream"] is False
    assert fake_client.sent_messages[0]["text"] == "hello"


@pytest.mark.asyncio
async def test_responses_create_with_instructions() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "input": "hello",
                "instructions": "You are a helpful assistant.",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    assert body["output"][0]["type"] == "message"
    assert body["output"][0]["content"][0]["text"] == "hello from taiji"
    assert fake_client.created_models == ["gpt-4.1-mini"]
    assert fake_client.deleted_sessions == [101]


@pytest.mark.asyncio
async def test_responses_create_stream_returns_events() -> None:
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
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "stream": True,
                "input": "hello",
            },
        ) as response:
            raw_payload = (await response.aread()).decode("utf-8")

    assert response.status_code == 200
    sse_lines = [line for line in raw_payload.splitlines() if line.startswith("data: ")]

    payloads = [json.loads(line[6:]) for line in sse_lines]

    # First event should be response.created
    assert payloads[0]["type"] == "response.created"
    assert payloads[0]["response"]["status"] == "in_progress"
    assert "id" in payloads[0]["response"]

    # Second event should be response.output_item.added
    assert payloads[1]["type"] == "response.output_item.added"
    assert payloads[1]["item"]["type"] == "text"

    # Content events should be response.delta
    content = "".join(
        payload["delta"]["text"]
        for payload in payloads
        if payload["type"] == "response.delta"
    )
    assert content == "Hello"

    # Last events should be completion events
    assert payloads[-2]["type"] == "response.output_item.done"
    assert payloads[-1]["type"] == "response.done"
    assert payloads[-1]["response"]["status"] == "completed"

    assert fake_client.deleted_sessions == [101]
    assert fake_client.sent_messages[0]["stream"] is True


@pytest.mark.asyncio
async def test_responses_create_with_temperature() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "input": "hello",
                "temperature": 0.7,
                "max_tokens": 100,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    assert fake_client.created_models == ["gpt-4.1-mini"]
    assert fake_client.deleted_sessions == [101]


@pytest.mark.asyncio
async def test_responses_create_input_items() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "input": [
                    {"type": "text", "text": "hello"},
                    {"type": "text", "text": " world"},
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    # Text inputs should be concatenated
    assert fake_client.sent_messages[0]["text"] == "hello\n world"


@pytest.mark.asyncio
async def test_responses_create_minimal() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"


@pytest.mark.asyncio
async def test_responses_create_missing_model() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "input": "hello",
            },
        )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_responses_create_with_codex_str_format() -> None:
    """测试 Codex 兼容格式: input = {"str": "..."}"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4.1-mini",
                "input": {"str": "hello from codex"},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    assert body["output"][0]["type"] == "message"
    # 假客户端返回固定的 "hello from taiji"
    assert body["output"][0]["content"][0]["text"] == "hello from taiji"
    assert fake_client.sent_messages[0]["text"] == "hello from codex"
