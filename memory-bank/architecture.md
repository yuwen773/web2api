# web2api 架构文档

## 项目结构

```
web2api/
├── main.py                      # FastAPI 入口 (93 行)
│
├── src/
│   ├── api/
│   │   └── openai.py            # OpenAI 路由 (353 行)
│   ├── client/
│   │   └── taiji_client.py      # TaijiClient 类 (534 行)
│   ├── utils/
│   │   ├── message_converter.py # OpenAI → 太极AI 转换 (207 行)
│   │   └── concurrency.py       # 全局并发限制 (15 行)
│   └── models/
│       ├── auth.py              # 认证模型 (28 行)
│       ├── openai_request.py    # OpenAI 请求模型 (21 行)
│       └── openai_response.py   # OpenAI 响应模型 (33 行)
│
├── tests/                       # 11 个测试文件，30 个用例
├── config/config.yaml           # 配置文件
└── memory-bank/                 # 项目知识库
```

---

## API 端点

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/` | GET | 健康检查 | ✅ |
| `/v1/chat/completions` | POST | 聊天完成 (非流式+流式) | ✅ |
| `/v1/models` | GET | 模型列表 | ✅ |

---

## 核心流程

```
客户端请求 (OpenAI 格式)
    ↓
FastAPI 路由 (openai.py)
    ↓
1. 创建新会话 (create_session)
2. messages → prompt 转换
3. 发送消息 SSE 流式 (send_message)
4. 转换格式返回客户端
5. 删除会话 (delete_session)
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
    async def close() -> None
```

---

## 太极AI API 端点

| 端点 | 用途 |
|------|------|
| `POST /api/user/login` | 获取 JWT token |
| `GET /api/chat/tmpl` | 获取模型列表 |
| `POST /api/chat/session` | 创建会话 |
| `DELETE /api/chat/session/{id}` | 删除会话 |
| `POST /api/chat/completions` | 发送消息 (SSE) |

---

## 关键请求头

```python
{
    "authorization": "<token>",        # ⚠️ 无 Bearer 前缀
    "x-app-version": "2.14.0",
    "accept": "text/event-stream",
}
```

---

## OpenAI 数据模型

```python
# 请求
ChatCompletionRequest(model, messages, stream=False)

# 响应
ChatCompletionResponse(id, created, model, choices, usage)
```

---

## 待实现

| 阶段 | 功能 |
|------|------|
| 3 | Anthropic 兼容接口 |
| 4 | 日志、错误处理、Docker |
| 5 | SDK 兼容性测试 |
