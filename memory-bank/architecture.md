# web2api 架构文档

## 项目结构

```
web2api/
├── src/
│   ├── client/
│   │   └── taiji_client.py      # TaijiClient 类（486行）
│   ├── utils/
│   │   └── message_converter.py # OpenAI → 太极AI 转换
│   └── models/
│       └── auth.py              # 认证模型
│
├── tests/                       # 8个测试文件，全部通过
├── config/config.yaml           # 配置文件
├── crawler/                     # 抓包分析文档（已完成）
└── memory-bank/                 # 项目知识库
```

---

## 核心流程（阶段 2 设计）

```
客户端请求 (OpenAI/Anthropic 格式)
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
    async def login(account, password) -> str
    async def get_models() -> list[dict]
    async def create_session(model) -> int
    async def delete_session(id) -> dict
    def send_message(session_id, text, stream) -> dict | AsyncIterator
    async def close() -> None
```

**异常**：`TaijiAPIError(code, status_code, message)`

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

## 待实现（阶段 2）

| 文件 | 功能 |
|------|------|
| `main.py` | FastAPI 入口 |
| `src/api/openai.py` | OpenAI 兼容路由 |
| `src/models/openai_request.py` | 请求模型 |
| `src/models/openai_response.py` | 响应模型 |
| `src/utils/concurrency.py` | 全局并发限制 |
