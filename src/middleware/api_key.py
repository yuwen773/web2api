from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.utils.settings import get_settings
from src.utils.logging_config import get_logger


logger = get_logger(__name__)


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key 鉴权中间件"""

    EXEMPT_PATHS = {"/metrics", "/stats", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # 豁免路径
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        settings = get_settings()
        api_keys = settings.api_keys

        # 空列表 = 不启用鉴权
        if not api_keys:
            return await call_next(request)

        # 获取请求头中的 API Key
        provided_key = request.headers.get("x-api-key")
        if not provided_key:
            logger.warning("api_key_missing", path=request.url.path)
            return _unauthorized_response(request, "Missing API key.")

        if provided_key not in api_keys:
            logger.warning("api_key_invalid", path=request.url.path)
            return _unauthorized_response(request, "Invalid API key.")

        return await call_next(request)


def _unauthorized_response(request: Request, message: str) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    return JSONResponse(
        status_code=401,
        content={
            "error": {
                "code": "auth_failed",
                "message": message,
                "status": 401,
                "request_id": request_id,
            },
            "detail": message,
        },
        headers={"WWW-Authenticate": "ApiKey"},
    )
