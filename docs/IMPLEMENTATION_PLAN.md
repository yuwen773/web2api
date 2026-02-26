# 太极AI 转 API 服务 - 实施计划

## 项目概述

将太极AI (ai.aurod.cn) 的网页聊天能力封装为标准 API 服务，同时支持 OpenAI 和 Anthropic 两种格式。

---

## 阶段 0: 环境准备

### 步骤 0.1: 创建项目目录结构

**指示：**
1. 在项目根目录下创建以下目录结构：
   ```
   web2api/
   ├── src/
   │   ├── api/          # API 路由层
   │   ├── client/       # 太极AI 客户端
   │   ├── models/       # 数据模型
   │   └── utils/        # 工具函数
   ├── tests/            # 测试文件
   ├── config/           # 配置文件
   └── requirements.txt  # 依赖列表
   ```

**测试：**
- 确认所有目录已创建
- 运行 `ls -la` 或 `dir` 验证目录结构

---

### 步骤 0.2: 初始化 Python 项目

**指示：**
1. 在项目根目录创建 `requirements.txt`，添加以下依赖：
   - fastapi
   - uvicorn[standard]
   - httpx
   - pydantic
   - python-dotenv
   - pytest
   - pytest-asyncio

2. 创建虚拟环境并安装依赖：
   - Windows: `python -m venv venv` 然后 `venv\Scripts\activate`
   - Linux/Mac: `python3 -m venv venv` 然后 `source venv/bin/activate`
   - 运行: `pip install -r requirements.txt`

**测试：**
- 运行 `pip list` 确认所有依赖已安装
- 在 Python 中导入 fastapi 验证：`python -c "import fastapi; print('OK')"`

---

### 步骤 0.3: 创建配置文件

**指示：**
1. 创建 `config/config.yaml`，包含以下配置项：
   - `taiji_api_base`: https://ai.aurod.cn
   - `taiji_account`: 你的账号
   - `taiji_password`: 你的密码
   - `server_host`: 0.0.0.0
   - `server_port`: 8000

2. 创建 `.env` 文件（用于敏感信息，加入 .gitignore）

**测试：**
- 确认配置文件可以读取
- 验证 .env 在 .gitignore 中

---

## 阶段 1: 太极AI 客户端实现

### 步骤 1.1: 实现登录功能

**指示：**
1. 在 `src/client/` 创建 `taiji_client.py`
2. 实现 `login()` 函数：
   - 发送 POST 请求到 `/api/user/login`
   - 请求体包含：account, password, code="", captcha="", invite="", agreement=True
   - 解析响应获取 token
   - 保存 token 供后续使用

3. 创建 `src/models/auth.py` 定义登录请求/响应的数据模型

**测试：**
1. 创建 `tests/test_login.py`
2. 手动测试：用你的真实账号密码调用登录函数
3. 验证：
   - 返回的 token 非空
   - token 格式为 JWT（包含三个点分隔的部分）
   - 打印 token 前20个字符确认

---

### 步骤 1.2: 实现获取模型列表

**指示：**
1. 在 `taiji_client.py` 添加 `get_models()` 函数
2. 发送 GET 请求到 `/api/chat/tmpl`
3. Headers 包含 Authorization: Bearer <token>
4. 解析响应，提取 models 数组

**测试：**
1. 创建 `tests/test_models.py`
2. 调用函数并打印模型数量
3. 验证：
   - 至少返回 50+ 个模型
   - 每个模型有 label 和 value 字段
   - 确认包含 "gpt-4.1-mini" 和 "claude-opus-4-6"

---

### 步骤 1.3: 实现新建会话

**指示：**
1. 在 `taiji_client.py` 添加 `create_session(model)` 函数
2. 发送 POST 请求到 `/api/chat/session`
3. 请求体：{"model": model_name, "plugins": [], "mcp": []}
4. 解析响应，返回 session_id

**测试：**
1. 创建测试函数
2. 用 "gpt-4.1-mini" 创建会话
3. 验证返回的 session_id 是数字类型
4. 用不同模型创建第二个会话，确认 id 不同

---

