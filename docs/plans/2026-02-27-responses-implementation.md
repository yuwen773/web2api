# `/v1/responses` API 端点实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 新增 `/v1/responses` API 端点，兼容 OpenAI Responses API 规范，复用现有 Taiji 客户端逻辑

**Architecture:** 新增 Responses 请求/响应模型和转换器层，将 Requests 格式转换为 Chat Completions 格式后调用现有 `_chat_completions_stream` 和 `_chat_completions_non_stream` 函数，最终请求 Taiji API

**Tech Stack:** FastAPI, Pydantic, Pytest, httpx

---

## Task 1: 创建 Responses 请求模型

**Files:**
- Create: `src/models/responses_request.py`
- Modify: `src/models/__init__.py` (添加导出)

**Step 1: 创建请求模型文件**

创建 `src/models/responses_request.py`:

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal, Optional, Union


class ResponseInputItem(BaseModel):
    """Responses API 输入项，支持文本/图像"""
    type: str = Field(default="text", pattern="^(text|image)$")
    text: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ResponseTool(BaseModel):
    """Responses API 工具定义"""
    type: str = Field(..., pattern="^(function|web_search|file_search)$")
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")


class ResponseRequest(BaseModel):
    """Responses API 请求模型"""
    model: str = Field(..., min_length=1)
    input: Union[str, list[ResponseInputItem]] = Field(default="")
    instructions: Optional[str] = Field(default=None, max_length=8000)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    tools: Optional[list[ResponseTool]] = None
    tool_choice: Optional[Union[str, dict[str, Any]]] = "auto"
    stream: bool = False
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    background: bool = False
    previous_response_id: Optional[str] = None
    reasoning: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")
```

**Step 2: 更新 `src/models/__init__.py` 导出新模型**

在 `src/models/__init__.py` 中添加:

```python
from .responses_request import ResponseInputItem, ResponseRequest, ResponseTool
```

并在 `__all__` 列表中添加:

```python
__all__ = [
    # ... 现有导出 ...
    "ResponseInputItem",
    "ResponseRequest",
    "ResponseTool",
]
```

**Step 3: 运行测试验证模型定义**

```bash
pytest tests/test_responses_models.py -v
```

预期: FAIL (文件不存在)

**Step 4: 编写模型验证测试**

创建 `tests/test_responses_models.py`:

```python
from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models.responses_request import (
    ResponseInputItem,
    ResponseRequest,
    ResponseTool,
)


def test_response_request_minimal():
    """测试最小有效请求"""
    req = ResponseRequest(model="gpt-4o", input="Hello")
    assert req.model == "gpt-4o"
    assert req.input == "Hello"
    assert req.stream is False
    assert req.temperature is None


