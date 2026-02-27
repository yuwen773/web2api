from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.client.taiji_client import TaijiAPIError
from src.models.openai_request import ChatCompletionRequest
from src.models.responses_request import ResponseRequest
from src.utils.message_converter import convert_openai_messages
from src.utils.responses_converter import (
    response_request_to_chat_request,
    chat_response_to_response_object,
)


logger = logging.getLogger(__name__)

router = APIRouter(tags=["openai"])


@router.post("/v1/chat/completions", response_model=None)
async def chat_completions(
    request_body: ChatCompletionRequest,
    request: Request,
) -> Any:
    taiji_client = _get_taiji_client(request)
    if request_body.stream:
        return await _chat_completions_stream(request_body, taiji_client)
    return await _chat_completions_non_stream(request_body, taiji_client)


@router.get("/v1/models")
async def list_models(request: Request) -> dict[str, Any]:
    taiji_client = _get_taiji_client(request)
    try:
        models = await taiji_client.get_models()
    except TaijiAPIError as exc:
        raise _http_exception_from_taiji_error(exc) from exc

    created = int(time.time())
    data: list[dict[str, Any]] = []
    for model_entry in models:
        if not isinstance(model_entry, dict):
            continue
        model_id = str(model_entry.get("value") or "").strip()
        if not model_id:
            continue
        data.append(
            {
                "id": model_id,
                "object": "model",
                "created": created,
                "owned_by": "taiji",
            }
        )

    return {
        "object": "list",
        "data": data,
    }


async def _chat_completions_non_stream(
    request_body: ChatCompletionRequest,
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

    return _build_chat_completion_response(request_body.model, taiji_response)


async def _chat_completions_stream(
    request_body: ChatCompletionRequest,
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
            detail=f"太极AI错误: {first_chunk.get('msg') or 'unknown error'}",
        )

    completion_id = f"chatcmpl-{uuid4().hex}"
    created = int(time.time())

    async def stream_generator() -> AsyncIterator[str]:
        try:
            # Start with an assistant role delta for better OpenAI SDK compatibility.
            yield _format_sse(
                _build_chat_completion_chunk(
                    completion_id=completion_id,
                    created=created,
                    model=request_body.model,
                    delta={"role": "assistant"},
                    finish_reason=None,
                )
            )

            for chunk in (first_chunk,):
                payload = _chunk_to_openai_payload(
                    chunk=chunk,
                    completion_id=completion_id,
                    created=created,
                    model=request_body.model,
                )
                if payload is not None:
                    yield _format_sse(payload)

            async for chunk in stream:
                if _is_error_chunk(chunk):
                    raise TaijiAPIError(
                        str(chunk.get("msg") or "Taiji stream returned an error chunk."),
                        code=_to_int(chunk.get("code")),
                        status_code=400,
                    )
                payload = _chunk_to_openai_payload(
                    chunk=chunk,
                    completion_id=completion_id,
                    created=created,
                    model=request_body.model,
                )
                if payload is not None:
                    yield _format_sse(payload)

            yield _format_sse(
                _build_chat_completion_chunk(
                    completion_id=completion_id,
                    created=created,
                    model=request_body.model,
                    delta={},
                    finish_reason="stop",
                )
            )
            yield "data: [DONE]\n\n"
        except asyncio.CancelledError:
            logger.info("Client disconnected during OpenAI streaming response.")
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


async def _build_prompt_payload(request_body: ChatCompletionRequest) -> tuple[str, list[dict[str, str]]]:
    try:
        converted = await convert_openai_messages(
            messages=[message.model_dump(mode="python") for message in request_body.messages],
            model=request_body.model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = converted.get("text")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Converted prompt text is invalid.")

    return text, _normalize_files(converted.get("files"))


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


def _build_chat_completion_response(model: str, taiji_response: dict[str, Any]) -> dict[str, Any]:
    prompt_tokens = _to_int(taiji_response.get("promptTokens")) or 0
    completion_tokens = _to_int(taiji_response.get("completionTokens")) or 0
    total_tokens = _to_int(taiji_response.get("useTokens")) or 0
    content = str(taiji_response.get("text") or "")

    return {
        "id": f"chatcmpl-{uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
    }


def _chunk_to_openai_payload(
    *,
    chunk: dict[str, Any],
    completion_id: str,
    created: int,
    model: str,
) -> dict[str, Any] | None:
    if _is_error_chunk(chunk):
        raise TaijiAPIError(
            str(chunk.get("msg") or "Taiji stream returned an error chunk."),
            code=_to_int(chunk.get("code")),
            status_code=400,
        )

    if chunk.get("type") != "string":
        return None

    content = chunk.get("data")
    if content is None:
        return None

    text = str(content)
    if not text:
        return None

    return _build_chat_completion_chunk(
        completion_id=completion_id,
        created=created,
        model=model,
        delta={"content": text},
        finish_reason=None,
    )


def _build_chat_completion_chunk(
    *,
    completion_id: str,
    created: int,
    model: str,
    delta: dict[str, str],
    finish_reason: str | None,
) -> dict[str, Any]:
    return {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "finish_reason": finish_reason,
            }
        ],
    }


