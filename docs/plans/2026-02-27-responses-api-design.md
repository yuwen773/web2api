# `/v1/responses` API 端点设计

## 概述

新增 `/v1/responses` API 端点，兼容 OpenAI Responses API 规范。该端点提供与 `/v1/chat/completions` 不同的请求/响应格式，支持更丰富的功能如工具调用、后台处理等。

## 设计目标

- 兼容 OpenAI Responses API 规范
- 复用现有 Taiji 客户端调用逻辑
- 支持流式和非流式响应
- 支持工具调用（tools）、后台处理（background）等高级功能

## 架构设计

### 组件结构

```
src/api/openai.py              # 新增 /v1/responses 路由
src/models/responses_request.py # 新增：Responses 请求模型
src/models/responses_response.py # 新增：Responses 响应模型
src/utils/responses_converter.py # 新增：格式转换器
tests/test_responses_converter.py   # 新增：转换器单元测试
tests/api/test_responses_endpoint.py # 新增：端点集成测试
```

### 数据流

```
客户端请求 → /v1/responses
         → responses_converter: ResponseRequest → ChatCompletionRequest
         → _chat_completions_stream / _chat_completions_non_stream
         → Taiji API
         → responses_converter: ChatResponse → ResponseObject
         → 客户端响应
```

## 请求模型设计

### 请求参数结构

文件：`src/models/responses_request.py`

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Any

class ResponseInputItem(BaseModel):
    type: str = "text"
    text: Optional[str] = None
    image_url: Optional[str] = None

class ResponseTool(BaseModel):
    type: str  # "function", "web_search", "file_search"
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None

class ResponseRequest(BaseModel):
    model: str
    input: Union[str, list[ResponseInputItem]] = Field(default="")
    instructions: Optional[str] = None  # 系统消息
    max_tokens: Optional[int] = None
    tools: Optional[list[ResponseTool]] = None
    tool_choice: Optional[Union[str, dict[str, Any]]] = "auto"
    stream: bool = False
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    background: bool = False
    previous_response_id: Optional[str] = None
    reasoning: Optional[dict[str, Any]] = None  # o-series 模型专用
```

### 与 Chat Completions 的转换映射

| Responses 字段 | Chat Completions 字段 |
|----------------|----------------------|
| `input` (string) | `messages[0].content` |
| `instructions` | `messages[0].role="system"` |
| `temperature` | `temperature` |
| `max_tokens` | `max_tokens` |
| `tools` | `tools` |
| `stream` | `stream` |

## 响应模型设计

### 响应结构

文件：`src/models/responses_response.py`

```python
from pydantic import BaseModel
from typing import Optional, Any

class ResponseOutputItem(BaseModel):
    type: str  # "text", "tool_call", "image"
    text: Optional[str] = None
    tool_use_id: Optional[str] = None
    name: Optional[str] = None
    arguments: Optional[str] = None

class ResponseUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ResponseObject(BaseModel):
    id: str
    object: str = "response"
    created: int
    model: str
    status: str  # "completed", "failed", "in_progress"
    output: list[ResponseOutputItem]
    usage: ResponseUsage
    error: Optional[dict[str, Any]] = None
```

### 流式事件格式

| 事件类型 | 说明 |
|---------|------|
| `response.created` | 响应创建 |
| `response.output_item.added` | 输出项添加 |
| `response.output_item.done` | 输出项完成 |
| `response.delta` | 内容增量 |
| `response.done` | 响应完成 |

### 与 Chat Completions 响应的转换

- `choices[0].message.content` → `output[0].text`
- 新增 `status` 字段（"completed"）
- `object` 从 "chat.completion" 改为 "response"

## 路由处理器实现

### 在 `src/api/openai.py` 中新增路由

```python
from src.models.responses_request import ResponseRequest
from src.utils.responses_converter import (
    response_request_to_chat_request,
    chat_response_to_response_object,
)

@router.post("/v1/responses", response_model=None)
async def responses_create(
    request_body: ResponseRequest,
    request: Request,
) -> Any:
    """OpenAI Responses API 兼容端点"""
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
```

## 转换器实现

### 创建 `src/utils/responses_converter.py`

```python
from src.models.responses_request import ResponseRequest, ResponseInputItem
from src.models.responses_response import ResponseObject, ResponseOutputItem
from src.models.openai_request import ChatCompletionRequest
from src.models.openai_response import ChatCompletionResponse
from typing import Any
import time

def response_request_to_chat_request(req: ResponseRequest) -> ChatCompletionRequest:
    """将 Responses 请求转换为 Chat Completions 请求"""
    messages = []

    # 添加系统消息
    if req.instructions:
        messages.append({"role": "system", "content": req.instructions})

    # 处理 input
    if isinstance(req.input, str):
        messages.append({"role": "user", "content": req.input})
    else:
        content = _convert_input_items_to_content(req.input)
        if content:
            messages.append({"role": "user", "content": content})

    return ChatCompletionRequest(
        model=req.model,
        messages=messages,
        stream=req.stream,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        tools=_convert_tools(req.tools) if req.tools else None,
    )

def chat_response_to_response_object(
    model: str,
    chat_resp: dict[str, Any]
) -> dict[str, Any]:
    """将 Chat Completions 响应转换为 Responses 响应"""
    content = chat_resp.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = chat_resp.get("usage", {})

    return {
        "id": f"resp-{chat_resp['id'].replace('chatcmpl-', '')}",
        "object": "response",
        "created": chat_resp.get("created", int(time.time())),
        "model": model,
        "status": "completed",
        "output": [{"type": "text", "text": content}] if content else [],
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }
```

## 错误处理

响应对象包含 `error` 字段，当 Taiji API 返回错误时：

```json
{
    "id": "resp-xxx",
    "object": "response",
    "status": "failed",
    "error": {
        "type": "invalid_request_error",
        "message": "具体错误信息"
    }
}
```

## 测试计划

### 单元测试 (`tests/test_responses_converter.py`)
- 请求格式转换测试
- 响应格式转换测试
- 边界情况处理

### 集成测试 (`tests/api/test_responses_endpoint.py`)
- 非流式请求/响应
- 流式事件格式
- 带系统消息的请求
- 错误处理

### 测试用例示例

```python
async def test_responses_create_basic():
    response = await client.post("/v1/responses", json={
        "model": "gpt-4o",
        "input": "Hello!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "response"
    assert data["status"] == "completed"
```

## 影响范围

- **新增文件**:
  - `src/models/responses_request.py`
  - `src/models/responses_response.py`
  - `src/utils/responses_converter.py`
  - `tests/test_responses_converter.py`
  - `tests/api/test_responses_endpoint.py`
- **修改文件**: `src/api/openai.py`（新增路由处理器）
- **破坏性变更**: 无

## 参考资料

- [OpenAI Responses API Reference](https://api.openai.com/v1/responses)
- [UCloud /v1/responses 接口文档](https://docs.ucloud.cn/modelverse/api_doc/text_api/response_api)
