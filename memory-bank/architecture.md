# web2api 架构文档

## 项目结构

```
web2api/
├── main.py                      # FastAPI 入口
│
├── src/
│   ├── client/
│   │   └── taiji_client.py      # TaijiClient 类（534行）
│   ├── utils/
│   │   ├── message_converter.py # OpenAI → 太极AI 转换
│   │   └── concurrency.py       # 全局并发限制
│   └── models/
│       ├── auth.py              # 认证模型
│       ├── openai_request.py    # OpenAI 请求模型
│       └── openai_response.py   # OpenAI 响应模型
│
├── tests/                       # 12个测试文件，26个用例
├── config/config.yaml           # 配置文件
└── memory-bank/                 # 项目知识库
```

---

## 核心流程

```
客户端请求 (OpenAI 格式)
    ↓
FastAPI 路由
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
    # 上下文管理器
    async def __aenter__(self) -> TaijiClient
    async def __aexit__(self, exc_type, exc, tb) -> None

    # 认证
    async def login(account, password) -> str

    # 模型与会话
    async def get_models() -> list[dict]
    async def create_session(model) -> int
    async def delete_session(id) -> dict

    # 消息发送（支持 stream=True/False）
    def send_message(session_id, text, stream) -> dict | AsyncIterator

    # 内部
    async def _request(...)           # 普通请求，支持401重试
    async def _relogin()              # 自动重登录
```

---

## 太极AI API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/user/login` | POST | 获取 JWT token |
| `/api/chat/tmpl` | GET | 获取模型列表 |
| `/api/chat/session` | POST | 创建会话 |
| `/api/chat/session/{id}` | DELETE | 删除会话 |
| `/api/chat/completions` | POST | 发送消息 (SSE) |

---

## 关键请求头

```python
{
    "authorization": "<token>",        # ⚠️ 无 Bearer 前缀
    "x-app-version": "2.14.0",
    "accept": "text/event-stream",     # 流式请求
    "referer": "https://ai.aurod.cn/chat",
}
```

**Cookie**: `server_name_session` (httpx 自动管理)

---

## SSE 响应格式

```
data: {"type":"string","data":"Hello","code":0}
data: {"type":"string","data":" World","code":0}
data: {"type":"object","data":{"promptTokens":10,...},"code":0}
data: [DONE]
```

---

## 数据模型

### OpenAI 请求
```python
ChatCompletionRequest:
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None
    max_tokens: int | None
```

### OpenAI 响应
```python
ChatCompletionResponse:
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage
```

---

## 待实现

| 阶段 | 文件 | 功能 |
|------|------|------|
| 2.3-2.4 | `src/api/openai.py` | /v1/chat/completions 路由 |
| 2.5 | `src/api/openai.py` | /v1/models 端点 |
| 3 | `src/api/anthropic.py` | Anthropic 兼容接口 |
| 4 | - | 日志、错误处理、Docker |
