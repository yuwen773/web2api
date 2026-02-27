from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.client.taiji_client import TaijiAPIError
from src.models.anthropic_request import AnthropicContentBlock, AnthropicRequest
from src.utils.message_converter import convert_openai_messages


logger = logging.getLogger(__name__)

router = APIRouter(tags=["anthropic"])


@router.post("/v1/messages", response_model=None)
async def create_message(
    request_body: AnthropicRequest,
    request: Request,
) -> Any:
    taiji_client = _get_taiji_client(request)
    if request_body.stream:
        return await _messages_stream(request_body, taiji_client)
    return await _messages_non_stream(request_body, taiji_client)


async def _messages_non_stream(
    request_body: AnthropicRequest,
    taiji_client: Any,
) -> dict[str, Any]:
    session_id = await _create_session_or_raise(taiji_client, request_body.model)

    try:
        prompt_text, files = await _build_prompt_payload(request_body)
        taiji_response = await taiji_client.send_message(
            session_id=session_id,
            text=prompt_text,
            files=files,
            stream=False,
        )
    except TaijiAPIError as exc:
        raise _http_exception_from_taiji_error(exc) from exc
    finally:
        await _safe_delete_session(taiji_client, session_id)

    return _build_anthropic_response(request_body.model, taiji_response)


async def _messages_stream(
    request_body: AnthropicRequest,
    taiji_client: Any,
) -> StreamingResponse:
    session_id = await _create_session_or_raise(taiji_client, request_body.model)

    try:
        prompt_text, files = await _build_prompt_payload(request_body)
        stream = taiji_client.send_message(
            session_id=session_id,
            text=prompt_text,
            files=files,
            stream=True,
        )
        first_chunk = await anext(stream)
    except StopAsyncIteration:
        await _safe_delete_session(taiji_client, session_id)
        raise HTTPException(
            status_code=502,
            detail="Taiji stream ended before any chunk was returned.",
        ) from None
    except TaijiAPIError as exc:
        await _safe_delete_session(taiji_client, session_id)
        raise _http_exception_from_taiji_error(exc) from exc
    except HTTPException:
        await _safe_delete_session(taiji_client, session_id)
        raise

    if _is_error_chunk(first_chunk):
        await _safe_delete_session(taiji_client, session_id)
        raise HTTPException(
            status_code=400,
            detail=f"Taiji error: {first_chunk.get('msg') or 'unknown error'}",
        )

    message_id = f"msg_{uuid4().hex}"

    async def stream_generator() -> AsyncIterator[str]:
        summary_data: dict[str, Any] | None = None

        try:
            yield _format_sse_event(
                "message_start",
                {
                    "type": "message_start",
                    "message": {
                        "id": message_id,
                        "type": "message",
                        "role": "assistant",
                        "content": [],
                        "model": request_body.model,
                        "stop_reason": None,
                        "stop_sequence": None,
                        "usage": {"input_tokens": 0, "output_tokens": 0},
                    },
                },
            )
            yield _format_sse_event(
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": 0,
                    "content_block": {"type": "text", "text": ""},
                },
            )

            for chunk in (first_chunk,):
                text, maybe_summary = _parse_stream_chunk(chunk)
                if text:
                    yield _format_sse_event(
                        "content_block_delta",
                        {
                            "type": "content_block_delta",
                            "index": 0,
                            "delta": {"type": "text_delta", "text": text},
                        },
                    )
                if maybe_summary is not None:
                    summary_data = maybe_summary

            async for chunk in stream:
                text, maybe_summary = _parse_stream_chunk(chunk)
                if text:
                    yield _format_sse_event(
                        "content_block_delta",
                        {
                            "type": "content_block_delta",
                            "index": 0,
                            "delta": {"type": "text_delta", "text": text},
                        },
                    )
                if maybe_summary is not None:
                    summary_data = maybe_summary

            yield _format_sse_event(
                "content_block_stop",
                {"type": "content_block_stop", "index": 0},
            )

            yield _format_sse_event(
                "message_delta",
                {
                    "type": "message_delta",
                    "delta": {
                        "stop_reason": "end_turn",
                        "stop_sequence": None,
                    },
                    "usage": {
                        "output_tokens": _to_int(
                            (summary_data or {}).get("completionTokens")
                        )
                        or 0
                    },
                },
            )

            yield _format_sse_event("message_stop", {"type": "message_stop"})
        except asyncio.CancelledError:
            logger.info("Client disconnected during Anthropic streaming response.")
            raise
        finally:
            await _safe_delete_session(taiji_client, session_id)

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _get_taiji_client(request: Request) -> Any:
    taiji_client = getattr(request.app.state, "taiji_client", None)
    if taiji_client is None:
        raise HTTPException(status_code=503, detail="Taiji client is not initialized.")
    return taiji_client


