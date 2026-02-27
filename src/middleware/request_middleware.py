from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.client.taiji_client import TaijiAPIError
from src.utils.request_context import reset_request_id, set_request_id


logger = logging.getLogger(__name__)

ERROR_CODE_MAP: dict[int, str] = {
    400: "bad_request",
    401: "auth_failed",
    429: "rate_limit_exceeded",
    500: "internal_server_error",
}


class RequestContextAndErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _resolve_request_id(request)
        request.state.request_id = request_id
        token = set_request_id(request_id)
        started_at = time.perf_counter()
        response: Response | None = None
        status_code = 500

        logger.info("API request started: %s %s", request.method, request.url.path)

        try:
            response = await call_next(request)
            if response.status_code >= 400:
                status_code = _map_status_code(response.status_code)
                message = await _extract_response_message(
                    response,
                    fallback=_default_message(status_code),
                )
                logger.error(
                    "HTTP error response: status=%s mapped_status=%s message=%s",
                    response.status_code,
                    status_code,
                    message,
                )
                response = _build_error_response(
                    status_code=status_code,
                    message=message,
                    request_id=request_id,
                )
            else:
                status_code = response.status_code
        except asyncio.CancelledError:
            logger.info("Client disconnected before response completed.")
            raise
        except RequestValidationError as exc:
            status_code = 400
            message = _build_validation_error_message(exc)
            logger.error("Request validation failed: %s", message)
            response = _build_error_response(status_code=status_code, message=message, request_id=request_id)
        except TaijiAPIError as exc:
            status_code = _map_status_code(exc.status_code)
            message = str(exc) or _default_message(status_code)
            logger.error("Taiji upstream error: status=%s message=%s", status_code, message)
            response = _build_error_response(status_code=status_code, message=message, request_id=request_id)
        except HTTPException as exc:
            status_code = _map_status_code(exc.status_code)
            message = _extract_message(exc.detail, fallback=_default_message(status_code))
            logger.error("HTTP exception: status=%s message=%s", status_code, message)
            response = _build_error_response(status_code=status_code, message=message, request_id=request_id)
        except Exception:
            status_code = 500
            logger.exception("Unhandled server exception.")
            response = _build_error_response(
                status_code=status_code,
                message=_default_message(status_code),
                request_id=request_id,
            )
        finally:
            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.info(
                "API request finished: %s %s -> %s (%.2f ms)",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )
            reset_request_id(token)

        if response is not None:
            response.headers["X-Request-ID"] = request_id
            return response

        fallback_response = _build_error_response(
            status_code=500,
            message=_default_message(500),
            request_id=request_id,
        )
        fallback_response.headers["X-Request-ID"] = request_id
        return fallback_response


def _resolve_request_id(request: Request) -> str:
    raw_request_id = request.headers.get("x-request-id")
    if raw_request_id is not None:
        normalized = raw_request_id.strip()
        if normalized:
            return normalized
    return uuid4().hex


def _map_status_code(status_code: int | None) -> int:
    if status_code in {400, 401, 429}:
        return status_code
    if status_code == 422:
        return 400
    if status_code is not None and status_code >= 500:
        return 500
    if status_code is None:
        return 500
    return status_code


def _build_validation_error_message(error: RequestValidationError) -> str:
    errors = error.errors()
    if not errors:
        return _default_message(400)

    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.get("loc", ()))
    message = str(first_error.get("msg") or "Invalid request parameter.")
    if location:
        return f"{location}: {message}"
    return message


def _extract_message(detail: Any, *, fallback: str) -> str:
    if isinstance(detail, str):
        normalized = detail.strip()
        return normalized or fallback

    if isinstance(detail, dict):
        for key in ("message", "detail", "msg"):
            value = detail.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, str):
            normalized = first.strip()
            if normalized:
                return normalized
        if isinstance(first, dict):
            if "loc" in first or "msg" in first:
                return _extract_validation_error_message(first, fallback=fallback)
            for key in ("msg", "message", "detail"):
                value = first.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

    return fallback


async def _extract_response_message(response: Response, *, fallback: str) -> str:
    body = await _read_response_body(response)
    if not body:
        return fallback

    text = body.decode("utf-8", errors="ignore").strip()
    if not text:
        return fallback

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text

    if isinstance(parsed, dict):
        if "detail" in parsed:
            return _extract_message(parsed["detail"], fallback=fallback)
        return _extract_message(parsed, fallback=fallback)

    return _extract_message(parsed, fallback=fallback)


async def _read_response_body(response: Response) -> bytes:
    body = getattr(response, "body", None)
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)

    chunks: list[bytes] = []
    async for chunk in response.body_iterator:
        if isinstance(chunk, str):
            chunks.append(chunk.encode("utf-8"))
        else:
            chunks.append(chunk)
    return b"".join(chunks)


def _extract_validation_error_message(error_item: dict[str, Any], *, fallback: str) -> str:
    location = ".".join(str(part) for part in error_item.get("loc", ()))
    message = str(error_item.get("msg") or fallback)
    if location:
        return f"{location}: {message}"
    return message


def _default_message(status_code: int) -> str:
    if status_code == 401:
        return "Authentication failed."
    if status_code == 429:
        return "Too many requests."
    if status_code == 400:
        return "Bad request."
    return "Internal server error."


def _build_error_response(*, status_code: int, message: str, request_id: str) -> JSONResponse:
    error_code = ERROR_CODE_MAP.get(status_code, f"http_{status_code}")
    payload = {
        "error": {
            "code": error_code,
            "message": message,
            "status": status_code,
            "request_id": request_id,
        },
        "detail": message,
    }
    return JSONResponse(status_code=status_code, content=payload)
