from __future__ import annotations

from src.models.responses_request import (
    ResponseRequest,
    ResponseInputItem,
)
from src.models.openai_request import ChatCompletionRequest, ChatMessage
from typing import Any


def response_request_to_chat_request(req: ResponseRequest) -> ChatCompletionRequest:
    """将 Responses 请求转换为 Chat Completions 请求

    转换映射:
    - input (string) -> messages[0].content
    - input ({"str": "..."}) -> messages[0].content  (Codex 兼容)
    - input ([{"type": "text", "text": "..."}]) -> messages[0].content
    - instructions -> messages[0].role="system"
    - temperature -> temperature
    - max_tokens -> max_tokens
    - stream -> stream
    """
    messages: list[ChatMessage] = []

    # 添加系统消息（如果有）
    if req.instructions:
        messages.append(ChatMessage(role="system", content=req.instructions))

    # 处理 input
    if isinstance(req.input, str):
        messages.append(ChatMessage(role="user", content=req.input))
    elif isinstance(req.input, dict):
        # Codex 兼容格式: {"str": "hello"}
        if "str" in req.input and isinstance(req.input["str"], str):
            messages.append(ChatMessage(role="user", content=req.input["str"]))
        else:
            messages.append(ChatMessage(role="user", content=""))
    elif isinstance(req.input, list):
        # 合并所有文本输入项
        text_parts = []
        for item in req.input:
            if item.type == "text" and item.text:
                text_parts.append(item.text)
            elif item.type == "image" and item.image_url:
                # 图像暂不支持，跳过
                pass
        if text_parts:
            messages.append(ChatMessage(role="user", content="\n".join(text_parts)))
    else:
        # 默认情况：添加空用户消息
        messages.append(ChatMessage(role="user", content=""))

    # 确保至少有一条消息
    if not messages:
        messages.append(ChatMessage(role="user", content=""))

    return ChatCompletionRequest(
        model=req.model,
        messages=messages,
        stream=req.stream,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
    )


def chat_response_to_response_object(
    model: str,
    chat_resp: dict[str, Any],
) -> dict[str, Any]:
    """将 Chat Completions 响应转换为 Responses 响应

    转换映射:
    - choices[0].message.content -> output[0].text
    - 新增 status="completed"
    - object 从 "chat.completion" 改为 "response"
    """
    content = ""
    if chat_resp.get("choices") and len(chat_resp["choices"]) > 0:
        message = chat_resp["choices"][0].get("message", {})
        content = message.get("content") or ""

    usage = chat_resp.get("usage", {})

    output = []
    if content:
        output.append({
            "type": "text",
            "text": content
        })

    return {
        "id": f"resp-{chat_resp['id'].replace('chatcmpl-', '')}",
        "object": "response",
        "created": chat_resp.get("created", 0),
        "model": model,
        "status": "completed",
        "output": output,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }
