from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.responses_request import (
    ResponseInputItem,
    ResponseRequest,
    ResponseTool,
)
from src.models.responses_response import (
    ResponseObject,
    ResponseOutputItem,
    ResponseUsage,
)


def test_response_request_minimal() -> None:
    """测试最小请求参数"""
    request = ResponseRequest(model="gpt-4.1-mini")
    assert request.model == "gpt-4.1-mini"
    assert request.input == ""
    assert request.instructions is None
    assert request.stream is False
    assert request.background is False
    assert request.tool_choice == "auto"


def test_response_request_with_instructions() -> None:
    """测试带指令的请求"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        instructions="You are a helpful assistant.",
    )
    assert request.model == "gpt-4.1-mini"
    assert request.instructions == "You are a helpful assistant."


def test_response_request_with_input_items() -> None:
    """测试带输入项列表的请求"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        input=[
            ResponseInputItem(type="text", text="Hello"),
            ResponseInputItem(type="image", image_url="https://example.com/image.png"),
        ],
    )
    assert request.model == "gpt-4.1-mini"
    assert len(request.input) == 2
    assert request.input[0].type == "text"
    assert request.input[0].text == "Hello"
    assert request.input[1].type == "image"
    assert request.input[1].image_url == "https://example.com/image.png"


def test_response_request_temperature_validation() -> None:
    """测试温度参数验证"""
    # 正常范围
    request = ResponseRequest(model="gpt-4.1-mini", temperature=1.0)
    assert request.temperature == 1.0

    # 边界值
    request = ResponseRequest(model="gpt-4.1-mini", temperature=0.0)
    assert request.temperature == 0.0

    request = ResponseRequest(model="gpt-4.1-mini", temperature=2.0)
    assert request.temperature == 2.0

    # 超出范围
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", temperature=-0.1)

    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", temperature=2.1)


def test_response_request_max_tokens_validation() -> None:
    """测试最大令牌数验证"""
    # 正常值
    request = ResponseRequest(model="gpt-4.1-mini", max_tokens=100)
    assert request.max_tokens == 100

    # 无效值
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", max_tokens=0)

    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", max_tokens=-1)


def test_response_input_item_text() -> None:
    """测试文本输入项"""
    item = ResponseInputItem(type="text", text="Hello, world!")
    assert item.type == "text"
    assert item.text == "Hello, world!"
    assert item.image_url is None


def test_response_input_item_image() -> None:
    """测试图像输入项"""
    item = ResponseInputItem(
        type="image",
        image_url="https://example.com/image.png",
    )
    assert item.type == "image"
    assert item.image_url == "https://example.com/image.png"
    assert item.text is None


def test_response_tool_function() -> None:
    """测试函数工具定义"""
    tool = ResponseTool(
        type="function",
        name="get_weather",
        description="Get the current weather",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
            },
        },
    )
    assert tool.type == "function"
    assert tool.name == "get_weather"
    assert tool.description == "Get the current weather"
    assert tool.parameters is not None
    assert tool.parameters["type"] == "object"


def test_response_tool_web_search() -> None:
    """测试网络搜索工具定义"""
    tool = ResponseTool(type="web_search")
    assert tool.type == "web_search"


def test_response_tool_file_search() -> None:
    """测试文件搜索工具定义"""
    tool = ResponseTool(type="file_search")
    assert tool.type == "file_search"


def test_response_request_extra_fields_forbidden() -> None:
    """测试禁止额外字段"""
    # ResponseInputItem
    with pytest.raises(ValidationError):
        ResponseInputItem(type="text", text="Hello", extra_field="not_allowed")

    # ResponseTool
    with pytest.raises(ValidationError):
        ResponseTool(type="function", name="test", extra_field="not_allowed")

    # ResponseRequest
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", unknown_field="not_allowed")


def test_response_request_top_p_validation() -> None:
    """测试 top_p 参数验证"""
    # 正常范围
    request = ResponseRequest(model="gpt-4.1-mini", top_p=0.5)
    assert request.top_p == 0.5

    # 边界值
    request = ResponseRequest(model="gpt-4.1-mini", top_p=0.0)
    assert request.top_p == 0.0

    request = ResponseRequest(model="gpt-4.1-mini", top_p=1.0)
    assert request.top_p == 1.0

    # 超出范围
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", top_p=-0.1)

    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4.1-mini", top_p=1.1)


def test_response_request_with_tools() -> None:
    """测试带工具列表的请求"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        tools=[
            ResponseTool(
                type="function",
                name="get_weather",
                description="Get weather",
            ),
            ResponseTool(type="web_search"),
        ],
    )
    assert len(request.tools) == 2
    assert request.tools[0].name == "get_weather"
    assert request.tools[1].type == "web_search"


def test_response_request_with_reasoning() -> None:
    """测试带推理参数的请求"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        reasoning={"max_tokens": 1000},
    )
    assert request.reasoning is not None
    assert request.reasoning["max_tokens"] == 1000


