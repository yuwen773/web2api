# web2api

将太极 AI 网页能力封装为兼容 OpenAI 和 Anthropic 的 HTTP API 服务。

## 功能特性

- OpenAI 兼容接口
  - `POST /v1/chat/completions`（支持流式和非流式）
  - `GET /v1/models`
- OpenAI Responses API 接口（Codex 兼容）
  - `POST /v1/responses`（支持流式和非流式）
  - 兼容 OpenAI Codex CLI
- Anthropic 兼容接口
  - `POST /v1/messages`（支持流式和非流式）
- 图片生成接口
  - `POST /v1/images/generations`（Nano-banana 绘图）
  - `POST /v1/images/create`（GT-4o-image-vip 绘图）
- 每次请求创建独立会话，完成后自动删除，避免上下文串线
- 自动重登录（401 时重试一次）
- 全局并发限制（`MAX_CONCURRENT`）
- 统一错误格式与请求级日志（含 `request_id`）
- API Key 鉴权（可选，配置 `WEB2API_API_KEYS` 启用）

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置

复制并编辑环境变量：

```bash
copy .env.example .env
```

至少配置：

- `TAIJI_ACCOUNT`
- `TAIJI_PASSWORD`

可选配置：

- `TAIJI_API_BASE`（默认 `https://ai.aurod.cn`）
- `TAIJI_APP_VERSION`（默认 `2.14.0`）
- `MAX_CONCURRENT`（默认 `5`）
- `WEB2API_HOST`（默认 `0.0.0.0`）
- `WEB2API_PORT`（默认 `8000`）
- `WEB2API_API_KEYS`（默认空，不启用鉴权，支持逗号分隔多个 key）

### 3. 运行

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://localhost:8000/
```

## API 使用示例

### OpenAI 非流式

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"gpt-4.1-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### OpenAI 流式

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"gpt-4.1-mini\",\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### Anthropic 非流式

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"claude-opus-4-6\",\"max_tokens\":1024,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### Anthropic 流式

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"claude-opus-4-6\",\"max_tokens\":1024,\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### OpenAI Responses API 非流式

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"gpt-4.1-mini\",\"input\":\"hello\"}"
```

### OpenAI Responses API 流式

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"gpt-4.1-mini\",\"stream\":true,\"input\":\"hello\"}"
```

### OpenAI Responses API 带指令

```bash
curl http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"gpt-4.1-mini\",\"input\":\"hello\",\"instructions\":\"You are a helpful assistant.\"}"
```

### Nano-banana 图片生成

```bash
curl http://localhost:8000/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"Nano-banana 2 绘图\",\"prompt\":\"科技感封面图\",\"n\":2,\"ratio\":\"16:9\"}"
```

### GT-4o-image-vip 图片生成

```bash
curl http://localhost:8000/v1/images/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d "{\"model\":\"GT-4o-image-vip（绘图模型）\",\"prompt\":\"科技感封面图\",\"n\":2,\"ratio\":\"16:9\"}"
```

详细接口文档请查看 [docs/api/images.md](docs/api/images.md)

## 配置说明

配置读取优先级：

1. 环境变量（最高优先级）
2. `config/config.yaml`
3. 代码默认值

阶段 4.3 要求的覆盖项已支持：

- `TAIJI_ACCOUNT`
- `TAIJI_PASSWORD`
- `TAIJI_API_BASE`
- `MAX_CONCURRENT`

## Docker 部署

### 构建并启动

```bash
docker compose up --build -d
```

### 查看日志

```bash
docker compose logs -f
```

### 停止

```bash
docker compose down
```

## 注意事项

- `authorization` 头使用原始 JWT，不要加 `Bearer` 前缀。
- 请勿提交真实账号、密码、JWT、Cookie 到代码仓库。
- `MAX_CONCURRENT` 过高可能导致上游风控或 429 错误。
- 流式请求中客户端主动断开连接属于正常场景，服务端会清理资源并结束会话。

## API Key 鉴权

服务支持可选的 API Key 鉴权，防止未授权访问。

### 配置方式

**环境变量：**

```bash
WEB2API_API_KEYS=key1,key2,key3
```

**配置文件 `config/config.yaml`：**

```yaml
api:
  api_keys:
    - key1
    - key2
    - key3
