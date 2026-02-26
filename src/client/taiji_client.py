from __future__ import annotations

from typing import Any

import httpx

from src.models.auth import LoginRequest, LoginResponse


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/145.0.0.0 Safari/537.36"
)
DEFAULT_SEC_CH_UA = '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"'
DEFAULT_SEC_CH_UA_MOBILE = "?0"
DEFAULT_SEC_CH_UA_PLATFORM = '"Windows"'


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
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_version = app_version
        self.token: str | None = None
        self.server_name_session: str | None = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
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
                "referer": f"{self.base_url}/chat",
            },
            cookies=httpx.Cookies(),
        )

    async def __aenter__(self) -> TaijiClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    @property
    def cookies(self) -> httpx.Cookies:
        return self._client.cookies

    async def login(self, account: str, password: str) -> str:
        payload = LoginRequest(account=account, password=password).model_dump()
        payload["captchaId"] = ""

        response = await self._client.post(
            "/api/user/login",
            json=payload,
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "x-app-version": self.app_version,
                "origin": self.base_url,
                "referer": f"{self.base_url}/auth",
            },
        )
        body = self._extract_body(response)

        parsed = LoginResponse.model_validate(body)
        if parsed.code != 0 or parsed.data is None or not parsed.data.token:
            raise TaijiAPIError(
                parsed.msg or "Taiji login failed.",
                code=parsed.code,
                status_code=response.status_code,
            )

        self.token = parsed.data.token
        self._client.headers["authorization"] = self._authorization_header()
        self.server_name_session = (
            self._client.cookies.get("server_name_session")
            or response.cookies.get("server_name_session")
        )
        return self.token

    async def get_models(self) -> list[dict[str, str]]:
        response = await self._client.get(
            "/api/chat/tmpl",
            headers={
                "accept": "application/json, text/plain, */*",
                "authorization": self._authorization_header(),
                "x-app-version": self.app_version,
                "referer": f"{self.base_url}/chat",
            },
        )
        body = self._extract_body(response)
        self._assert_success(body, response.status_code)
        return self._extract_models(body)

    async def create_session(self, model: str) -> int:
        response = await self._client.post(
            "/api/chat/session",
            json={
                "model": model,
                "plugins": [],
                "mcp": [],
            },
            headers={
                "accept": "application/json, text/plain, */*",
                "authorization": self._authorization_header(),
                "content-type": "application/json",
                "x-app-version": self.app_version,
                "origin": self.base_url,
                "referer": f"{self.base_url}/chat",
            },
        )
        body = self._extract_body(response)
        self._assert_success(body, response.status_code)

        session_id = body.get("data", {}).get("id")
        if isinstance(session_id, int):
            return session_id
        if isinstance(session_id, str) and session_id.isdigit():
            return int(session_id)
        raise TaijiAPIError(
            "Taiji create_session response does not contain a valid session id.",
            status_code=response.status_code,
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

    def _extract_models(self, body: dict[str, Any]) -> list[dict[str, str]]:
        data = body.get("data")
        raw_models: Any

        if isinstance(data, dict) and "models" in data:
            raw_models = data.get("models")
        elif isinstance(data, (dict, list)):
            raw_models = data
        else:
            raise TaijiAPIError(
                "Taiji model list response format is unexpected (data is not dict/list)."
            )

        result = self._collect_model_entries(raw_models)
        if not result:
            raise TaijiAPIError("Taiji model list response does not contain label/value pairs.")

        deduped: list[dict[str, str]] = []
        seen_values: set[str] = set()
        for item in result:
            value = item["value"]
            if value in seen_values:
                continue
            seen_values.add(value)
            deduped.append(item)
        return deduped

    @classmethod
    def _collect_model_entries(cls, node: Any) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []

        if isinstance(node, list):
            for item in node:
                result.extend(cls._collect_model_entries(item))
            return result

        if isinstance(node, dict):
            label = node.get("label")
            value = node.get("value")
            if isinstance(label, str) and isinstance(value, str):
                result.append({"label": label, "value": value})
                return result

            for child in node.values():
                if isinstance(child, (list, dict)):
                    result.extend(cls._collect_model_entries(child))

        return result

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.lstrip("-").isdigit():
            return int(value)
        return None
