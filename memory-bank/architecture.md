# web2api 架构文档

## 系统概览

将太极 AI 网页协议封装为标准接口：
- OpenAI 兼容：`/v1/chat/completions`、`/v1/models`
- Anthropic 兼容：`/v1/messages`

核心策略：**请求级会话**（每次新建，结束删除）

---

## 项目结构

```
web2api/
├── main.py                      # FastAPI 入口
├── src/
│   ├── api/
│   │   ├── openai.py            # OpenAI 兼容 (353行)
│   │   └── anthropic.py         # Anthropic 兼容 (404行)
│   ├── client/
│   │   └── taiji_client.py      # Taiji HTTP 客户端 (552行)
│   ├── middleware/
│   │   └── request_middleware.py # 错误处理 + request_id (240行)
│   ├── utils/
│   │   ├── message_converter.py # OpenAI/Anthropic → Taiji (207行)
│   │   ├── settings.py          # 配置加载 (141行)
│   │   ├── concurrency.py       # 并发控制 (32行)
│   │   ├── logging_config.py    # 日志配置
│   │   └── request_context.py   # 请求上下文
│   └── models/                  # Pydantic 模型
├── tests/                       # 39 个测试用例
│   ├── sdk_openai_compat.py     # OpenAI SDK 联调
│   └── sdk_anthropic_compat.py  # Anthropic SDK 联调
├── config/config.yaml
├── Dockerfile
└── docker-compose.yml
```

---

## 请求链路

```
SDK → FastAPI → message_converter → TaijiClient → 上游
                (文本/多轮/图片)    (会话管理)    (/api/chat/completions)
                                                    ↓
                                  SSE 转换 ← 响应流
                                                    ↓
                                    finally: 删除会话
```

---

## API 端点

| 接口 | 端点 | 功能 |
|------|------|------|
| OpenAI | `POST /v1/chat/completions` | 聊天（流式/非流式） |
| OpenAI | `GET /v1/models` | 模型列表 |
| Anthropic | `POST /v1/messages` | 消息（流式/非流式） |
| 通用 | `GET /` | 健康检查 |

---

## 配置优先级

```
环境变量 > config/config.yaml > 默认值
```

关键变量：`TAIJI_API_BASE`, `TAIJI_ACCOUNT`, `TAIJI_PASSWORD`, `MAX_CONCURRENT`

---

## 关键设计

| 项目 | 方案 |
|------|------|
| 会话策略 | 每次请求新建，结束删除 |
| 并发控制 | 全局信号量（默认 5） |
| 错误处理 | 流式先检查首块错误，再持续转换 |
| 日志追踪 | `request_id` 贯穿日志与错误响应 |
| 认证容错 | 401 自动重登并重试 |
| SDK 兼容 | OpenAI base_url 需 `/v1`，Anthropic 不需要 |

---

## TaijiClient 核心

```python
class TaijiClient:
    async def login(account, password) -> str
    async def get_models() -> list[dict]
    async def create_session(model) -> int
    async def delete_session(id) -> dict
    def send_message(session_id, text, stream) -> dict | AsyncIterator
```
