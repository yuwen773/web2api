# web2api 部署文档

## 部署方式概览

| 方式 | 适用场景 | 复杂度 |
|------|----------|--------|
| Docker Compose | 推荐，一键部署 | 低 |
| Docker 单容器 | 自定义编排 | 中 |
| 直接运行 | 开发/测试 | 低 |

---

## 一、Docker Compose 部署（推荐）

### 1.1 准备工作

```bash
# 克隆项目
git clone <repo_url>
cd web2api

# 创建环境变量文件
cp .env.example .env
```

### 1.2 配置环境变量

编辑 `.env` 文件，填入真实凭据：

```bash
# 必填
TAIJI_ACCOUNT=your_taiji_account
TAIJI_PASSWORD=your_taiji_password

# 可选（有默认值）
TAIJI_API_BASE=https://ai.aurod.cn
TAIJI_APP_VERSION=2.14.0
WEB2API_HOST=0.0.0.0
WEB2API_PORT=8000
MAX_CONCURRENT=5
```

### 1.3 启动服务

```bash
# 构建并启动（后台运行）
docker compose up --build -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 1.4 验证部署

```bash
# 健康检查
curl http://localhost:8000/

# OpenAI 接口测试
curl http://localhost:8000/v1/models

# Anthropic 接口测试
curl http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: any" \
  -d '{"model":"claude-opus-4-6","max_tokens":100,"messages":[{"role":"user","content":"hello"}]}'
```

---

## 二、Docker 单容器部署

### 2.1 构建镜像

```bash
docker build -t web2api:latest .
```

### 2.2 运行容器

```bash
docker run -d \
  --name web2api \
  -p 8000:8000 \
  -e TAIJI_ACCOUNT=your_account \
  -e TAIJI_PASSWORD=your_password \
  -e MAX_CONCURRENT=5 \
  --restart unless-stopped \
  web2api:latest
```

### 2.3 管理容器

```bash
# 查看日志
docker logs -f web2api

# 停止
docker stop web2api

# 启动
docker start web2api

# 删除
docker rm -f web2api
```

---

## 三、直接运行（开发/测试）

### 3.1 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3.2 配置环境变量

```bash
# 复制并编辑 .env 文件
cp .env.example .env
# 编辑 .env 填入真实凭据
```

### 3.3 启动服务

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 四、配置说明

### 4.1 配置优先级

```
环境变量 > config/config.yaml > 代码默认值
```

### 4.2 环境变量列表

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `TAIJI_ACCOUNT` | ✅ | - | 太极账号 |
| `TAIJI_PASSWORD` | ✅ | - | 太极密码 |
| `TAIJI_API_BASE` | ❌ | `https://ai.aurod.cn` | API 地址 |
| `TAIJI_APP_VERSION` | ❌ | `2.14.0` | 应用版本 |
| `WEB2API_HOST` | ❌ | `0.0.0.0` | 监听地址 |
| `WEB2API_PORT` | ❌ | `8000` | 监听端口 |
| `MAX_CONCURRENT` | ❌ | `5` | 最大并发数 |

### 4.3 安全建议

⚠️ **重要**：
- 不要将真实凭据提交到代码仓库
- `config/config.yaml` 中的真实凭据应移除或覆盖
- 生产环境使用环境变量或密钥管理服务
- 建议配置反向代理（Nginx）和 HTTPS

---

## 五、生产环境建议

### 5.1 反向代理配置（Nginx）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 5.2 性能调优

| 参数 | 建议 | 说明 |
|------|------|------|
| `MAX_CONCURRENT` | 5-20 | 根据上游限制调整 |
| `workers` | 2-4 | CPU 核心数 |
| 超时时间 | 120s | 流式请求需要较长超时 |

### 5.3 日志管理

```bash
# 查看实时日志
docker compose logs -f

# 导出日志
docker compose logs > web2api.log

# 日志轮转（在启动脚本中配置）
```

---

## 六、故障排查

### 6.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 401 错误 | 凭据错误 | 检查 `TAIJI_ACCOUNT`/`TAIJI_PASSWORD` |
| 429 错误 | 并发超限 | 降低 `MAX_CONCURRENT` |
| 超时 | 上游响应慢 | 增加超时时间或降低并发 |
| 端口占用 | 8000 端口被占用 | 修改 `WEB2API_PORT` |

### 6.2 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/

# 检查日志
docker compose logs --tail=50 web2api

# 进入容器调试
docker exec -it web2api bash
```

---

## 七、升级与维护

### 7.1 升级服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up --build -d

# 查看新版本日志
docker compose logs -f
```

### 7.2 备份与恢复

```bash
# 备份环境变量
cp .env .env.backup

# 备份配置文件
cp config/config.yaml config/config.yaml.backup
```

---

## 八、API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/v1/chat/completions` | POST | OpenAI 聊天接口 |
| `/v1/models` | GET | OpenAI 模型列表 |
| `/v1/messages` | POST | Anthropic 消息接口 |
