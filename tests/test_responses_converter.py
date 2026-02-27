from __future__ import annotations

from src.models.responses_request import ResponseRequest, ResponseInputItem
from src.utils.responses_converter import (
    response_request_to_chat_request,
    chat_response_to_response_object,
)


def test_convert_simple_request_to_chat() -> None:
    """测试将简单的 Responses 请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input="Hello, how are you?",
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.model == "gpt-4.1-mini"
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == "Hello, how are you?"
    assert chat_req.stream is False
    assert chat_req.temperature is None
    assert chat_req.max_tokens is None


def test_convert_request_with_instructions_to_chat() -> None:
    """测试将带指令的 Responses 请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        instructions="You are a helpful assistant.",
        input="Hello!",
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.model == "gpt-4.1-mini"
    assert len(chat_req.messages) == 2
    assert chat_req.messages[0].role == "system"
    assert chat_req.messages[0].content == "You are a helpful assistant."
    assert chat_req.messages[1].role == "user"
    assert chat_req.messages[1].content == "Hello!"


def test_convert_request_with_input_items_to_chat() -> None:
    """测试将带输入项列表的 Responses 请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input=[
            ResponseInputItem(type="text", text="First message"),
            ResponseInputItem(type="text", text="Second message"),
            ResponseInputItem(type="image", image_url="https://example.com/image.png"),
        ],
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.model == "gpt-4.1-mini"
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    # 应该合并两个文本项，忽略图像
    assert chat_req.messages[0].content == "First message\nSecond message"


def test_convert_request_with_stream_enabled() -> None:
    """测试将流式请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input="Hello",
        stream=True,
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.stream is True


def test_convert_request_with_temperature() -> None:
    """测试将带温度参数的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input="Hello",
        temperature=0.8,
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.temperature == 0.8


def test_convert_request_with_max_tokens() -> None:
    """测试将带最大令牌数的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input="Hello",
        max_tokens=500,
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.max_tokens == 500


def test_convert_chat_response_to_response_object() -> None:
    """测试将 Chat Completions 响应转换为 Responses 响应"""
    chat_resp = {
        "id": "chatcmpl-abc123xyz",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4.1-mini",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 9,
            "total_tokens": 19,
        },
    }

    resp = chat_response_to_response_object("gpt-4.1-mini", chat_resp)

    assert resp["id"] == "resp-abc123xyz"
    assert resp["object"] == "response"
    assert resp["created"] == 1234567890
    assert resp["model"] == "gpt-4.1-mini"
    assert resp["status"] == "completed"
    assert len(resp["output"]) == 1
    assert resp["output"][0]["type"] == "text"
    assert resp["output"][0]["text"] == "Hello! How can I help you today?"
    assert resp["usage"]["prompt_tokens"] == 10
    assert resp["usage"]["completion_tokens"] == 9
    assert resp["usage"]["total_tokens"] == 19


def test_convert_empty_chat_response() -> None:
    """测试转换空的 Chat Completions 响应"""
    chat_resp = {
        "id": "chatcmpl-empty",
        "object": "chat.completion",
        "created": 1234567890,
        "choices": [],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 0,
            "total_tokens": 5,
        },
    }

    resp = chat_response_to_response_object("gpt-4.1-mini", chat_resp)

    assert resp["id"] == "resp-empty"
    assert resp["status"] == "completed"
    assert len(resp["output"]) == 0


def test_convert_request_with_empty_string_input() -> None:
    """测试将空字符串输入的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input="",
    )

    chat_req = response_request_to_chat_request(req)

    # 空字符串输入仍会生成一个 user 消息
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == ""


def test_convert_request_with_empty_input_items() -> None:
    """测试将空输入项列表的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input=[],
    )

    chat_req = response_request_to_chat_request(req)

    # 空列表会生成一个空用户消息，以满足 ChatCompletionRequest 的要求
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == ""


def test_convert_request_with_only_image_input_items() -> None:
    """测试将只有图像输入项的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        input=[
            ResponseInputItem(type="image", image_url="https://example.com/image.png"),
        ],
    )

    chat_req = response_request_to_chat_request(req)

    # 只有图像项会被跳过，会生成一个空用户消息以满足 ChatCompletionRequest 的要求
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == ""


def test_convert_request_with_instructions_only() -> None:
    """测试将只有指令的请求转换为 Chat Completions 请求"""
    req = ResponseRequest(
        model="gpt-4.1-mini",
        instructions="You are a helpful assistant.",
    )

    chat_req = response_request_to_chat_request(req)

    # 有指令时会添加系统消息和空用户消息
    assert len(chat_req.messages) == 2
    assert chat_req.messages[0].role == "system"
    assert chat_req.messages[0].content == "You are a helpful assistant."
    assert chat_req.messages[1].role == "user"
    assert chat_req.messages[1].content == ""


def test_convert_chat_response_with_null_content() -> None:
    """测试转换内容为空的 Chat Completions 响应"""
    chat_resp = {
        "id": "chatcmpl-null",
        "object": "chat.completion",
        "created": 1234567890,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                },
            }
        ],
        "usage": {
            "prompt_tokens": 5,
            "completion_tokens": 0,
            "total_tokens": 5,
        },
    }

    resp = chat_response_to_response_object("gpt-4.1-mini", chat_resp)

    # None 内容应该被当作空字符串处理
    assert len(resp["output"]) == 0