### 步骤 1.4: 实现发送消息（非流式）

**指示：**
1. 在 `taiji_client.py` 添加 `send_message(session_id, text)` 函数
2. 发送 POST 请求到 `/api/chat/completions`
3. 请求体：{"text": text, "sessionId": session_id, "files": []}
4. Headers 添加：`accept: text/event-stream`
5. 读取完整的 SSE 响应，拼接所有 "string" 类型的 data
6. 返回完整回复文本

**测试：**
1. 创建测试函数
2. 流程：登录 → 创建会话 → 发送 "hello"
3. 验证：
   - 收到多个 SSE 数据块
   - 最后一个块的 type 是 "object"
   - 拼接后的文本是连贯的中文回复
   - 打印完整回复内容

---

### 步骤 1.5: 实现发送消息（流式）

**指示：**
1. 修改 `send_message()` 函数，添加 `stream=True` 参数
2. 当 stream=True 时，返回一个异步生成器
3. 每收到一个 SSE 数据块就 yield 一次
4. 处理 `[DONE]` 标记，停止生成

**测试：**
1. 创建异步测试函数
2. 用 for 循环遍历流式响应
3. 验证：
   - 每次迭代收到一个文本片段
   - 片段按顺序拼接是完整回复
   - 最后正确结束循环

---

### 步骤 1.6: 实现会话复用管理

**指示：**
1. 创建 `SessionManager` 类
2. 维护一个字典：{model_name: session_id}
3. 提供 `get_session(model)` 方法：
   - 如果该模型的会话存在，返回已有 session_id
   - 如果不存在，创建新会话并缓存
4. 提供 `clear()` 方法清空所有缓存

**测试：**
1. 创建测试：同一个模型调用两次 get_session()
2. 验证两次返回相同的 session_id
3. 测试 clear() 后再次获取，应返回新 session_id

---

## 阶段 2: OpenAI 兼容接口

### 步骤 2.1: 搭建 FastAPI 基础框架

**指示：**
1. 在项目根目录创建 `main.py`
2. 初始化 FastAPI 应用
3. 添加健康检查端点 `GET /`
4. 添加 CORS 中间件，允许所有来源
5. 配置 uvicorn 启动参数

**测试：**
1. 启动服务：`python main.py` 或 `uvicorn main:app --reload`
2. 访问 http://localhost:8000
3. 验证返回 {"status": "ok"} 或类似消息
4. 访问 http://localhost:8000/docs 查看自动生成的 API 文档

---

### 步骤 2.2: 实现 /v1/chat/completions 路由（非流式）

**指示：**
1. 在 `src/api/` 创建 `openai.py`
2. 创建请求模型（Pydantic）：
   - model: string（必填）
   - messages: array（必填）
   - stream: boolean（默认 false）
   - temperature: number（可选）
3. 创建响应模型：
   - id: string
   - choices: array（包含 message 和 finish_reason）
   - usage: object（prompt_tokens, completion_tokens）
4. 实现路由逻辑：
   - 从 messages 中提取最后一条用户消息
   - 调用 TaijiClient.send_message()
   - 转换为 OpenAI 格式返回

**测试：**
1. 使用 curl 测试：
   ```bash
   curl http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}]}'
   ```
2. 验证响应格式符合 OpenAI 规范
3. 验证 choices[0].message.content 包含 AI 回复

---

### 步骤 2.3: 实现 /v1/chat/completions 流式响应

**指示：**
1. 修改路由函数，支持 stream=True
2. 当 stream=True 时，返回 StreamingResponse
3. 将太极AI的 SSE 格式转换为 OpenAI SSE 格式：
   - 太极格式：`data: {"type":"string","data":"内容"}`
   - OpenAI格式：`data: {"choices":[{"delta":{"content":"内容"}}]}\n\n`
4. 最后发送 `data: [DONE]\n\n`

**测试：**
1. 用 curl 测试流式：
   ```bash
   curl http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}],"stream":true}'
   ```
2. 验证每个数据块格式正确
3. 验证最后有 [DONE] 标记

---

### 步骤 2.4: 实现多轮对话支持

