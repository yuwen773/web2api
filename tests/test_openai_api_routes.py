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
async def test_chat_completions_non_stream_returns_openai_shape() -> None:
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4.1-mini",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "chat.completion"
    assert body["model"] == "gpt-4.1-mini"
    assert body["choices"][0]["message"]["role"] == "assistant"
    assert body["choices"][0]["message"]["content"] == "hello from taiji"
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
async def test_chat_completions_stream_returns_openai_sse_and_done() -> None:
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
            "/v1/chat/completions",
            json={
                "model": "gpt-4.1-mini",
                "stream": True,
                "messages": [{"role": "user", "content": "hello"}],
            },
        ) as response:
            raw_payload = (await response.aread()).decode("utf-8")

    assert response.status_code == 200
    sse_lines = [line for line in raw_payload.splitlines() if line.startswith("data: ")]
    assert sse_lines[-1] == "data: [DONE]"

    payloads = [json.loads(line[6:]) for line in sse_lines[:-1]]
    assert payloads[0]["choices"][0]["delta"]["role"] == "assistant"

    content = "".join(
        payload["choices"][0]["delta"].get("content", "")
        for payload in payloads
    )
    assert content == "Hello"
    assert payloads[-1]["choices"][0]["finish_reason"] == "stop"
    assert fake_client.deleted_sessions == [101]
    assert fake_client.sent_messages[0]["stream"] is True


@pytest.mark.asyncio
async def test_chat_completions_stream_peek_first_error_chunk_returns_400() -> None:
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
            "/v1/chat/completions",
            json={
                "model": "gpt-4.1-mini",
                "stream": True,
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

    assert response.status_code == 400
    assert "太极AI错误" in response.json()["detail"]
    assert fake_client.deleted_sessions == [101]


@pytest.mark.asyncio
async def test_models_route_returns_openai_list_shape() -> None:
    fake_client = FakeTaijiClient()
    fake_client.models = [
        {"label": "GPT-4.1 Mini", "value": "gpt-4.1-mini"},
        {"label": "Claude Opus 4.6", "value": "claude-opus-4-6"},
    ]
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "list"
    assert len(body["data"]) == 2
    assert body["data"][0]["id"] == "gpt-4.1-mini"
    assert body["data"][0]["object"] == "model"
    assert body["data"][0]["owned_by"] == "taiji"

