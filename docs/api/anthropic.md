# Anthropic Messages API 文档

## 概述

提供 Anthropic 兼容的 Messages 接口，支持流式和非流式两种模式。内部复用了 Chat Completions 的实现。

---

## Messages 非流式

**端点:** `POST /v1/messages`

### 请求头

| 头部 | 值 | 说明 |
|------|-----|------|
| `Content-Type` | `application/json` | 内容类型 |
| `x-api-key` | 任意值 | 认证密钥，本服务忽略但要求提供 |

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，如 `claude-opus-4-6` |
| `messages` | array | 是 | 消息列表，至少包含一条消息 |
| `max_tokens` | integer | 是 | 最大生成 token 数，需大于 0 |
| `system` | string | 否 | 系统提示 |
| `stream` | boolean | 否 | 是否使用流式输出，默认 `false` |

### Messages 格式

```json
{
  "role": "user",
  "content": "你好"
}
```

支持的 role: `user`, `assistant`

### 请求示例

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "messages": [
    {"role": "user", "content": "hello"}
  ]
}
```

### 响应示例

```json
{
  "id": "msg_abc123def456",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "你好！有什么可以帮助你的吗？"
    }
  ],
  "model": "claude-opus-4-6",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: any" \
  -d '{"model":"claude-opus-4-6","max_tokens":1024,"messages":[{"role":"user","content":"hello"}]}'
```

---

## Messages 流式

**端点:** `POST /v1/messages`

设置 `stream: true` 启用流式输出，使用 SSE (Server-Sent Events) 传输。

### 请求示例

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "stream": true,
  "messages": [
    {"role": "user", "content": "hello"}
  ]
}
```

### SSE 事件格式

**内容块:**
```
event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text","text":"你"}}

```

**消息完成:**
```
event: message_delta
data: {"type":"message_delta","delta":{"type":"usage","output_tokens":20},"usage":{"input_tokens":10,"output_tokens":20}}

```

**消息停止:**
```
event: message_stop
data: {}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: any" \
  -d '{"model":"claude-opus-4-6","max_tokens":1024,"stream":true,"messages":[{"role":"user","content":"hello"}]}'
```

---

## 系统提示

使用 `system` 参数传递系统提示：

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "system": "你是一个有帮助的助手",
  "messages": [
    {"role": "user", "content": "hello"}
  ]
}
```

---

## 错误响应

### 400 Bad Request

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

### 401 Unauthorized

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

### 429 Too Many Requests

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

---

## 内部实现

### 消息转换

Anthropic 格式的 `messages` 和 `system` 会被转换为 Chat Completions 格式处理。

### 会话管理

与 Chat Completions 相同，每次请求创建独立会话，完成后自动删除。
