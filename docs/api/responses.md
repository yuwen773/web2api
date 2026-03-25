# Responses API 文档

## 概述

提供 OpenAI Responses API 兼容接口，支持 Codex CLI。内部转换为 Chat Completions 格式处理。

---

## Responses 非流式

**端点:** `POST /v1/responses`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称，如 `gpt-4.1-mini` |
| `input` | string/object/array | 是 | 输入内容 |
| `instructions` | string | 否 | 系统指令 |
| `stream` | boolean | 否 | 是否使用流式输出，默认 `false` |
| `max_tokens` | integer | 否 | 最大生成 token 数 |
| `temperature` | float | 否 | 采样温度，0-2 之间 |

### Input 格式

**字符串格式:**
```json
{
  "input": "hello"
}
```

**Codex 对象格式:**
```json
{
  "input": {"str": "hello"}
}
```

**Codex 消息数组格式:**
```json
{
  "input": [
    {"role": "user", "content": [{"type": "input_text", "text": "hello"}]}
  ]
}
```

### 请求示例

**基础用法:**
```json
{
  "model": "gpt-4.1-mini",
  "input": "hello"
}
```

**带指令:**
```json
{
  "model": "gpt-4.1-mini",
  "input": "hello",
  "instructions": "You are a helpful assistant."
}
```

### 响应示例

```json
{
  "id": "resp-abc123def456",
  "object": "response",
  "created_at": 1743000000,
  "model": "gpt-4.1-mini",
  "status": "completed",
  "output": [
    {
      "id": "msg_xyz789",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "你好！有什么可以帮助你的吗？",
          "annotations": []
        }
      ]
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "error": null,
  "incomplete_details": null,
  "metadata": {}
}
```

### cURL 示例

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","input":"hello"}'
```

---

## Responses 流式

**端点:** `POST /v1/responses`

设置 `stream: true` 启用流式输出。

### 请求示例

```json
{
  "model": "gpt-4.1-mini",
  "stream": true,
  "input": "hello"
}
```

### SSE 事件格式

**响应创建:**
```
data: {"type":"response.created","response":{"id":"resp-abc123"}}

```

**输出项完成:**
```
data: {"type":"response.output_item.done","item":{"type":"message","role":"assistant","id":"msg_xyz789","content":[{"type":"output_text","text":"你好"}]}}

```

**响应完成:**
```
data: {"type":"response.completed","response":{"id":"resp-abc123","usage":{"input_tokens":10,"input_tokens_details":null,"output_tokens":20,"output_tokens_details":null,"total_tokens":30}}}

```

### cURL 示例

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4.1-mini","stream":true,"input":"hello"}'
```

---

## Codex CLI 集成

### 配置

```bash
codex config set api.base_url http://localhost:8000/v1
codex config set api.key "your-api-key"
```

### 使用

```bash
codex "帮我分析这个项目"
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

### 格式转换

Responses API 请求会被转换为 Chat Completions 格式：

| Responses 字段 | Chat Completions 映射 |
|---------------|---------------------|
| `input` (string) | `messages[0].content` |
| `input` ({"str": "..."}) | `messages[0].content` |
| `instructions` | `messages[0]` (role=system) |
| Codex `input` 数组 | 提取最后的用户消息 |

### 支持的 Codex 功能

- 基础对话请求
- 流式响应
- System/Developer 指令
- 工具调用（function calling）
- 多轮对话历史
- 并行工具调用