def _format_sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


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


@router.post("/v1/responses", response_model=None)
async def responses_create(
    request_body: ResponseRequest,
    request: Request,
) -> Any:
    """OpenAI Responses API 兼容端点

    将 Responses 格式请求转换为 Chat Completions 格式，
    复用现有 Taiji 客户端调用逻辑。
    """
    # 调试日志：打印原始请求体
    import json
    body = await request.body()
    logger.info("=== /v1/responses DEBUG ===")
    logger.info("Raw body: %s", body.decode("utf-8"))
    logger.info("Parsed input type: %s", type(request_body.input))
    logger.info("Parsed input value: %s", request_body.input)
    logger.info("==========================")

    taiji_client = _get_taiji_client(request)

    # 转换为 Chat Completions 格式
    chat_request = response_request_to_chat_request(request_body)

    if request_body.stream:
        return await _responses_stream(
            chat_request, taiji_client, request_body.model
        )
    return await _responses_non_stream(
        chat_request, taiji_client, request_body.model
    )


async def _responses_non_stream(
    chat_request: ChatCompletionRequest,
    taiji_client: Any,
    model: str,
) -> dict[str, Any]:
    """Responses 非流式响应处理"""
    chat_response = await _chat_completions_non_stream(chat_request, taiji_client)
    return chat_response_to_response_object(model, chat_response)


async def _responses_stream(
    chat_request: ChatCompletionRequest,
    taiji_client: Any,
    model: str,
) -> StreamingResponse:
    """Responses 流式响应处理

    复用现有 Chat Completions 流式逻辑，
    将 SSE 事件转换为 Responses 格式。
    """
    session_id = await _create_session_or_raise(taiji_client, chat_request.model)

    try:
        prompt_text, files = await _build_prompt_payload(chat_request)
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
            detail=f"太极AI错误: {first_chunk.get('msg') or 'unknown error'}",
        )

    response_id = f"resp-{uuid4().hex}"
    message_id = f"msg_{uuid4().hex}"
    created = int(time.time())

    # 收集所有文本内容
    collected_text = []

    async def stream_generator() -> AsyncIterator[str]:
        try:
            # 1. 发送 response.created 事件
            yield _format_sse({
                "type": "response.created",
                "response": {
                    "id": response_id,
                }
            })

            # 2. 收集所有文本块
            # 处理第一个 chunk
            for chunk in (first_chunk,):
                if chunk.get("type") == "string":
                    text = str(chunk.get("data") or "")
                    if text:
                        collected_text.append(text)

            # 处理后续 chunks
            async for chunk in stream:
                if _is_error_chunk(chunk):
                    raise TaijiAPIError(
                        str(chunk.get("msg") or "Taiji stream returned an error chunk."),
                        code=_to_int(chunk.get("code")),
                        status_code=400,
                    )
                if chunk.get("type") == "string":
                    text = str(chunk.get("data") or "")
                    if text:
                        collected_text.append(text)

            # 3. 获取 token 使用情况（从最后一个 object 类型的 chunk）
            # Taiji 最后会发送一个 object 类型的 chunk 包含 token 信息
            # 但由于我们已经流式处理了，这里使用估算值
            full_text = "".join(collected_text)
            input_tokens = len(chat_request.messages[0].content) if chat_request.messages else 0
            output_tokens = len(full_text)
            total_tokens = input_tokens + output_tokens

            # 4. 发送 response.output_item.done 事件（包含完整消息）
            yield _format_sse({
                "type": "response.output_item.done",
                "item": {
                    "type": "message",
                    "role": "assistant",
                    "id": message_id,
                    "content": [
                        {
                            "type": "output_text",
                            "text": full_text,
                        }
                    ],
                }
            })

            # 5. 发送 response.completed 事件（包含 usage）
            yield _format_sse({
                "type": "response.completed",
                "response": {
                    "id": response_id,
                    "usage": {
                        "input_tokens": input_tokens,
                        "input_tokens_details": None,
                        "output_tokens": output_tokens,
                        "output_tokens_details": None,
                        "total_tokens": total_tokens,
                    },
                }
            })
        except asyncio.CancelledError:
            logger.info("Client disconnected during Responses streaming.")
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