def test_response_request_with_instructions():
    """测试带系统消息的请求"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello",
        instructions="You are a helpful assistant"
    )
    assert req.instructions == "You are a helpful assistant"


def test_response_request_with_input_items():
    """测试带输入项列表的请求"""
    req = ResponseRequest(
        model="gpt-4o",
        input=[
            ResponseInputItem(type="text", text="Hello")
        ]
    )
    assert len(req.input) == 1
    assert req.input[0].type == "text"
    assert req.input[0].text == "Hello"


def test_response_request_temperature_validation():
    """测试温度参数验证"""
    # 有效温度
    req = ResponseRequest(model="gpt-4o", input="Hello", temperature=1.5)
    assert req.temperature == 1.5

    # 无效温度（超出范围）
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4o", input="Hello", temperature=3.0)


def test_response_request_max_tokens_validation():
    """测试 max_tokens 验证"""
    # 有效值
    req = ResponseRequest(model="gpt-4o", input="Hello", max_tokens=100)
    assert req.max_tokens == 100

    # 无效值（<= 0）
    with pytest.raises(ValidationError):
        ResponseRequest(model="gpt-4o", input="Hello", max_tokens=0)


def test_response_input_item_text():
    """测试文本输入项"""
    item = ResponseInputItem(type="text", text="Hello")
    assert item.type == "text"
    assert item.text == "Hello"


def test_response_input_item_image():
    """测试图像输入项"""
    item = ResponseInputItem(type="image", image_url="https://example.com/img.png")
    assert item.type == "image"
    assert item.image_url == "https://example.com/img.png"


def test_response_tool_function():
    """测试函数工具定义"""
    tool = ResponseTool(
        type="function",
        name="get_weather",
        description="Get current weather",
        parameters={"location": "string"}
    )
    assert tool.type == "function"
    assert tool.name == "get_weather"
    assert tool.description == "Get current weather"


def test_response_request_extra_fields_forbidden():
    """测试禁止额外字段"""
    with pytest.raises(ValidationError):
        ResponseRequest(
            model="gpt-4o",
            input="Hello",
            unknown_field="should_fail"
        )
```

**Step 5: 运行测试验证**

```bash
pytest tests/test_responses_models.py -v
```

预期: PASS

**Step 6: 提交**

```bash
git add src/models/responses_request.py src/models/__init__.py tests/test_responses_models.py
git commit -m "feat: 添加 Responses API 请求模型

- 定义 ResponseRequest 主请求模型
- 定义 ResponseInputItem 输入项模型
- 定义 ResponseTool 工具定义模型
- 添加参数验证（temperature、max_tokens 等）
- 添加完整单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 创建 Responses 响应模型

**Files:**
- Create: `src/models/responses_response.py`
- Modify: `src/models/__init__.py` (添加导出)

**Step 1: 创建响应模型文件**

创建 `src/models/responses_response.py`:

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional


class ResponseOutputItem(BaseModel):
    """Responses API 输出项"""
    type: str = Field(..., pattern="^(text|tool_call|image)$")
    text: Optional[str] = None
    tool_use_id: Optional[str] = None
    name: Optional[str] = None
    arguments: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ResponseUsage(BaseModel):
    """Responses API 使用量统计"""
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class ResponseObject(BaseModel):
    """Responses API 响应对象"""
    id: str
    object: str = Field(default="response", pattern="^response$")
    created: int = Field(..., ge=0)
    model: str
    status: str = Field(..., pattern="^(completed|failed|in_progress)$")
    output: list[ResponseOutputItem] = Field(default_factory=list)
    usage: ResponseUsage
    error: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")
```

**Step 2: 更新 `src/models/__init__.py`**

在 `src/models/__init__.py` 中添加:

```python
from .responses_response import ResponseObject, ResponseOutputItem, ResponseUsage
```

并在 `__all__` 列表中添加:

```python
__all__ = [
    # ... 现有导出 ...
    "ResponseObject",
    "ResponseOutputItem",
    "ResponseUsage",
]
```

**Step 3: 添加响应模型测试**

在 `tests/test_responses_models.py` 中添加:

```python
from src.models.responses_response import (
    ResponseObject,
    ResponseOutputItem,
    ResponseUsage,
)


def test_response_usage():
    """测试使用量模型"""
    usage = ResponseUsage(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30
    )
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 20
    assert usage.total_tokens == 30


def test_response_output_item_text():
    """测试文本输出项"""
    item = ResponseOutputItem(type="text", text="Hello!")
    assert item.type == "text"
    assert item.text == "Hello!"


def test_response_output_item_tool_call():
    """测试工具调用输出项"""
    item = ResponseOutputItem(
        type="tool_call",
        tool_use_id="call_123",
        name="get_weather",
        arguments='{"location": "Beijing"}'
    )
    assert item.type == "tool_call"
    assert item.tool_use_id == "call_123"
    assert item.name == "get_weather"


def test_response_object_completed():
    """测试完成状态的响应对象"""
    resp = ResponseObject(
        id="resp-123",
        created=1234567890,
        model="gpt-4o",
        status="completed",
        output=[ResponseOutputItem(type="text", text="Hello!")],
        usage=ResponseUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
    )
    assert resp.object == "response"
    assert resp.status == "completed"
    assert len(resp.output) == 1
    assert resp.output[0].text == "Hello!"


def test_response_object_failed():
    """测试失败状态的响应对象"""
    resp = ResponseObject(
        id="resp-456",
        created=1234567890,
        model="gpt-4o",
        status="failed",
        output=[],
        usage=ResponseUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        ),
        error={"type": "invalid_request_error", "message": "Bad request"}
    )
    assert resp.status == "failed"
    assert resp.error is not None
    assert resp.error["type"] == "invalid_request_error"


def test_response_usage_negative_tokens_invalid():
    """测试负数 token 无效"""
    with pytest.raises(ValidationError):
        ResponseUsage(
            prompt_tokens=-1,
            completion_tokens=20,
            total_tokens=30
        )


def test_response_object_invalid_status():
    """测试无效状态"""
    with pytest.raises(ValidationError):
        ResponseObject(
            id="resp-123",
            created=1234567890,
            model="gpt-4o",
            status="invalid_status",
            output=[],
            usage=ResponseUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0
            )
        )
```

**Step 4: 运行测试验证**

```bash
pytest tests/test_responses_models.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/models/responses_response.py src/models/__init__.py tests/test_responses_models.py
git commit -m "feat: 添加 Responses API 响应模型

- 定义 ResponseObject 主响应模型
- 定义 ResponseOutputItem 输出项模型
- 定义 ResponseUsage 使用量模型
- 添加状态验证（completed/failed/in_progress）
- 添加完整单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 创建格式转换器

**Files:**
- Create: `src/utils/responses_converter.py`
- Test: `tests/test_responses_converter.py`

**Step 1: 编写转换器测试**

创建 `tests/test_responses_converter.py`:

```python
from __future__ import annotations

from src.models.responses_request import ResponseRequest, ResponseInputItem
from src.utils.responses_converter import (
    response_request_to_chat_request,
    chat_response_to_response_object,
)
from src.models.openai_request import ChatCompletionRequest


def test_convert_simple_request_to_chat():
    """测试简单请求转换（仅 input 字符串）"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello, how are you?"
    )

    chat_req = response_request_to_chat_request(req)

    assert isinstance(chat_req, ChatCompletionRequest)
    assert chat_req.model == "gpt-4o"
    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == "Hello, how are you?"
    assert chat_req.stream is False


