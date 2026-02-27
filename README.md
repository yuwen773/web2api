# web2api

将太极 AI 网页能力封装为兼容 OpenAI 和 Anthropic 的 HTTP API 服务。

## 功能特性

- OpenAI 兼容接口
  - `POST /v1/chat/completions`（支持流式和非流式）
  - `GET /v1/models`
- Anthropic 兼容接口
  - `POST /v1/messages`（支持流式和非流式）
- 每次请求创建独立会话，完成后自动删除，避免上下文串线
- 自动重登录（401 时重试一次）
- 全局并发限制（`MAX_CONCURRENT`）
- 统一错误格式与请求级日志（含 `request_id`）

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
  -d "{\"model\":\"gpt-4.1-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### OpenAI 流式

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-4.1-mini\",\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### Anthropic 非流式

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: any" \
  -d "{\"model\":\"claude-opus-4-6\",\"max_tokens\":1024,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

### Anthropic 流式

```bash
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: any" \
  -d "{\"model\":\"claude-opus-4-6\",\"max_tokens\":1024,\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}]}"
```

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
- 该服务默认是自用场景，若多人使用请先加鉴权和配额控制。
- `MAX_CONCURRENT` 过高可能导致上游风控或 429 错误。
- 流式请求中客户端主动断开连接属于正常场景，服务端会清理资源并结束会话。
