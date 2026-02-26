from __future__ import annotations

import asyncio
import importlib
from typing import Any

import httpx
import pytest

import src.client.taiji_client as taiji_client_module
import src.utils.concurrency as concurrency_module
from src.client.taiji_client import TaijiClient


class _StreamContext:
    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    async def __aenter__(self) -> httpx.Response:
        return self._response

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


class _SemaphoreProbe:
    def __init__(self) -> None:
        self.entered = 0
        self.exited = 0

    async def __aenter__(self) -> "_SemaphoreProbe":
        self.entered += 1
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.exited += 1
        return None


def _chat_sse_payload(text: str = "hello") -> bytes:
    return (
        f'data: {{"type":"string","code":0,"data":"{text}","msg":""}}\n\n'
        'data: {"type":"object","code":0,"data":{"promptTokens":1,"completionTokens":2,"useTokens":3,"model":"gpt-4.1-mini","taskId":"task-1"},"msg":""}\n\n'
        "data: [DONE]\n\n"
    ).encode("utf-8")


def _full_url(client: TaijiClient, path: str) -> str:
    return f"{client.base_url}{path}"


@pytest.mark.asyncio
async def test_request_retries_once_after_401_and_refreshes_auth_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = TaijiClient()
    client.token = "old-token"
    client._account = "demo-account"
    client._password = "demo-password"

    seen_auth_headers: list[str | None] = []
    request_count = 0
    relogin_count = 0

    async def fake_request(
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        del json
        nonlocal request_count
        request_count += 1
        seen_auth_headers.append(None if headers is None else headers.get("authorization"))
        request = httpx.Request(method, _full_url(client, url))
        if request_count == 1:
            return httpx.Response(
                status_code=401,
                request=request,
                json={"code": 401, "msg": "token expired"},
            )
        return httpx.Response(
            status_code=200,
            request=request,
            json={"code": 0, "data": {"ok": True}, "msg": ""},
        )

    async def fake_relogin() -> None:
        nonlocal relogin_count
        relogin_count += 1
        client.token = "new-token"
        client._client.headers["authorization"] = "new-token"

    monkeypatch.setattr(client._client, "request", fake_request)
    monkeypatch.setattr(client, "_relogin", fake_relogin)

    try:
        response = await client._request(
            "GET",
            "/api/chat/tmpl",
            headers={"authorization": "old-token"},
        )
    finally:
        await client.close()

    assert response.status_code == 200
    assert request_count == 2
    assert relogin_count == 1
    assert seen_auth_headers == ["old-token", "new-token"]


@pytest.mark.asyncio
async def test_request_retries_only_once_when_401_persists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = TaijiClient()
    client.token = "token-1"
    client._account = "demo-account"
    client._password = "demo-password"

    request_count = 0
    relogin_count = 0

    async def fake_request(
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        del headers, json
        nonlocal request_count
        request_count += 1
        request = httpx.Request(method, _full_url(client, url))
        return httpx.Response(
            status_code=401,
            request=request,
            json={"code": 401, "msg": "still expired"},
        )

    async def fake_relogin() -> None:
        nonlocal relogin_count
        relogin_count += 1
        client.token = "token-2"
        client._client.headers["authorization"] = "token-2"

    monkeypatch.setattr(client._client, "request", fake_request)
    monkeypatch.setattr(client, "_relogin", fake_relogin)

    try:
        response = await client._request(
            "GET",
            "/api/chat/tmpl",
            headers={"authorization": "token-1"},
        )
    finally:
        await client.close()

    assert response.status_code == 401
    assert request_count == 2
    assert relogin_count == 1


@pytest.mark.asyncio
async def test_stream_retries_once_after_401(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TaijiClient()
    client.token = "old-token"
    client._account = "demo-account"
    client._password = "demo-password"
    client._client.headers["authorization"] = "old-token"

    request = httpx.Request("POST", _full_url(client, "/api/chat/completions"))
    responses = [
        httpx.Response(
            status_code=401,
            request=request,
            json={"code": 401, "msg": "token expired"},
        ),
        httpx.Response(
            status_code=200,
            request=request,
            content=_chat_sse_payload("stream-ok"),
        ),
    ]

    seen_auth_headers: list[str | None] = []
    relogin_count = 0

    def fake_stream(
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _StreamContext:
        del method, url, json
        seen_auth_headers.append(None if headers is None else headers.get("authorization"))
        return _StreamContext(responses.pop(0))

    async def fake_relogin() -> None:
        nonlocal relogin_count
        relogin_count += 1
        client.token = "new-token"
        client._client.headers["authorization"] = "new-token"

    monkeypatch.setattr(client._client, "stream", fake_stream)
    monkeypatch.setattr(client, "_relogin", fake_relogin)

    try:
        response = await client.send_message(session_id=123, text="hello", stream=False)
    finally:
        await client.close()

    assert response["text"] == "stream-ok"
    assert relogin_count == 1
    assert seen_auth_headers == ["old-token", "new-token"]


def test_get_semaphore_returns_global_singleton() -> None:
    module = importlib.reload(concurrency_module)
    semaphore_1 = module.get_semaphore()
    semaphore_2 = module.get_semaphore()
    assert semaphore_1 is semaphore_2


@pytest.mark.asyncio
async def test_get_semaphore_enforces_default_limit() -> None:
    module = importlib.reload(concurrency_module)
    semaphore = module.get_semaphore()

    active = 0
    max_active = 0
    lock = asyncio.Lock()

    async def worker() -> None:
        nonlocal active, max_active
        async with semaphore:
            async with lock:
                active += 1
                max_active = max(max_active, active)
            await asyncio.sleep(0.01)
            async with lock:
                active -= 1

    await asyncio.gather(*(worker() for _ in range(10)))
    assert max_active <= module.DEFAULT_MAX_CONCURRENT


@pytest.mark.asyncio
async def test_send_message_uses_global_semaphore(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TaijiClient()
    client.token = "token-1"
    client._client.headers["authorization"] = "token-1"

    semaphore_probe = _SemaphoreProbe()
    request = httpx.Request("POST", _full_url(client, "/api/chat/completions"))
    response = httpx.Response(
        status_code=200,
        request=request,
        content=_chat_sse_payload("semaphore-ok"),
    )

    def fake_stream(
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _StreamContext:
        del method, url, json, headers
        return _StreamContext(response)

    monkeypatch.setattr(taiji_client_module, "get_semaphore", lambda: semaphore_probe)
    monkeypatch.setattr(client._client, "stream", fake_stream)

    try:
        result = await client.send_message(session_id=777, text="hello", stream=False)
    finally:
        await client.close()

    assert result["text"] == "semaphore-ok"
    assert semaphore_probe.entered == 1
    assert semaphore_probe.exited == 1
