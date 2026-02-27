# web2api 架构文档

## 项目结构

```
web2api/
├── main.py                      # FastAPI 入口
│
├── src/
│   ├── api/                     # API 路由
│   │   ├── openai.py            # OpenAI 兼容
│   │   └── anthropic.py         # Anthropic 兼容
│   ├── client/
│   │   └── taiji_client.py      # TaijiAI 客户端
│   ├── middleware/
│   │   └── request_middleware.py # 错误处理中间件
│   ├── utils/
│   │   ├── message_converter.py # OpenAI → 太极AI 转换
│   │   ├── concurrency.py       # 并发限制
│   │   ├── logging_config.py    # 日志配置
│   │   └── request_context.py   # 请求上下文 (request_id)
│   └── models/                  # 数据模型
│       ├── auth.py
│       ├── openai_request.py
│       ├── openai_response.py
│       └── anthropic_request.py
│
├── tests/                       # 14 个测试文件，37 个用例
├── config/config.yaml
└── memory-bank/
```

---

## API 端点

| 格式 | 端点 | 功能 |
|------|------|------|
| OpenAI | `POST /v1/chat/completions` | 聊天 (流式/非流式) |
| OpenAI | `GET /v1/models` | 模型列表 |
| Anthropic | `POST /v1/messages` | 消息 (流式/非流式) |
| 通用 | `GET /` | 健康检查 |

---

## 日志系统

**格式**: `时间戳 [级别] [request_id=xxx] 模块名: 消息`

**关键位置**:
- API 请求开始/结束
- 登录成功/失败（账号脱敏）
- 错误信息
- 客户端断开连接

---

## 错误处理

**错误码映射**:
- `400` → `bad_request`
- `401` → `auth_failed`
- `429` → `rate_limit_exceeded`
- `500` → `internal_server_error`

**统一格式**:
```json
{
  "error": {"code": "...", "message": "...", "status": 400, "request_id": "..."},
  "detail": "..."
}
```

---

## TaijiClient 类

```python
class TaijiClient:
    async def login(account, password) -> str
    async def get_models() -> list[dict]
    async def create_session(model) -> int
    async def delete_session(id) -> dict
    def send_message(session_id, text, stream) -> dict | AsyncIterator
```

---

## 待实现

| 阶段 | 功能 |
|------|------|
| 4.3-4.5 | Docker、README |
| 5 | SDK 兼容性测试 |
| 6 | 部署上线 |