**指示：**
1. 修改会话管理逻辑
2. 为每个 API 请求创建独立的 session_id
3. 从 messages 数组中提取历史消息
4. 调用太极AI时传递完整的会话上下文

**注意：** 太极AI通过 session_id 自动维护历史，不需要手动传递历史消息

**测试：**
1. 发送包含3条消息的请求（system, user, assistant, user）
2. 验证 AI 能理解上下文
3. 测试：第一条说"我叫小明"，第二条问"我叫什么"，验证回复包含"小明"

---

### 步骤 2.5: 实现 /v1/models 模型列表接口

**指示：**
1. 创建 `GET /v1/models` 路由
2. 调用 TaijiClient.get_models()
3. 转换为 OpenAI 格式：
   ```json
   {
     "object": "list",
     "data": [
       {"id": "gpt-4.1-mini", "object": "model", ...},
       ...
     ]
   }
   ```

**测试：**
1. 访问 http://localhost:8000/v1/models
2. 验证返回格式正确
3. 验证包含至少 50 个模型

---

## 阶段 3: Anthropic 兼容接口

### 步骤 3.1: 实现 /v1/messages 路由（非流式）

**指示：**
1. 在 `src/api/` 创建 `anthropic.py`
2. 创建 Anthropic 请求模型：
   - model: string
   - messages: array（必须包含 role 和 content）
   - max_tokens: number（必填，可设默认值 4096）
3. 创建响应模型：
   - id, type, role, content（数组格式）
4. 实现路由逻辑，复用 TaijiClient
5. 转换为 Anthropic 格式返回

**测试：**
1. 用 curl 测试：
   ```bash
   curl http://localhost:8000/v1/messages \
     -H "Content-Type: application/json" \
     -H "x-api-key: any" \
     -d '{"model":"claude-opus-4-6","max_tokens":4096,"messages":[{"role":"user","content":"hello"}]}'
   ```
2. 验证响应格式符合 Anthropic 规范
3. 验证 content[0].type 是 "text"

---

### 步骤 3.2: 实现 /v1/messages 流式响应

**指示：**
1. 添加 stream=True 支持
2. 转换为 Anthropic SSE 格式：
   - 事件类型：`content_block_delta`, `message_delta`
   - 格式与 OpenAI 不同，注意区分
3. 处理 `message_stop` 事件

**测试：**
1. 测试流式输出
2. 验证事件类型正确
3. 验证内容拼接正确

---

## 阶段 4: 生产化完善

### 步骤 4.1: 添加日志系统

**指示：**
1. 配置 Python logging 模块
2. 在关键位置添加日志：
   - 登录成功/失败
   - API 请求开始/结束
   - 错误信息
3. 日志级别：INFO（正常）、ERROR（错误）
4. 日志格式包含时间戳

**测试：**
1. 启动服务并发送请求
2. 检查控制台日志输出
3. 验证每个请求都有对应的日志记录

---

### 步骤 4.2: 添加错误处理

**指示：**
1. 定义错误码映射：
   - 401: 认证失败
   - 500: 服务器错误
   - 400: 请求参数错误
2. 创建异常处理中间件
3. 捕获所有异常，返回标准格式

**测试：**
1. 测试无效的模型名
2. 测试空的 messages
3. 验证返回合适的 HTTP 状态码
4. 验证错误消息格式正确

---

### 步骤 4.3: 添加 token 自动重登录

**指示：**
1. 在 TaijiClient 添加 token 过期检测
2. 当收到 401 错误时自动重新登录
3. 更新保存的 token
4. 重试原请求

**测试：**
1. 手动使 token 失效（使用无效 token）
2. 发送请求
3. 验证自动重新登录成功
4. 验证第二次请求成功

---

### 步骤 4.4: 添加环境变量配置

**指示：**
1. 修改配置读取逻辑
2. 支持通过环境变量覆盖配置文件：
   - TAIJI_ACCOUNT
   - TAIJI_PASSWORD
   - TAIJI_API_BASE
3. 更新 .env.example 模板

**测试：**
1. 设置不同的环境变量
2. 启动服务
3. 验证使用环境变量中的值