def test_response_request_with_previous_response_id() -> None:
    """测试带先前响应ID的请求"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        previous_response_id="resp_123",
    )
    assert request.previous_response_id == "resp_123"


def test_response_request_stream_and_background() -> None:
    """测试流式和后台模式"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        stream=True,
        background=True,
    )
    assert request.stream is True
    assert request.background is True


def test_response_request_tool_choice_variants() -> None:
    """测试工具选择的不同形式"""
    # 字符串形式
    request = ResponseRequest(
        model="gpt-4.1-mini",
        tool_choice="auto",
    )
    assert request.tool_choice == "auto"

    # 字典形式
    request = ResponseRequest(
        model="gpt-4.1-mini",
        tool_choice={"type": "function", "name": "get_weather"},
    )
    assert isinstance(request.tool_choice, dict)
    assert request.tool_choice["name"] == "get_weather"


def test_response_input_item_invalid_type() -> None:
    """测试无效的输入项类型"""
    with pytest.raises(ValidationError):
        ResponseInputItem(type="invalid", text="Hello")


def test_response_tool_invalid_type() -> None:
    """测试无效的工具类型"""
    with pytest.raises(ValidationError):
        ResponseTool(type="invalid_tool")


def test_response_request_instructions_max_length() -> None:
    """测试指令最大长度限制"""
    # 正常长度
    long_instructions = "a" * 8000
    request = ResponseRequest(
        model="gpt-4.1-mini",
        instructions=long_instructions,
    )
    assert len(request.instructions) == 8000

    # 超出最大长度
    with pytest.raises(ValidationError):
        ResponseRequest(
            model="gpt-4.1-mini",
            instructions="a" * 8001,
        )


def test_response_request_model_min_length() -> None:
    """测试模型名称最小长度"""
    # 正常
    request = ResponseRequest(model="gpt-4.1-mini")
    assert request.model == "gpt-4.1-mini"

    # 空字符串
    with pytest.raises(ValidationError):
        ResponseRequest(model="")


def test_response_request_with_string_input() -> None:
    """测试字符串形式的输入"""
    request = ResponseRequest(
        model="gpt-4.1-mini",
        input="Hello, how are you?",
    )
    assert request.input == "Hello, how are you?"


def test_response_usage() -> None:
    """测试使用量统计模型"""
    usage = ResponseUsage(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
    )
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30


def test_response_output_item_text() -> None:
    """测试文本输出项"""
    item = ResponseOutputItem(type="text", text="Hello, world!")
    assert item.type == "text"
    assert item.text == "Hello, world!"
    assert item.tool_use_id is None
    assert item.name is None
    assert item.arguments is None


def test_response_output_item_tool_call() -> None:
    """测试工具调用输出项"""
    item = ResponseOutputItem(
        type="tool_call",
        tool_use_id="call_123",
        name="get_weather",
        arguments='{"location": "New York"}',
    )
    assert item.type == "tool_call"
    assert item.tool_use_id == "call_123"
    assert item.name == "get_weather"
    assert item.arguments == '{"location": "New York"}'
    assert item.text is None


def test_response_object_completed() -> None:
    """测试完成的响应对象"""
    response = ResponseObject(
        id="resp_abc123",
        created=1234567890,
        model="gpt-4.1-mini",
        status="completed",
        output=[
            ResponseOutputItem(type="text", text="Hello!"),
        ],
        usage=ResponseUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        ),
    )
    assert response.id == "resp_abc123"
    assert response.object == "response"
    assert response.created == 1234567890
    assert response.model == "gpt-4.1-mini"
    assert response.status == "completed"
    assert len(response.output) == 1
    assert response.output[0].text == "Hello!"
    assert response.usage.total_tokens == 15
    assert response.error is None


def test_response_object_failed() -> None:
    """测试失败的响应对象"""
    response = ResponseObject(
        id="resp_error",
        created=1234567890,
        model="gpt-4.1-mini",
        status="failed",
        output=[],
        usage=ResponseUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        ),
        error={"message": "Internal server error", "code": "server_error"},
    )
    assert response.status == "failed"
    assert response.error is not None
    assert response.error["message"] == "Internal server error"
    assert response.error["code"] == "server_error"


def test_response_usage_negative_tokens_invalid() -> None:
    """测试负数令牌验证"""
    with pytest.raises(ValidationError):
        ResponseUsage(
            prompt_tokens=-1,
            completion_tokens=10,
            total_tokens=9,
        )

    with pytest.raises(ValidationError):
        ResponseUsage(
            prompt_tokens=10,
            completion_tokens=-5,
            total_tokens=5,
        )


def test_response_object_invalid_status() -> None:
    """测试无效状态验证"""
    with pytest.raises(ValidationError):
        ResponseObject(
            id="resp_123",
            created=1234567890,
            model="gpt-4.1-mini",
            status="invalid_status",
            output=[],
            usage=ResponseUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )
