# `/v1/responses/completions` 端点设计

## 概述

新增 `/v1/responses/completions` API 端点，作为现有 `/v1/chat/completions` 端点的完全功能相同别名。

## 设计目标

- 提供与 `/v1/chat/completions` 完全相同的功能
- 复用现有代码逻辑，避免重复
- 保持响应格式与原端点一致

## 实现方案

### 路由定义

在 `src/api/openai.py` 中新增路由处理器：

```python
@router.post("/v1/responses/completions", response_model=None)
async def responses_completions(
    request_body: ChatCompletionRequest,
    request: Request,
) -> Any:
    """与 /v1/chat/completions 完全功能相同的别名端点"""
    taiji_client = _get_taiji_client(request)
    if request_body.stream:
        return await _chat_completions_stream(request_body, taiji_client)
    return await _chat_completions_non_stream(request_body, taiji_client)
```

### 技术细节

| 项目 | 说明 |
|------|------|
| 请求模型 | `ChatCompletionRequest`（与原端点相同） |
| 响应格式 | 与原端点完全一致 |
| Completion ID 前缀 | `chatcmpl-`（与原端点相同） |
| Object 字段 | `chat.completion`（与原端点相同） |
| 内部逻辑 | 复用 `_chat_completions_stream` 和 `_chat_completions_non_stream` |

### 数据流

```
客户端请求 → /v1/responses/completions
           → _get_taiji_client(request)
           → _chat_completions_stream / _chat_completions_non_stream
           → Taiji API
           → 标准响应格式
           → 客户端响应
```

## 测试计划

1. 复制现有 `/v1/chat/completions` 测试用例
2. 将请求路径改为 `/v1/responses/completions`
3. 验证流式和非流式响应
4. 确认响应格式与原端点一致

## 影响范围

- **修改文件**: `src/api/openai.py`（新增约8行代码）
- **新增文件**: 无
- **破坏性变更**: 无