def _http_exception_from_taiji_error(error: TaijiAPIError) -> HTTPException:
    status_code = error.status_code or 502
    if status_code < 400 or status_code > 599:
        status_code = 502
    message = str(error) or "Taiji upstream request failed."
    return HTTPException(status_code=status_code, detail=message)


async def _create_session_or_raise(taiji_client: Any, model: str) -> int:
    try:
        return await taiji_client.create_session(model)
    except TaijiAPIError as exc:
        raise _http_exception_from_taiji_error(exc) from exc


async def _build_prompt_payload(
    request_body: AnthropicRequest,
) -> tuple[str, list[dict[str, str]]]:
    openai_messages = _to_openai_messages(request_body)
    try:
        converted = await convert_openai_messages(
            messages=openai_messages,
            model=request_body.model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = converted.get("text")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Converted prompt text is invalid.")

    return text, _normalize_files(converted.get("files"))


def _to_openai_messages(request_body: AnthropicRequest) -> list[dict[str, object]]:
    messages: list[dict[str, object]] = []

    if request_body.system is not None:
        system_content = _normalize_anthropic_content(request_body.system)
        messages.append({"role": "system", "content": system_content})

    for message in request_body.messages:
        role = message.role.strip().lower() or "user"
        content = _normalize_anthropic_content(message.content)
        messages.append({"role": role, "content": content})

    return messages


def _normalize_anthropic_content(
    content: str | list[AnthropicContentBlock],
) -> str | list[dict[str, Any]]:
    if isinstance(content, str):
        return content.strip()

    parts: list[dict[str, Any]] = []
    for block in content:
        block_type = block.type.strip().lower()
        if block_type == "text":
            text = (block.text or "").strip()
            if text:
                parts.append({"type": "text", "text": text})
            continue

        if block_type == "image":
            image_url = _block_to_image_url(block)
            if image_url:
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    }
                )
            continue

        if block_type == "image_url":
            image_url = _coerce_image_url(block.image_url)
            if image_url:
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    }
                )

    if not parts:
        return ""
    return parts


def _block_to_image_url(block: AnthropicContentBlock) -> str | None:
    if block.source is None:
        return _coerce_image_url(block.image_url)

    source_type = block.source.type.strip().lower()
    if source_type == "base64":
        data = (block.source.data or "").strip()
        if not data:
            raise HTTPException(status_code=400, detail="Anthropic image block is missing base64 data.")

        media_type = (block.source.media_type or "image/png").strip().lower()
        if data.startswith("data:image/"):
            return data
        return f"data:{media_type};base64,{data}"

    if source_type in {"url", "image_url"}:
        url = (block.source.url or "").strip()
        if not url:
            raise HTTPException(status_code=400, detail="Anthropic image block is missing url.")
        return url

    if block.source.url:
        return block.source.url.strip()

    return None


def _coerce_image_url(value: object) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None

    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str):
            stripped = url.strip()
            return stripped or None

    return None


def _normalize_files(raw_files: object) -> list[dict[str, str]]:
    if not isinstance(raw_files, list):
        return []

    normalized: list[dict[str, str]] = []
    for item in raw_files:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        data = item.get("data")
        if isinstance(name, str) and isinstance(data, str):
            normalized.append({"name": name, "data": data})
    return normalized


def _build_anthropic_response(model: str, taiji_response: dict[str, Any]) -> dict[str, Any]:
    prompt_tokens = _to_int(taiji_response.get("promptTokens")) or 0
    completion_tokens = _to_int(taiji_response.get("completionTokens")) or 0
    text = str(taiji_response.get("text") or "")

    return {
        "id": f"msg_{uuid4().hex}",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": model,
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
        },
    }


def _parse_stream_chunk(chunk: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    if _is_error_chunk(chunk):
        raise TaijiAPIError(
            str(chunk.get("msg") or "Taiji stream returned an error chunk."),
            code=_to_int(chunk.get("code")),
            status_code=400,
        )

    chunk_type = chunk.get("type")
    if chunk_type == "string":
        text = str(chunk.get("data") or "")
        return (text if text else None, None)

    if chunk_type == "object" and isinstance(chunk.get("data"), dict):
        return (None, chunk["data"])

    return (None, None)


def _format_sse_event(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _is_error_chunk(chunk: dict[str, Any]) -> bool:
    code = _to_int(chunk.get("code"))
    return code is not None and code != 0


def _to_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.lstrip("-").isdigit():
        return int(value)
    return None


async def _safe_delete_session(taiji_client: Any, session_id: int) -> None:
    try:
        await taiji_client.delete_session(session_id)
    except TaijiAPIError as exc:
        logger.warning("Failed to delete Taiji session %s: %s", session_id, exc)
