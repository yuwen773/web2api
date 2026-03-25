# Chat Completions API 文档

## 概述

提供 OpenAI 兼容的 Chat Completions 接口，支持流式和非流式两种模式。每次请求创建独立会话，完成后自动删除。

---

## 获取模型列表

**端点:** `GET /v1/models`

### 响应示例

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4.1-mini",
      "object": "model",
      "created": 1743000000,
      "owned_by": "taiji"
    }
  ]
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/models
```

---

## Chat Completions 非流式

**端点:** `POST /v1/chat/completions`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，如 `gpt-4.1-mini` |
| `messages` | array | 是 | 消息列表，至少包含一条消息 |
| `stream` | boolean | 否 | 是否使用流式输出，默认 `false` |
| `temperature` | float | 否 | 采样温度，0-2 之间 |
| `max_tokens` | integer | 否 | 最大生成 token 数，需大于 0 |

### Messages 格式

```json
{
  "role": "user",
  "content": "你好"
}
```

支持的 role: `system`, `user`, `assistant`

### 请求示例

```json
{
  "model": "gpt-4.1-mini",
  "messages": [
    {"role": "system", "content": "你是一个有帮助的助手"},
    {"role": "user", "content": "hello"}
  ]
}
```

### 响应示例

```json
{
  "id": "chatcmpl-abc123def456",
  "object": "chat.completion",
  "created": 1743000000,
  "model": "gpt-4.1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么可以帮助你的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}]}'
```

---

## Chat Completions 流式

**端点:** `POST /v1/chat/completions`

设置 `stream: true` 启用流式输出，使用 SSE (Server-Sent Events) 传输。

### 请求示例

```json
{
  "model": "gpt-4.1-mini",
  "stream": true,
  "messages": [{"role": "user", "content": "hello"}]
}
```

### SSE 事件格式

**首个事件 - role 初始化:**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1743000000,"model":"gpt-4.1-mini","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

```

**内容块:**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1743000000,"model":"gpt-4.1-mini","choices":[{"index":0,"delta":{"content":"你"},"finish_reason":null}]}

```

**结束事件:**
```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1743000000,"model":"gpt-4.1-mini","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### cURL 示例

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","stream":true,"messages":[{"role":"user","content":"hello"}]}'
```

---

## 错误响应

### 400 Bad Request - 缺少 messages

```json
{
  "error": {
    "code": "bad_request",
    "message": "body.messages: Field required",
    "status": 400,
    "request_id": "abc123"
  },
  "detail": "body.messages: Field required"
}
```

### 400 Bad Request - 太极 AI 错误

```json
{
  "error": {
    "code": "bad_request",
    "message": "太极AI错误: xxx",
    "status": 400,
    "request_id": "abc123"
  },
  "detail": "太极AI错误: xxx"
}
```

### 401 Unauthorized - 认证失败

```json
{
  "error": {
    "code": "auth_failed",
    "message": "Authentication failed.",
    "status": 401,
    "request_id": "abc123"
  },
  "detail": "Authentication failed."
}
```

### 429 Too Many Requests - 请求过多

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests.",
    "status": 429,
    "request_id": "abc123"
  },
  "detail": "Too many requests."
}
```

### 500 Internal Server Error

```json
{
  "error": {
    "code": "internal_server_error",
    "message": "Internal server error.",
    "status": 500,
    "request_id": "abc123"
  },
  "detail": "Internal server error."
}
```

---

## 内部实现

### 会话管理

1. 每次请求调用 `/api/chat/session` 创建新会话
2. 请求完成后调用 `/api/chat/session/{id}` 删除会话
3. 流式请求中断时也会清理会话

### 消息转换

`messages` 数组会被转换为太极 AI 的 `text` 字段，发送给 `/api/chat/completions`。

### 并发控制

通过全局 semaphore 限制并发请求数，避免上游风控或 429 错误。

### 401 自动重登录

首次请求返回 401 时，自动使用存储的账号密码重新登录并重试一次。