```

### 使用方式

客户端请求时在 HTTP 头中添加 `X-API-Key`：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: key1" \
  -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}]}'
```

### 鉴权行为

- `WEB2API_API_KEYS` 为空或不配置：不启用鉴权，所有请求均可访问
- `WEB2API_API_KEYS` 有值：请求必须携带匹配的 `X-API-Key` 头
- 鉴权失败返回 `401 Unauthorized`

### 豁免路径

以下端点无需鉴权：

- `/metrics` - Prometheus 指标
- `/stats` - 监控仪表盘
- `/docs` - API 文档
- `/openapi.json` - OpenAPI 规范
- `/redoc` - ReDoc 文档

## Claude Code Skills

### taiji-image-generator

独立的图片生成工具，不依赖 web2api 服务，支持 Windows/Linux/macOS。

**功能：**
- 通过 Taiji AI API 直接生成图片
- 支持 Nano-banana 和 GT-4o-image-vip 模型
- 兼容 Claude Code、Codex、OpenClaw 等 CLI 工具

**安装：**

```bash
cd skills/taiji-image-generator
pip install -r requirements.txt
```

**配置：** 创建 `assets/credentials.json`：

```json
{
  "base_url": "https://ai.aurod.cn",
  "account": "your@email.com",
  "password": "your_password",
  "app_version": "2.14.0"
}
```

**使用：**

```bash
python scripts/taiji_image.py generate \
  --model "Nano-banana 2 绘图" \
  --prompt "科技感封面图" \
  --n 2 \
  --ratio "16:9"
```

详细文档请查看 [skills/taiji-image-generator/SKILL.md](skills/taiji-image-generator/SKILL.md)

## Codex 集成

本项目支持 OpenAI Codex CLI，可以通过配置本地 API 端点使用。

### 配置步骤

1. 启动本服务：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. 配置 Codex 使用本地 API：

```bash
codex config set api.base_url http://localhost:8000/v1
```

或者在配置文件 `~/.codex/config.toml` 中设置：

```toml
[api]
base_url = "http://localhost:8000/v1"
```

3. 设置 API Key（与 `WEB2API_API_KEYS` 配置的值一致）：

```bash
codex config set api.key "your-api-key"
```

### 使用示例

```bash
# 直接使用 Codex
codex "帮我分析这个项目的结构"

# 或者在项目目录中使用
codex "帮我写一个排序函数"
```

### 支持的 Codex 功能

- ✅ 基础对话请求
- ✅ 流式响应
- ✅ System/Developer 指令
- ✅ 工具调用（function calling）
- ✅ 多轮对话历史
- ✅ 并行工具调用

### Codex 响应格式

本服务完全兼容 OpenAI Responses API SSE 事件格式：

- `response.created` - 响应创建事件
- `response.output_item.done` - 输出项完成（包含完整消息）
- `response.completed` - 响应完成（包含 usage 信息）

## 日志和监控

### 日志

服务使用 structlog 记录结构化日志，支持 JSON 和文本双格式输出。

日志文件位于 `logs/` 目录：
- `app.log` - 主日志（JSON 格式）
- `app-error.log` - 错误日志（ERROR 及以上）

### 监控端点

| 端点 | 说明 |
|------|------|
| `GET /metrics` | Prometheus 格式的指标 |
| `GET /stats` | 可视化监控仪表盘 |
| `GET /stats/json` | JSON 格式的统计数据 |

### 配置

日志和监控配置在 `config/config.yaml` 中：

```yaml
logging:
  level: INFO
  format: both
  directory: ./logs

monitoring:
  enabled: true
  metrics_endpoint: /metrics
  stats_endpoint: /stats

api:
  api_keys:
    - your-api-key-1
    - your-api-key-2
```
