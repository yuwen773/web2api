# web2api 架构文档

## 项目结构

```
web2api/
├── main.py                 # FastAPI 入口 (待创建)
├── requirements.txt        # Python 依赖
│
├── config/
│   └── config.yaml        # 配置: 账号密码、并发限制
│
├── src/
│   ├── api/               # 路由层
│   │   ├── openai.py      # /v1/chat/completions, /v1/models
│   │   └── anthropic.py   # /v1/messages
│   │
│   ├── client/
│   │   └── taiji_client.py # 太极AI HTTP客户端
│   │
│   ├── models/
│   │   ├── auth.py        # 登录请求/响应模型
│   │   ├── openai_request.py
│   │   └── openai_response.py
│   │
│   └── utils/
│       ├── message_converter.py  # OpenAI messages → prompt
│       └── concurrency.py        # 全局并发限制
│
├── tests/                 # 测试文件
└── crawler/               # 抓包分析文档 (已完成)
```

## 核心流程

```
客户端请求 (OpenAI/Anthropic格式)
    ↓
FastAPI 路由
    ↓
1. 创建新会话 (create_session)
2. messages → prompt 转换
3. 发送消息 SSE 流式 (send_message)
4. 转换格式返回客户端
5. 删除会话 (delete_session)
```

## 关键设计 (v2.0)

| 问题 | 方案 |
|------|------|
| 会话隔离 | 每次请求新建会话，不复用 |
| 历史消息 | messages数组转为单一prompt |
| 上下文污染 | 请求结束后立即删除会话 |
| 并发控制 | 全局 Semaphore (最多5个) |
| 断线处理 | 捕获 CancelledError |

## 太极AI API 端点

| 端点 | 用途 |
|------|------|
| `POST /api/user/login` | 登录获取 token |
| `GET /api/chat/tmpl` | 获取模型列表 |
| `POST /api/chat/session` | 创建会话 |
| `DELETE /api/chat/session/{id}` | 删除会话 |
| `POST /api/chat/completions` | 发送消息 (SSE) |

## 必需请求头

```python
{
    "authorization": "Bearer <token>",
    "x-app-version": "2.14.0",
    "content-type": "application/json",
    "accept": "text/event-stream",
    "referer": "https://ai.aurod.cn/chat",
    "origin": "https://ai.aurod.cn"
}
```

## Cookie

```
server_name_session=<session_id>  # httpx自动管理
```
