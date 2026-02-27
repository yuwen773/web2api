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
            # 兼容 ResponseInputItem 对象和字典格式
            if isinstance(item, dict):
                item_type = item.get("type")
                item_text = item.get("text")
                item_image_url = item.get("image_url")
            else:
                item_type = getattr(item, "type", None)
                item_text = getattr(item, "text", None)
                item_image_url = getattr(item, "image_url", None)

            if item_type == "text" and item_text:
                text_parts.append(item_text)
            elif item_type == "image" and item_image_url:
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
    """将 Chat Completions 响应转换为 Codex Responses API 响应格式

    Codex 期望的格式:
    - created_at (不是 created)
    - output 是 message 数组，每个 message 有 content 数组
    - content 使用 output_text 类型
    """
    content = ""
    if chat_resp.get("choices") and len(chat_resp["choices"]) > 0:
        message = chat_resp["choices"][0].get("message", {})
        content = message.get("content") or ""

    usage = chat_resp.get("usage", {})
    resp_id = chat_resp.get("id", "")
    created = chat_resp.get("created", 0)

    # 生成 message ID
    import uuid
    msg_id = f"msg_{uuid.uuid4().hex}"

    output = []
    if content:
        output.append({
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": content,
                    "annotations": []
                }
            ]
        })

    return {
        "id": f"resp-{resp_id.replace('chatcmpl-', '')}",
        "object": "response",
        "created_at": created,
        "model": model,
        "status": "completed",
        "output": output,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
        "error": None,
        "incomplete_details": None,
        "metadata": {}
    }