def test_convert_request_with_instructions_to_chat():
    """测试带系统消息的请求转换"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello",
        instructions="You are a helpful assistant"
    )

    chat_req = response_request_to_chat_request(req)

    assert len(chat_req.messages) == 2
    assert chat_req.messages[0].role == "system"
    assert chat_req.messages[0].content == "You are a helpful assistant"
    assert chat_req.messages[1].role == "user"
    assert chat_req.messages[1].content == "Hello"


def test_convert_request_with_input_items_to_chat():
    """测试带输入项列表的请求转换"""
    req = ResponseRequest(
        model="gpt-4o",
        input=[
            ResponseInputItem(type="text", text="Hello")
        ]
    )

    chat_req = response_request_to_chat_request(req)

    assert len(chat_req.messages) == 1
    assert chat_req.messages[0].role == "user"
    assert chat_req.messages[0].content == "Hello"


def test_convert_request_with_stream_enabled():
    """测试流式请求转换"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello",
        stream=True
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.stream is True


def test_convert_request_with_temperature():
    """测试带温度的请求转换"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello",
        temperature=0.7
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.temperature == 0.7


def test_convert_request_with_max_tokens():
    """测试带 max_tokens 的请求转换"""
    req = ResponseRequest(
        model="gpt-4o",
        input="Hello",
        max_tokens=500
    )

    chat_req = response_request_to_chat_request(req)

    assert chat_req.max_tokens == 500


def test_convert_chat_response_to_response_object():
    """测试 Chat Completions 响应转换为 Responses 响应"""
    chat_resp = {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! I'm doing well, thank you!"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25
        }
    }

    resp = chat_response_to_response_object("gpt-4o", chat_resp)

    assert resp["object"] == "response"
    assert resp["status"] == "completed"
    assert resp["model"] == "gpt-4o"
    assert resp["created"] == 1234567890
    assert resp["id"] == "resp-abc123"
    assert len(resp["output"]) == 1
    assert resp["output"][0]["type"] == "text"
    assert resp["output"][0]["text"] == "Hello! I'm doing well, thank you!"
    assert resp["usage"]["prompt_tokens"] == 10
    assert resp["usage"]["completion_tokens"] == 15
    assert resp["usage"]["total_tokens"] == 25


def test_convert_empty_chat_response():
    """测试空内容响应转换"""
    chat_resp = {
        "id": "chatcmpl-empty",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": ""},
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 5, "completion_tokens": 0, "total_tokens": 5}
    }

    resp = chat_response_to_response_object("gpt-4o", chat_resp)

    assert resp["output"] == []
    assert resp["status"] == "completed"
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_responses_converter.py -v
```

预期: FAIL (模块不存在)

**Step 3: 实现转换器**

创建 `src/utils/responses_converter.py`:

```python
from __future__ import annotations

from src.models.responses_request import ResponseRequest, ResponseInputItem
from src.models.openai_request import ChatCompletionRequest, ChatMessage
from typing import Any


def response_request_to_chat_request(req: ResponseRequest) -> ChatCompletionRequest:
    """将 Responses 请求转换为 Chat Completions 请求

    转换映射:
    - input (string) -> messages[0].content
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
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_responses_converter.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/utils/responses_converter.py tests/test_responses_converter.py
git commit -m "feat: 添加 Responses API 格式转换器

- 实现 response_request_to_chat_request 函数
- 实现 chat_response_to_response_object 函数
- 处理 input 字符串和列表两种格式
- 处理 instructions 系统消息转换
- 添加完整单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 添加路由处理器

