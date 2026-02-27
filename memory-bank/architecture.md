# web2api 架构文档

## 项目结构

```
web2api/
├── main.py                      # FastAPI 入口 (95 行)
│
├── src/
│   ├── api/
│   │   ├── openai.py            # OpenAI 路由 (353 行)
│   │   └── anthropic.py         # Anthropic 路由 (404 行)
│   ├── client/
│   │   └── taiji_client.py      # TaijiClient 类 (534 行)
│   ├── utils/
│   │   ├── message_converter.py # 消息转换 (207 行)
│   │   └── concurrency.py       # 并发限制 (15 行)
│   └── models/
│       ├── auth.py              # 认证模型
│       ├── openai_request.py    # OpenAI 请求模型
│       ├── openai_response.py   # OpenAI 响应模型
│       └── anthropic_request.py # Anthropic 请求模型
│
├── tests/                       # 13 个测试文件，33 个用例
├── config/config.yaml           # 配置文件
└── memory-bank/                 # 项目知识库
```

---

## API 端点

| 格式 | 端点 | 方法 | 功能 |
|------|------|------|------|
| OpenAI | `/v1/chat/completions` | POST | 聊天完成 |
| OpenAI | `/v1/models` | GET | 模型列表 |
| Anthropic | `/v1/messages` | POST | 消息接口 |
| 通用 | `/` | GET | 健康检查 |

---

## 核心流程

```
客户端请求 (OpenAI/Anthropic 格式)
    ↓
FastAPI 路由 (openai.py / anthropic.py)
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

## 数据模型

### OpenAI
```python
# 请求
ChatCompletionRequest(model, messages, stream=False)
# 响应
ChatCompletionResponse(id, created, model, choices, usage)
```

### Anthropic
```python
# 请求
AnthropicRequest(model, max_tokens, messages, system, stream)
# 响应
Message(id, type, role, content, stop_reason, usage)
```

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

## 待实现

| 阶段 | 功能 |
|------|------|
| 4 | 日志、错误处理、Docker |
| 5 | SDK 兼容性测试 |
| 6 | 部署上线 |
