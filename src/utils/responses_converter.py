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
    - input ([ResponseInputItem, ...]) -> 合并文本内容（旧格式）
    - input ([message, ...]) -> 提取最后的用户消息（Codex 消息格式）
    - instructions -> messages[0].role="system"（仅非 Codex 请求）
    - temperature -> temperature
    - max_tokens -> max_tokens
    - stream -> stream

    注意: Codex 请求的消息数组格式会被特殊处理：
    - 过滤掉 role="developer" 的系统消息
    - 只提取最后的用户消息内容
    - instructions 不发送给上游 API（Codex 本地使用）
    """
    messages: list[ChatMessage] = []

    # 判断是否为 Codex 消息数组格式
    # 通过检查是否有 role 字段来区分
    is_codex_message_format = False
    if isinstance(req.input, list) and len(req.input) > 0:
        first_item = req.input[0]
        if isinstance(first_item, dict):
            is_codex_message_format = "role" in first_item
        else:
            is_codex_message_format = hasattr(first_item, "role")

    # 添加系统消息（仅非 Codex 格式）
    if req.instructions and not is_codex_message_format:
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
        if is_codex_message_format:
            # 处理 Codex 消息数组格式
            # 过滤掉 developer 角色的系统消息，提取最后的用户消息
            last_user_message = ""

            for item in req.input:
                if isinstance(item, dict):
                    item_role = item.get("role")
                    item_content = item.get("content")
                else:
                    item_role = getattr(item, "role", None)
                    item_content = getattr(item, "content", None)

                # 跳过 developer 消息（Codex 内部使用的权限说明等）
                if item_role == "developer":
                    continue

                # 提取用户消息内容
                if item_role == "user" and isinstance(item_content, list):
                    # content 是数组格式: [{"type": "input_text", "text": "..."}]
                    for content_part in item_content:
                        if isinstance(content_part, dict):
                            text = content_part.get("text", "")
                            # 只取 input_text 类型的内容
                            if content_part.get("type") == "input_text" and text:
                                last_user_message = text
                                break
                        elif text:
                            last_user_message = str(text)
                            break

            if last_user_message:
                messages.append(ChatMessage(role="user", content=last_user_message))
            else:
                messages.append(ChatMessage(role="user", content=""))
        else:
            # 处理旧的 input_items 格式 (ResponseInputItem)
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
                messages.append(ChatMessage(role="user", content=""))
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