**Files:**
- Modify: `src/api/openai.py`
- Test: `tests/test_responses_api_routes.py`

**Step 1: 编写 API 路由测试**

创建 `tests/test_responses_api_routes.py`:

```python
from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from src.api.openai import router


class FakeTaijiClient:
    """模拟 Taiji 客户端"""
    def __init__(self) -> None:
        self.session_id = 101
        self.created_models: list[str] = []
        self.deleted_sessions: list[int] = []
        self.sent_messages: list[dict[str, Any]] = []

    async def create_session(self, model: str) -> int:
        self.created_models.append(model)
        return self.session_id

    async def delete_session(self, session_id: int) -> dict[str, Any]:
        self.deleted_sessions.append(session_id)
        return {"code": 0}

    async def get_models(self) -> list[dict[str, str]]:
        return []

    def send_message(
        self,
        session_id: int,
        text: str,
        files: list[dict[str, str]] | None = None,
        *,
        stream: bool = False,
    ) -> Any:
        self.sent_messages.append({
            "session_id": session_id,
            "text": text,
            "files": files or [],
            "stream": stream,
        })
        if stream:
            return self._stream_generator()
        return self._non_stream_result()

    async def _non_stream_result(self) -> dict[str, Any]:
        return {
            "text": "hello from taiji",
            "promptTokens": 3,
            "completionTokens": 7,
            "useTokens": 10,
            "model": "gpt-4o",
            "taskId": "task-1",
        }

    async def _stream_generator(self) -> AsyncIterator[dict[str, Any]]:
        chunks = [
            {"type": "string", "code": 0, "data": "Hel"},
            {"type": "string", "code": 0, "data": "lo"},
            {
                "type": "object",
                "code": 0,
                "data": {
                    "promptTokens": 2,
                    "completionTokens": 3,
                    "useTokens": 5,
                },
            },
        ]
        for chunk in chunks:
            yield chunk


def _build_test_app(fake_client: FakeTaijiClient):
    """构建测试应用"""
    from fastapi import FastAPI
    app = FastAPI()
    app.state.taiji_client = fake_client
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_responses_create_non_stream_basic():
    """测试非流式基本请求"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4o",
                "input": "hello",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    assert body["model"] == "gpt-4o"
    assert body["output"][0]["type"] == "text"
    assert body["output"][0]["text"] == "hello from taiji"
    assert body["usage"]["total_tokens"] == 10


@pytest.mark.asyncio
async def test_responses_create_with_instructions():
    """测试带系统消息的请求"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4o",
                "input": "hello",
                "instructions": "You are a helpful assistant",
            },
        )

    assert response.status_code == 200
    # 验证发送的消息包含系统消息
    assert fake_client.sent_messages[0]["text"] == "You are a helpful assistant\nhello"


@pytest.mark.asyncio
async def test_responses_create_stream_returns_events():
    """测试流式请求返回 SSE 事件"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        async with client.stream(
            "POST",
            "/v1/responses",
            json={
                "model": "gpt-4o",
                "input": "hello",
                "stream": True,
            },
        ) as response:
            raw_payload = (await response.aread()).decode("utf-8")

    assert response.status_code == 200
    # 验证包含响应事件
    assert "response.created" in raw_payload or "data:" in raw_payload
    assert fake_client.sent_messages[0]["stream"] is True


@pytest.mark.asyncio
async def test_responses_create_with_temperature():
    """测试带温度参数的请求"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4o",
                "input": "hello",
                "temperature": 0.5,
            },
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_responses_create_input_items():
    """测试带输入项列表的请求"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4o",
                "input": [
                    {"type": "text", "text": "hello"}
                ],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["output"][0]["text"] == "hello from taiji"


@pytest.mark.asyncio
async def test_responses_create_minimal():
    """测试最小有效请求"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "model": "gpt-4o",
            },
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_responses_create_missing_model():
    """测试缺少 model 参数"""
    fake_client = FakeTaijiClient()
    app = _build_test_app(fake_client)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/v1/responses",
            json={
                "input": "hello",
            },
        )

    assert response.status_code == 422  # Validation error
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_responses_api_routes.py -v
```

预期: FAIL (路由不存在)

**Step 3: 实现路由处理器**

在 `src/api/openai.py` 中添加:

