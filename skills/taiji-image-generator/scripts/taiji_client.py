#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiji AI 客户端 - 独立版本，不依赖 web2api
支持 Windows / Linux / macOS
"""

from __future__ import annotations

import asyncio
import json
import platform
import sys
from collections.abc import AsyncIterator
from typing import Any, Literal, overload

import httpx


DEFAULT_ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"


def _get_platform_headers() -> tuple[str, str, str, str]:
    """根据当前平台返回合适的 HTTP 头信息"""
    system = platform.system()

    if system == "Windows":
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
            '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
            "?0",
            '"Windows"',
        )
    elif system == "Darwin":
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            '"Not:A-Brand";v="99", "Chromium";v="145", "Google Chrome";v="145"',
            "?0",
            '"macOS"',
        )
    else:  # Linux and others
        return (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            '"Not:A-Brand";v="99", "Chromium";v="145", "Google Chrome";v="145"',
            "?0",
            '"Linux"',
        )


DEFAULT_USER_AGENT, DEFAULT_SEC_CH_UA, DEFAULT_SEC_CH_UA_MOBILE, DEFAULT_SEC_CH_UA_PLATFORM = _get_platform_headers()
CHAT_REFERER_PATH = "/chat?_userMenuKey=chat"


class TaijiAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class TaijiClient:
    def __init__(
        self,
        *,
        base_url: str = "https://ai.aurod.cn",
        app_version: str = "2.14.0",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_version = app_version
        self.token: str | None = None
        self._account: str | None = None
        self._password: str | None = None
        self.server_name_session: str | None = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._default_headers(),
            cookies=httpx.Cookies(),
        )

    async def __aenter__(self) -> TaijiClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    @property
    def chat_referer(self) -> str:
        return f"{self.base_url}{CHAT_REFERER_PATH}"

    async def login(self, account: str, password: str) -> str:
        account_hint = self._mask_account(account)
        print(f"[TaijiClient] 登录中: {account_hint}")

        try:
            payload = {"account": account, "password": password, "captchaId": ""}

            response = await self._request(
                "POST",
                "/api/user/login",
                json_payload=payload,
                headers=self._headers(
                    accept="application/json, text/plain, */*",
                    content_type="application/json",
                    referer=f"{self.base_url}/auth",
                    origin=self.base_url,
                ),
                retry_on_401=False,
            )
            body = self._extract_body(response)

            code = body.get("code")
            if code != 0:
                raise TaijiAPIError(
                    body.get("msg") or "Taiji login failed.",
                    code=code,
                    status_code=response.status_code,
                )

            data = body.get("data")
            if not isinstance(data, dict):
                raise TaijiAPIError(
                    "Taiji login response has unexpected format.",
                    status_code=response.status_code,
                )

            token = data.get("token")
            if not token:
                raise TaijiAPIError(
                    "Taiji login failed.",
                    code=code,
                    status_code=response.status_code,
                )

            self.token = token
            self._account = account
            self._password = password
            self._client.headers["authorization"] = self._authorization_header()
            self.server_name_session = (
                self._client.cookies.get("server_name_session")
                or response.cookies.get("server_name_session")
            )
        except TaijiAPIError as exc:
            print(f"[TaijiClient] 登录失败: {exc}")
            raise

        print(f"[TaijiClient] 登录成功")
        return self.token

    async def create_session(self, model: str) -> int:
        response = await self._request(
            "POST",
            "/api/chat/session",
            json_payload={"model": model, "plugins": [], "mcp": []},
            headers=self._headers(
                accept="application/json, text/plain, */*",
                content_type="application/json",
                referer=self.chat_referer,
                origin=self.base_url,
                include_auth=True,
            ),
        )
        body = self._extract_body(response)
        self._assert_success(body, response.status_code)

        data = body.get("data")
        if not isinstance(data, dict):
            raise TaijiAPIError(
                "Taiji create_session response does not contain a valid data object.",
                status_code=response.status_code,
            )

        session_id = data.get("id")
        if isinstance(session_id, int):
            return session_id
        if isinstance(session_id, str) and session_id.isdigit():
            return int(session_id)
        raise TaijiAPIError(
            "Taiji create_session response does not contain a valid session id.",
            status_code=response.status_code,
        )

    async def delete_session(self, session_id: int) -> dict[str, Any]:
        response = await self._request(
            "DELETE",
            f"/api/chat/session/{session_id}",
            headers=self._headers(
                accept="application/json, text/plain, */*",
                referer=self.chat_referer,
                origin=self.base_url,
                include_auth=True,
            ),
        )
        body = self._extract_body(response)
        self._assert_success(body, response.status_code)
        return body

    @overload
    def send_message(
        self,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None = None,
        *,
        stream: Literal[False] = False,
    ) -> Any: ...

    @overload
    def send_message(
        self,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None = None,
        *,
        stream: Literal[True],
    ) -> AsyncIterator[dict[str, Any]]: ...

    def send_message(
        self,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None = None,
        *,
        stream: bool = False,
    ) -> Any:
        if stream:
            return self._send_message_stream(session_id=session_id, text=text, files=files)
        return self._send_message_non_stream(session_id=session_id, text=text, files=files)

    async def _send_message_non_stream(
        self,
        *,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None,
    ) -> dict[str, Any]:
        text_parts: list[str] = []
        summary_data: dict[str, Any] | None = None

        async for chunk in self._iter_chat_chunks(
            session_id=session_id,
            text=text,
            files=files,
        ):
            chunk_type = chunk.get("type")
            if chunk_type == "string":
                text_parts.append(str(chunk.get("data", "")))
                continue

            if chunk_type == "object" and isinstance(chunk.get("data"), dict):
                summary_data = chunk["data"]

        if summary_data is None:
            raise TaijiAPIError("Taiji chat response is missing the final summary chunk.")

        return {
            "text": "".join(text_parts),
            "promptTokens": self._safe_int(summary_data.get("promptTokens")) or 0,
            "completionTokens": self._safe_int(summary_data.get("completionTokens")) or 0,
            "useTokens": self._safe_int(summary_data.get("useTokens")) or 0,
            "model": str(summary_data.get("model") or ""),
            "taskId": str(summary_data.get("taskId") or ""),
        }

    async def _send_message_stream(
        self,
        *,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None,
    ) -> AsyncIterator[dict[str, Any]]:
        try:
            async for chunk in self._iter_chat_chunks(
                session_id=session_id,
                text=text,
                files=files,
            ):
                yield chunk
        except asyncio.CancelledError:
            print("[TaijiClient] 客户端断开连接")
            raise

    async def _iter_chat_chunks(
        self,
        *,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None,
    ) -> AsyncIterator[dict[str, Any]]:
        for attempt in range(2):
            try:
                async with self._client.stream(
                    "POST",
                    "/api/chat/completions",
                    json={
                        "text": text,
                        "sessionId": session_id,
                        "files": files or [],
                    },
                    headers=self._headers(
                        accept="text/event-stream",
                        content_type="application/json",
                        referer=self.chat_referer,
                        origin=self.base_url,
                        include_auth=True,
                    ),
                ) as response:
                    if response.status_code == 401 and attempt == 0:
                        await response.aread()
                        print("[TaijiClient] 收到 401，正在重新登录...")
                        await self._relogin()
                        continue

                    if response.status_code >= 400:
                        body_text = await response.text()
                        print(f"[TaijiClient] HTTP 错误: {response.status_code} - {body_text[:200]}")
                        self._extract_body(response)
                        return

                    lines_received = 0
                    async for raw_line in response.aiter_lines():
                        line = raw_line.strip()
                        lines_received += 1

                        if not line or not line.startswith("data:"):
                            continue

                        payload = line[5:].strip()
                        if not payload:
                            continue
                        if payload == "[DONE]":
                            return

                        chunk = self._parse_sse_payload(payload, response.status_code)
                        self._assert_sse_chunk_success(chunk, response.status_code)
                        yield chunk
                    return
            except httpx.RequestError as exc:
                raise TaijiAPIError(f"Taiji stream request failed: {exc!s}") from exc

    def _default_headers(self) -> dict[str, str]:
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": DEFAULT_ACCEPT_LANGUAGE,
            "content-type": "application/json",
            "x-app-version": self.app_version,
            "user-agent": DEFAULT_USER_AGENT,
            "sec-ch-ua": DEFAULT_SEC_CH_UA,
            "sec-ch-ua-mobile": DEFAULT_SEC_CH_UA_MOBILE,
            "sec-ch-ua-platform": DEFAULT_SEC_CH_UA_PLATFORM,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "priority": "u=1, i",
            "origin": self.base_url,
            "referer": self.chat_referer,
        }

    def _headers(
        self,
        *,
        accept: str | None = None,
        content_type: str | None = None,
        referer: str | None = None,
        origin: str | None = None,
        include_auth: bool = False,
    ) -> dict[str, str]:
        headers: dict[str, str] = {"x-app-version": self.app_version}
        if accept:
            headers["accept"] = accept
        if content_type:
            headers["content-type"] = content_type
        if referer:
            headers["referer"] = referer
        if origin:
            headers["origin"] = origin
        if include_auth:
            headers["authorization"] = self._authorization_header()
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        json_payload: dict[str, Any] | None = None,
        retry_on_401: bool = True,
    ) -> httpx.Response:
        request_headers = dict(headers) if headers else None
        for attempt in range(2):
            try:
                response = await self._client.request(
                    method=method,
                    url=path,
                    headers=request_headers,
                    json=json_payload,
                )
            except httpx.RequestError as exc:
                raise TaijiAPIError(f"Taiji request failed: {exc!s}") from exc

            should_retry_401 = (
                response.status_code == 401
                and retry_on_401
                and attempt == 0
                and path != "/api/user/login"
                and self.token is not None
            )
            if not should_retry_401:
                return response

            await response.aread()
            await self._relogin()
            if request_headers is not None:
                self._refresh_authorization_header(request_headers)

        return response

    def _refresh_authorization_header(self, headers: dict[str, str]) -> None:
        if "authorization" in headers:
            headers["authorization"] = self._authorization_header()

    async def _relogin(self) -> None:
        if not self._account or not self._password:
            raise TaijiAPIError(
                "Token expired but no stored credentials are available for automatic re-login.",
                status_code=401,
            )
        print("[TaijiClient] Token 过期，正在重新认证...")
        await self.login(self._account, self._password)

    def _parse_sse_payload(self, payload: str, status_code: int) -> dict[str, Any]:
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise TaijiAPIError(
                f"Taiji SSE chunk is not valid JSON: {payload!r}",
                status_code=status_code,
            ) from exc

        if not isinstance(parsed, dict):
            raise TaijiAPIError(
                "Taiji SSE chunk has unexpected structure.",
                status_code=status_code,
            )
        return parsed

    def _assert_sse_chunk_success(self, chunk: dict[str, Any], status_code: int) -> None:
        code = self._safe_int(chunk.get("code"))
        if code == 0:
            return

        message = str(chunk.get("err") or chunk.get("msg") or chunk.get("data") or "Taiji SSE stream returned an error.")
        raise TaijiAPIError(
            message,
            code=code,
            status_code=status_code,
        )

    def _authorization_header(self) -> str:
        if not self.token:
            raise TaijiAPIError("Not logged in. Call login() first.")
        token = self.token.strip()
        if token.lower().startswith("bearer "):
            return token.split(" ", 1)[1].strip()
        return token

    def _extract_body(self, response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError as exc:
            raise TaijiAPIError(
                "Taiji API returned a non-JSON response.",
                status_code=response.status_code,
            ) from exc

        if not isinstance(body, dict):
            raise TaijiAPIError(
                "Taiji API returned an unexpected JSON structure.",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            raise TaijiAPIError(
                str(body.get("msg") or f"HTTP {response.status_code}"),
                code=self._safe_int(body.get("code")),
                status_code=response.status_code,
            )

        return body

    def _assert_success(self, body: dict[str, Any], status_code: int) -> None:
        code = self._safe_int(body.get("code"))
        if code == 0:
            return
        raise TaijiAPIError(
            str(body.get("msg") or "Taiji API returned an error."),
            code=code,
            status_code=status_code,
        )

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.lstrip("-").isdigit():
            return int(value)
        return None

    @staticmethod
    def _mask_account(account: str) -> str:
        normalized = account.strip()
        if len(normalized) <= 4:
            return "***"
        return f"{normalized[:2]}***{normalized[-2:]}"
