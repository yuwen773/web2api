# API 文档索引

## 目录

- [Chat Completions API](chat.md) - OpenAI 兼容聊天接口
- [Anthropic Messages API](anthropic.md) - Anthropic 兼容消息接口
- [Responses API](responses.md) - OpenAI Responses API (Codex 兼容)
- [图片生成 API](images.md) - 图片生成接口

---

## 快速参考

### 健康检查

```bash
GET /
```

返回: `{"status": "ok"}`

---

### OpenAI Chat Completions

```bash
POST /v1/chat/completions
```

核心参数: `model`, `messages`, `stream`

---

### Anthropic Messages

```bash
POST /v1/messages
```

核心参数: `model`, `messages`, `max_tokens`, `stream`

---

### OpenAI Responses API

```bash
POST /v1/responses
```

核心参数: `model`, `input`, `instructions`, `stream`

---

### 图片生成

```bash
# Nano-banana
POST /v1/images/generations

# GT-4o-image-vip
POST /v1/images/create
```

核心参数: `model`, `prompt`, `n`, `ratio`

---

### 获取模型列表

```bash
GET /v1/models
```

---

## 通用错误格式

```json
{
  "error": {
    "code": "bad_request",
    "message": "错误描述",
    "status": 400,
    "request_id": "请求ID"
  },
  "detail": "错误描述"
}
```

常见错误码：

| code | HTTP 状态 | 说明 |
|------|-----------|------|
| `auth_failed` | 401 | API Key 缺失或无效 |
| `bad_request` | 400 | 请求参数错误 |
| `rate_limit_exceeded` | 429 | 请求过于频繁 |
| `internal_server_error` | 500 | 服务器内部错误 |

---

## 认证

服务支持可选的 API Key 鉴权（配置 `WEB2API_API_KEYS` 启用）。

### 请求头

| 头部 | 值 | 说明 |
|------|-----|------|
| `Content-Type` | `application/json` | 所有 API 均需要 |
| `X-API-Key` | 配置的 API Key | 鉴权启用时需要 |
| `x-request-id` | 任意值 | 可选，用于追踪请求 |

### 鉴权失败响应

```json
{
  "error": {
    "code": "auth_failed",
    "message": "Missing API key.",
    "status": 401,
    "request_id": "请求ID"
  },
  "detail": "Missing API key."
}
```

### 豁免路径

以下端点无需 API Key：

- `/metrics` - Prometheus 指标
- `/stats` - 监控仪表盘
- `/docs` - API 文档
- `/openapi.json` - OpenAPI 规范
- `/redoc` - ReDoc 文档