```python
# 在文件顶部添加导入
from src.models.responses_request import ResponseRequest
from src.utils.responses_converter import (
    response_request_to_chat_request,
    chat_response_to_response_object,
)
from src.models.responses_response import ResponseObject as ResponseObjectModel

# 在文件末尾（router 定义之后）添加路由

@router.post("/v1/responses", response_model=None)
async def responses_create(
    request_body: ResponseRequest,
    request: Request,
) -> Any:
    """OpenAI Responses API 兼容端点

    将 Responses 格式请求转换为 Chat Completions 格式，
    复用现有 Taiji 客户端调用逻辑。
    """
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
    created = int(time.time())

    async def stream_generator() -> AsyncIterator[str]:
        try:
            # 发送 response.created 事件
            yield _format_sse({
                "type": "response.created",
                "response": {
                    "id": response_id,
                    "created": created,
                    "model": model,
                    "status": "in_progress",
                }
            })

            # 发送输出项添加事件
            yield _format_sse({
                "type": "response.output_item.added",
                "item": {"type": "text", "index": 0}
            })

            # 处理第一个 chunk
            for chunk in (first_chunk,):
                payload = _chunk_to_response_delta(chunk)
                if payload:
                    yield _format_sse(payload)

            # 处理后续 chunks
            async for chunk in stream:
                if _is_error_chunk(chunk):
                    raise TaijiAPIError(
                        str(chunk.get("msg") or "Taiji stream returned an error chunk."),
                        code=_to_int(chunk.get("code")),
                        status_code=400,
                    )
                payload = _chunk_to_response_delta(chunk)
                if payload:
                    yield _format_sse(payload)

            # 发送完成事件
            yield _format_sse({
                "type": "response.output_item.done",
                "item": {"type": "text", "index": 0}
            })
            yield _format_sse({
                "type": "response.done",
                "response": {
                    "id": response_id,
                    "status": "completed",
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


def _chunk_to_response_delta(chunk: dict[str, Any]) -> dict[str, Any] | None:
    """将 Taiji chunk 转换为 response.delta 事件"""
    if chunk.get("type") != "string":
        return None

    content = chunk.get("data")
    if content is None:
        return None

    text = str(content)
    if not text:
        return None

    return {
        "type": "response.delta",
        "delta": {"type": "text", "text": text}
    }
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_responses_api_routes.py -v
```

预期: PASS

**Step 5: 运行所有 OpenAI API 测试确保兼容性**

```bash
pytest tests/test_openai_api_routes.py -v
```

预期: PASS (确保现有功能不受影响)

**Step 6: 提交**

```bash
git add src/api/openai.py tests/test_responses_api_routes.py
git commit -m "feat: 添加 /v1/responses API 路由处理器

- 实现 responses_create 主路由
- 实现 _responses_non_stream 非流式处理
- 实现 _responses_stream 流式处理
- 复用现有 Taiji 客户端调用逻辑
- 添加完整集成测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 端到端测试验证

**Files:**
- Test: 手动验证或运行现有测试套件

**Step 1: 运行所有测试**

```bash
pytest tests/ -v --tb=short -k "responses or openai"
```

预期: 所有测试通过

**Step 2: 启动服务器进行手动测试**

```bash
python main.py
```

**Step 3: 测试非流式请求**

```bash
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": "Hello! Who are you?"
  }'
```

预期响应:
```json
{
  "id": "resp-xxx",
  "object": "response",
  "created": 1234567890,
  "model": "gpt-4o",
  "status": "completed",
  "output": [{"type": "text", "text": "..."}],
  "usage": {"prompt_tokens": N, "completion_tokens": M, "total_tokens": T}
}
```

**Step 4: 测试带系统消息的请求**

```bash
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": "Hello!",
    "instructions": "You are a helpful assistant."
  }'
```

**Step 5: 测试流式请求**

```bash
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "input": "Hello!",
    "stream": true
  }'
```

预期: SSE 格式的流式响应

**Step 6: 确认无误后更新项目文档**

更新 `README.md` 添加新端点说明（如需要）

**Step 7: 最终提交**

```bash
git add README.md  # 如果有更新
git commit -m "docs: 更新文档说明 /v1/responses 端点

- 添加 Responses API 端点说明
- 更新使用示例

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验收标准

- [ ] 所有单元测试通过 (`pytest tests/test_responses_*.py -v`)
- [ ] 所有 API 集成测试通过 (`pytest tests/test_*api_routes.py -v`)
- [ ] 现有 `/v1/chat/completions` 功能不受影响
- [ ] 手动测试验证非流式/流式响应正确
- [ ] 响应格式符合 OpenAI Responses API 规范
- [ ] 错误处理正确（400/502 等状态码）

## 参考资料

- 设计文档: `docs/plans/2026-02-27-responses-api-design.md`
- 现有 Chat Completions 实现: `src/api/openai.py`
- OpenAI Responses API: https://api.openai.com/v1/responses
- UCloud 文档: https://docs.ucloud.cn/modelverse/api_doc/text_api/response_api