---

### 步骤 4.5: 创建 Docker 配置

**指示：**
1. 创建 `Dockerfile`：
   - 基础镜像：python:3.11-slim
   - 安装依赖
   - 暴露 8000 端口
   - 启动命令

2. 创建 `docker-compose.yml`：
   - 定义服务
   - 配置环境变量
   - 配置端口映射

**测试：**
1. 构建 Docker 镜像
2. 运行 `docker-compose up`
3. 验证服务正常运行
4. 从宿主机访问 API 测试

---

### 步骤 4.6: 编写 README 文档

**指示：**
1. 创建 `README.md`，包含：
   - 项目简介
   - 功能特性
   - 快速开始（安装、配置、运行）
   - API 使用示例
   - 配置说明
   - Docker 部署指南

**测试：**
1. 按照 README 的步骤从零开始部署
2. 验证每一步都能成功执行

---

## 阶段 5: 集成测试

### 步骤 5.1: OpenAI SDK 兼容性测试

**指示：**
1. 安装 openai Python 库
2. 创建测试脚本，使用官方 SDK：
   ```python
   from openai import OpenAI
   client = OpenAI(base_url="http://localhost:8000/v1", api_key="any")
   response = client.chat.completions.create(...)
   ```
3. 测试流式和非流式

**测试：**
1. 运行测试脚本
2. 验证 SDK 可以正常调用
3. 验证响应解析正确

---

### 步骤 5.2: Anthropic SDK 兼容性测试

**指示：**
1. 安装 anthropic Python 库
2. 创建测试脚本：
   ```python
   from anthropic import Anthropic
   client = Anthropic(base_url="http://localhost:8000/v1", api_key="any")
   message = client.messages.create(...)
   ```
3. 测试流式和非流式

**测试：**
1. 运行测试脚本
2. 验证 SDK 可以正常调用

---

### 步骤 5.3: 压力测试

**指示：**
1. 使用 Locust 或类似工具
2. 配置并发用户数：10、50、100
3. 测试场景：连续发送 100 条消息
4. 记录响应时间和错误率

**测试：**
1. 运行压力测试
2. 分析结果
3. 确认错误率 < 1%
4. 确认平均响应时间 < 5 秒

---

## 阶段 6: 部署上线

### 步骤 6.1: 服务器准备

**指示：**
1. 选择服务器（推荐：有海外 IP 的 VPS）
2. 安装 Docker 和 Docker Compose
3. 配置防火墙开放 8000 端口

**测试：**
1. SSH 连接服务器
2. 验证 Docker 版本

---

### 步骤 6.2: 部署服务

**指示：**
1. 将代码上传到服务器（git clone 或 scp）
2. 配置 .env 文件
3. 运行 `docker-compose up -d`
4. 配置 Nginx 反向代理（可选）
5. 配置 SSL 证书（可选，使用 Let's Encrypt）

**测试：**
1. 从本地访问服务器 IP:8000
2. 测试 API 调用
3. 检查 Docker 日志

---

### 步骤 6.3: 监控配置

**指示：**
1. 配置日志轮转
2. 设置 Docker 自动重启策略
3. 配置健康检查

**测试：**
1. 重启服务器
2. 验证服务自动启动
3. 验证健康检查正常

---

## 完成标准

项目完成时应满足：

1. ✅ 可以通过 OpenAI SDK 调用 /v1/chat/completions
2. ✅ 可以通过 Anthropic SDK 调用 /v1/messages
3. ✅ 支持流式和非流式输出
4. ✅ 支持所有太极AI模型
5. ✅ 错误处理完善
6. ✅ 可以通过 Docker 一键部署
7. ✅ 有完整的 README 文档
8. ✅ 通过所有集成测试

---

## 预计时间

- 阶段 0: 30 分钟
- 阶段 1: 2-3 小时
- 阶段 2: 2-3 小时
- 阶段 3: 1-2 小时
- 阶段 4: 2-3 小时
- 阶段 5: 1-2 小时
- 阶段 6: 1-2 小时

**总计：约 10-16 小时**
