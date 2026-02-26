# 太极AI 转 API 服务 - 实施计划 v2.0

## 重大修正说明

**v2.0 主要变更**：修正了**会话状态管理**的致命漏洞，采用"每次请求即抛弃的新会话"策略，避免上下文污染。

---

## 项目概述

将太极AI (ai.aurod.cn) 的网页聊天能力封装为标准 API 服务，同时支持 OpenAI 和 Anthropic 两种格式。

---

## 附录 A: 太极AI 请求头规范（重要）

基于对 `crawler/` 目录下抓包文档的分析，太极AI 服务端对请求头有特定要求。以下是实现时**必须遵循**的请求头规范。

### 核心/必需请求头

| Header | 值 | 说明 | 重要性 |
|--------|-----|------|--------|
| `authorization` | `<JWT_TOKEN>` | 登录后获取的 JWT token（⚠️ 不需要 Bearer 前缀） | ⭐⭐⭐ 必需 |
| `x-app-version` | `2.14.0` | **应用版本号**，服务端可能据此做校验 | ⭐⭐⭐ 必需 |
| `content-type` | `application/json` | POST 请求内容类型 | ⭐⭐⭐ 必需 |
| `accept` | `application/json, text/plain, */*` | 接受的响应类型 | ⭐⭐⭐ 必需 |

### Cookie 管理

| Cookie | 说明 | 重要性 |
|--------|------|--------|
| `server_name_session` | 会话标识，与 authorization 配合使用 | ⭐⭐ 必需 |

**Cookie 处理建议**：

使用 `httpx.AsyncClient` 的 `cookies` 参数自动管理：

```python
class TaijiClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://ai.aurod.cn",
            headers=DEFAULT_HEADERS,
            cookies=httpx.Cookies()  # 自动存储 cookies
        )
        self.token = None

    async def login(self, account: str, password: str):
        response = await self.client.post(
            "/api/user/login",
            json={"account": account, "password": password, ...}
        )
        # httpx 会自动将响应中的 Set-Cookie 保存到 self.client.cookies
        self.token = response.json()["data"]["token"]
        # 更新 authorization header（⚠️ 太极AI 不需要 Bearer 前缀）
        self.client.headers["authorization"] = self.token
```

### 浏览器指纹请求头（反爬检测）

| Header | 示例值 | 说明 | 重要性 |
|--------|--------|------|--------|
| `user-agent` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...` | 浏览器标识 | ⭐⭐ 建议 |
| `sec-ch-ua` | `"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"` | 浏览器品牌 | ⭐ 建议 |
| `sec-ch-ua-mobile` | `?0` | 是否移动端 | ⭐ 建议 |
| `sec-ch-ua-platform` | `"Windows"` | 操作系统 | ⭐ 建议 |

### CORS 相关请求头

| Header | 值 | 说明 | 重要性 |
|--------|-----|------|--------|
| `origin` | `https://ai.aurod.cn` | 请求来源 | ⭐⭐ 建议 |
| `referer` | `https://ai.aurod.cn/chat` | 来源页面 | ⭐⭐ 建议 |
| `sec-fetch-dest` | `empty` | 请求目标 | ⭐ 建议 |
| `sec-fetch-mode` | `cors` | 请求模式 | ⭐ 建议 |
| `sec-fetch-site` | `same-origin` | 站点关系 | ⭐ 建议 |

### 流式请求特殊请求头

| Header | 值 | 说明 | 使用场景 |
|--------|-----|------|----------|
| `accept` | `text/event-stream` | SSE 流式响应 | 流式请求时覆盖默认值 |

### 推荐的默认请求头配置

```python
DEFAULT_HEADERS = {
    # 核心/必需
    "authorization": None,  # 动态设置
    "x-app-version": "2.14.0",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",

    # 浏览器指纹（避免反爬）
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',

    # CORS 相关
    "origin": "https://ai.aurod.cn",
    "referer": "https://ai.aurod.cn/chat",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",

    # 优先级
    "priority": "u=1, i",
}
```

### 实现注意事项

1. **x-app-version 是关键**：服务端可能根据此 Header 做版本校验或兼容性控制
2. **Cookie 存储**：需要持久化 `server_name_session`，建议使用 `httpx.Cookies` 或类似机制
3. **流式请求**：记得将 `accept` 头改为 `text/event-stream`
4. **登录接口**：需要 `origin` 和 `referer` 头
5. **文件上传**：太极AI 支持图片等文件，需要正确处理 base64 编码

### 文件上传格式

太极AI 的文件上传是通过在 `/api/chat/completions` 请求的 `files` 字段中传递：

```python
# 图片文件格式
files = [{
    "name": "image.png",           # 文件名
    "data": "data:image/png;base64,iVBORw0KG..."  # base64 data URL
}]

# 请求体
request_body = {
    "text": "这张图片是什么？",
    "sessionId": 123456,
    "files": files
}
```

**支持的图片格式**：基于分析，太极AI 应支持常见图片格式（PNG、JPG、WebP 等）。

---

## 附录 B: 太极AI API 参考

基于抓包文档的完整 API 端点列表。

### 认证相关

| 端点 | 方法 | 说明 | 请求体 |
|------|------|------|--------|
| `/api/user/login` | POST | 用户登录 | `{"account":"","password":"","code":"","captcha":"","invite":"","agreement":true}` |
| `/api/user/info` | GET | 获取用户信息 | - |

### 模型与会话

| 端点 | 方法 | 说明 | 请求体 |
|------|------|------|--------|
| `/api/chat/tmpl` | GET | 获取可用模型列表 | - |
| `/api/chat/session` | POST | 创建新会话 | `{"model":"gpt-4.1-mini","plugins":[],"mcp":[]}` |
| `/api/chat/session` | GET | 获取会话列表 | `?page=1` |
| `/api/chat/session/{id}` | PUT | 更新会话配置 | `{"id":123,"model":"gpt-4.1-mini",...}` |
| `/api/chat/session/{id}` | DELETE | 删除会话 | - |

### 聊天相关

| 端点 | 方法 | 说明 | 请求体 |
|------|------|------|--------|
| `/api/chat/completions` | POST | 发送消息（SSE流式） | `{"text":"","sessionId":123,"files":[]}` |
| `/api/chat/record/{sessionId}` | GET | 获取会话消息记录 | `?page=1` |

### 其他

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/notice` | GET | 获取公告 | `?size=3&page=1&detail=true` |

### 响应格式说明

**成功响应**（统一格式）：
```json
{
    "code": 0,
    "data": { ... },
    "msg": ""
}
```

**错误响应**：
```json
{
    "code": 非0值,
    "data": null,
    "msg": "错误信息"
}
```

**SSE 流式响应格式**：
```
data: {"type":"string","code":0,"data":"Hello","msg":""}

data: {"type":"string","code":0,"data":" World","msg":""}

data: {"type":"object","code":0,"data":{"promptTokens":10,"completionTokens":5,"useTokens":15,"model":"gpt-4.1-mini","taskId":"..."},"msg":""}

data: [DONE]
```

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
   - aiofiles

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
   ```yaml
   taiji:
     api_base: https://ai.aurod.cn
     account: your_account
     password: your_password
     app_version: 2.14.0  # 应用版本号，请求头需要

   server:
     host: 0.0.0.0
     port: 8000

   limits:
     max_concurrent: 5  # 全局并发限制
   ```

2. 创建 `.env` 文件（用于敏感信息，加入 .gitignore）

3. 创建 `.env.example` 作为模板

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
   - **关键请求头**（参考附录 A）：
     ```python
     headers = {
         "accept": "application/json, text/plain, */*",
         "content-type": "application/json",
         "x-app-version": "2.14.0",
         "origin": "https://ai.aurod.cn",
         "referer": "https://ai.aurod.cn/auth",
     }
     ```
   - 解析响应获取 token
   - 保存 token 到类属性中
   - 保存响应中的 cookies（特别是 `server_name_session`）

3. 创建 `src/models/auth.py` 定义登录请求/响应的数据模型：
   ```python
   class LoginRequest(BaseModel):
       account: str
       password: str
       code: str = ""
       captcha: str = ""
       invite: str = ""
       agreement: bool = True

   class LoginResponse(BaseModel):
       code: int
       data: Optional[TokenData]
       msg: str

   class TokenData(BaseModel):
       token: str
       email: str
       phone: str
       role: str
   ```

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
3. **关键请求头**：
   ```python
   headers = {
       "accept": "application/json, text/plain, */*",
       "authorization": self.token,  # ⚠️ 不需要 Bearer 前缀！
       "x-app-version": "2.14.0",
       "referer": "https://ai.aurod.cn/chat",
   }
   ```
4. 解析响应，提取 models 数组
5. **响应格式修正**（2025-02-26 验证）：
   ```python
   # data 可能是 dict 或 list，需要处理两种情况
   raw_data = response["data"]
   if isinstance(raw_data, dict) and "models" in raw_data:
       models = raw_data["models"]  # 实际模型列表
   elif isinstance(raw_data, list):
       models = raw_data
   else:
       models = []
   ```

**测试：**
1. 创建 `tests/test_models.py`
2. 调用函数并打印模型数量
3. 验证：
   - 至少返回 50+ 个模型
   - 每个模型有 label 和 value 字段
   - 确认包含 "gpt-4.1-mini" 和 "claude-opus-4-6"

---

### 步骤 1.3: 实现新建会话（修正）

**指示：**
1. 在 `taiji_client.py` 添加 `create_session(model)` 函数
2. 发送 POST 请求到 `/api/chat/session`
3. **关键请求头**：
   ```python
   headers = {
       "accept": "application/json, text/plain, */*",
       "authorization": self.token,  # ⚠️ 不需要 Bearer 前缀
       "content-type": "application/json",
       "x-app-version": "2.14.0",
       "origin": "https://ai.aurod.cn",
       "referer": "https://ai.aurod.cn/chat",
   }
   ```
4. 请求体：`{"model": model_name, "plugins": [], "mcp": []}`
5. 解析响应，返回 session_id（响应 data 中的 id 字段）

**注意**：此函数将在每次 API 请求时被调用，创建独立的会话。

**测试：**
1. 创建测试函数
2. 用 "gpt-4.1-mini" 创建会话
3. 验证返回的 session_id 是数字类型
4. 连续创建 3 个会话，确认每个 id 不同

---

### 步骤 1.4: 实现删除会话（新增）

**指示：**
1. 在 `taiji_client.py` 添加 `delete_session(session_id)` 函数
2. 发送 **DELETE** 请求到 `/api/chat/session/{session_id}`
3. **关键请求头**：
   ```python
   headers = {
       "accept": "application/json, text/plain, */*",
       "authorization": self.token,  # ⚠️ 不需要 Bearer 前缀
       "x-app-version": "2.14.0",
       "origin": "https://ai.aurod.cn",
       "referer": "https://ai.aurod.cn/chat?_userMenuKey=chat",
   }
   ```
4. 验证响应 code == 0

**API 确认**（基于抓包）：
```
DELETE /api/chat/session/{id}
响应: {"code":0,"data":null,"msg":""}
```

**目的**：防止太极AI 网页端堆积数万个会话。

**测试：**
1. 创建会话后调用删除
2. 在网页端验证会话已消失
3. 验证响应 code 为 0

---

### 步骤 1.5: 实现 Messages 数组转换为 Prompt + 图片提取（新增 - 关键）

**指示：**
1. 在 `src/utils/` 创建 `message_converter.py`
2. 创建 `convert_openai_messages(messages, model)` 函数
3. 处理 OpenAI messages 数组格式，返回：
   ```python
   {
       "text": "转换后的文本 prompt",
       "files": [{"name": "image.png", "data": "data:image/png;base64,..."}]  # 可选
   }
   ```

4. 处理规则：

   **A. 文本消息处理**：
   - system 消息转换为 "系统提示：{content}"
   - user 消息转换为 "用户：{content}"
   - assistant 消息转换为 "助手：{content}"
   - 用换行符连接

   **B. 图片消息处理**（Vision 支持）：

   OpenAI Vision 格式：
   ```json
   {
       "role": "user",
       "content": [
           {"type": "text", "text": "这是什么？"},
           {"type": "image_url", "image_url": {"url": "https://..."}}
       ]
   }
   ```

   需要提取图片并转换为太极AI 格式：
   ```json
   {
       "text": "这是什么？",
       "files": [
           {
               "name": "image.png",
               "data": "data:image/png;base64,iVBORw0KG..."
           }
       ]
   }
   ```

   **C. 图片 URL 处理**：
   - 如果是 base64 URL（`data:image/...`）→ 直接使用
   - 如果是 HTTP URL → 需要下载并转换为 base64

5. **特殊处理**：如果 messages 只有最后一条 user 消息且无图片，直接返回

**测试：**
1. 测试只有一条 text 消息的情况
2. 测试包含 system 的多轮对话
3. 测试包含图片的消息（content 为数组）
4. 测试同时有文本和图片的情况
5. 验证转换后的格式正确

---

### 步骤 1.6: 实现发送消息（非流式，返回完整数据）

**指示：**
1. 在 `taiji_client.py` 添加 `send_message(session_id, text, files=None)` 函数
2. 发送 POST 请求到 `/api/chat/completions`
3. 请求体：{"text": text, "sessionId": session_id, "files": files or []}
4. **关键请求头**：
   ```python
   headers = {
       "accept": "text/event-stream",  # SSE 流式响应
       "authorization": self.token,  # ⚠️ 不需要 Bearer 前缀
       "content-type": "application/json",
       "x-app-version": "2.14.0",
       "referer": "https://ai.aurod.cn/chat",
   }
   ```
5. 读取完整的 SSE 响应：
   - 拼接所有 "string" 类型的 data 为完整文本
   - 保存最后一个 "object" 类型的 data（包含 token 信息）
6. **重要**：检查每个数据块的 code 字段，如果不为 0，表示错误
7. 返回包含文本和 token 数的字典：
   ```python
   return {
       "text": full_response_text,      # 完整回复文本
       "promptTokens": data["promptTokens"],      # 从最后一个 object 获取
       "completionTokens": data["completionTokens"],
       "useTokens": data["useTokens"],
       "model": data["model"],
       "taskId": data["taskId"]
   }
   ```

**测试：**
1. 创建测试函数
2. 流程：登录 → 创建会话 → 发送 "hello"
3. 验证：
   - 收到多个 SSE 数据块
   - 最后一个块的 type 是 "object"
   - code 字段为 0（成功）
   - 返回的字典包含 text 和 token 数
   - 打印完整回复内容和 token 数

---

### 步骤 1.7: 实现发送消息（流式，带断开处理）

**指示：**
1. 修改 `send_message()` 函数，添加 `stream=True` 参数
2. 当 stream=True 时，返回一个异步生成器
3. 每收到一个 SSE 数据块就 yield 一次
4. 处理 `[DONE]` 标记，停止生成
5. **关键**：添加客户端断开处理：
   ```python
   async def stream_generator():
       async with httpx.AsyncClient() as client:
           try:
               async with client.stream(...) as response:
                   async for chunk in response.aiter_lines():
                       if chunk.strip():
                           data = parse_sse(chunk)
                           if check_error(data):  # 检查错误码
                               raise HTTPException(...)
                           yield format_openai(data)
           except asyncio.CancelledError:
               # 客户端断开连接，清理资源
               logger.info("Client disconnected")
               raise
           finally:
               # 确保关闭 httpx 连接
               pass
   ```

**测试：**
1. 创建异步测试函数
2. 用 for 循环遍历流式响应
3. 验证：
   - 每次迭代收到一个文本片段
   - 片段按顺序拼接是完整回复
   - 最后正确结束循环
4. 测试中途断开连接的情况

---

### 步骤 1.8: 实现 Token 自动重登录（修正）

**指示：**
1. 在 `taiji_client.py` 添加装饰器或中间件
2. 捕获 401 错误
3. 自动调用 `login()` 重新获取 token
4. 更新类属性中的 token
5. **关键**：重试原请求，最多重试 1 次
6. 如果重试后仍然失败，抛出异常

**测试：**
1. 手动使 token 失效（使用无效 token）
2. 发送请求
3. 验证自动重新登录成功
4. 验证第二次请求成功

---

### 步骤 1.9: 创建全局并发限制（新增）

**指示：**
1. 在 `src/utils/` 创建 `concurrency.py`
2. 创建全局 `asyncio.Semaphore` 实例：
   ```python
   # 全局单例
   _semaphore = None

   def get_semaphore():
       global _semaphore
       if _semaphore is None:
           _semaphore = asyncio.Semaphore(5)  # 最多 5 个并发
       return _semaphore
   ```

3. 在 `taiji_client.py` 中使用：
   ```python
   async def send_message(...):
       semaphore = get_semaphore()
       async with semaphore:
           # 实际的请求逻辑
   ```

**测试：**
1. 同时发送 10 个请求
2. 验证最多同时有 5 个在执行
3. 验证所有请求最终都完成

---

## 阶段 2: OpenAI 兼容接口

### 步骤 2.1: 搭建 FastAPI 基础框架

**指示：**
1. 在项目根目录创建 `main.py`
2. 初始化 FastAPI 应用
3. 添加健康检查端点 `GET /`
4. 添加 CORS 中间件，允许所有来源
5. 配置 lifespan 函数，在启动时登录太极AI

**测试：**
1. 启动服务：`python main.py` 或 `uvicorn main:app --reload`
2. 访问 http://localhost:8000
3. 验证返回 {"status": "ok"} 或类似消息
4. 访问 http://localhost:8000/docs 查看自动生成的 API 文档

---

### 步骤 2.2: 实现请求/响应数据模型

**指示：**
1. 在 `src/models/` 创建 `openai_request.py`
2. 定义 Pydantic 模型：
   ```python
   class ChatMessage(BaseModel):
       role: str
       content: str

   class ChatCompletionRequest(BaseModel):
       model: str
       messages: List[ChatMessage]
       stream: bool = False
       temperature: Optional[float] = None
       max_tokens: Optional[int] = None
   ```

3. 在 `src/models/openai_response.py` 定义响应模型：
   ```python
   class ChatCompletionResponse(BaseModel):
       id: str
       object: str = "chat.completion"
       created: int
       model: str
       choices: List[Choice]
       usage: Usage

   class Choice(BaseModel):
       index: int = 0
       message: ChatMessage
       finish_reason: str
   ```

**测试：**
1. 尝试创建请求对象
2. 验证 Pydantic 验证正常工作
3. 测试无效输入会报错

---

### 步骤 2.3: 实现 /v1/chat/completions 路由（非流式，修正版）

**指示：**
1. 在 `src/api/` 创建 `openai.py`
2. 创建路由函数：
   ```python
   @router.post("/v1/chat/completions")
   async def chat_completions(request: ChatCompletionRequest):
       # 1. 每次请求创建新的会话
       session_id = await taiji_client.create_session(request.model)

       try:
           # 2. 将 messages 数组转换为 prompt
           prompt = messages_to_prompt(request.messages)

           # 3. 发送消息
           response_text = await taiji_client.send_message(
               session_id=session_id,
               text=prompt,
               stream=False
           )

           # 4. 获取太极AI 返回的完整数据（包含真实 token 数）
           # 注意：send_message 需要返回完整的数据对象，而不只是文本
           taiji_response = await taiji_client.send_message(...)

           # 5. 转换为 OpenAI 格式返回
           return {
               "id": f"chatcmpl-{uuid4().hex}",
               "object": "chat.completion",
               "created": int(time.time()),
               "model": request.model,
               "choices": [{
                   "index": 0,
                   "message": {
                       "role": "assistant",
                       "content": taiji_response["text"]
                   },
                   "finish_reason": "stop"
               }],
               "usage": {
                   # 使用太极AI 返回的真实 token 数
                   "prompt_tokens": taiji_response.get("promptTokens", 0),
                   "completion_tokens": taiji_response.get("completionTokens", 0),
                   "total_tokens": taiji_response.get("useTokens", 0)
               }
           }
       finally:
           # 5. 清理会话（防止堆积）
           await taiji_client.delete_session(session_id)
   ```

**测试：**
1. 使用 curl 测试：
   ```bash
   curl http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}]}'
   ```
2. 验证响应格式符合 OpenAI 规范
3. 验证 choices[0].message.content 包含 AI 回复
4. 测试多轮对话：发送包含 4 条消息的请求

---

### 步骤 2.4: 实现 /v1/chat/completions 流式响应（修正版）

**指示：**
1. 修改路由函数，支持 stream=True
2. 当 stream=True 时，返回 StreamingResponse
3. **关键**：先检查第一个数据块是否为错误：
   ```python
   async def stream_openai_format(request):
       session_id = await taiji_client.create_session(request.model)
       prompt = messages_to_prompt(request.messages)

       try:
           # 获取流式生成器
           stream = taiji_client.send_message(
               session_id=session_id,
               text=prompt,
               stream=True
           )

           first_chunk = True
           async for chunk in stream:
               # 第一块数据检查错误
               if first_chunk:
                   if is_error_response(chunk):
                       raise HTTPException(
                           status_code=400,
                           detail=f"太极AI错误: {chunk['msg']}"
                       )
                   first_chunk = False

               # 转换为 OpenAI SSE 格式
               yield f"data: {json.dumps(format_openai_chunk(chunk))}\n\n"

           # 发送结束标记
           yield "data: [DONE]\n\n"

       except asyncio.CancelledError:
           logger.info("Client disconnected during streaming")
           raise
       finally:
           await taiji_client.delete_session(session_id)
   ```

**测试：**
1. 用 curl 测试流式：
   ```bash
   curl http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4.1-mini","messages":[{"role":"user","content":"hello"}],"stream":true}'
   ```
2. 验证每个数据块格式正确
3. 验证最后有 [DONE] 标记
4. 测试中途断开连接（Ctrl+C）

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
       {"id": "gpt-4.1-mini", "object": "model", "owned_by": "taiji"},
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
   ```python
   class AnthropicMessage(BaseModel):
       role: str
       content: str

   class AnthropicRequest(BaseModel):
       model: str
       max_tokens: int = 4096
       messages: List[AnthropicMessage]
       system: Optional[str] = None
       stream: bool = False
   ```

3. 实现路由逻辑，复用 TaijiClient
4. 转换为 Anthropic 格式返回

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
   - 事件类型：`content_block_delta`, `message_stop`
3. 处理客户端断开

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
   - 客户端断开连接
3. 日志级别：INFO（正常）、ERROR（错误）
4. 日志格式包含时间戳和请求 ID

**测试：**
1. 启动服务并发送请求
2. 检查控制台日志输出
3. 验证每个请求都有对应的日志记录

---

### 步骤 4.2: 添加错误处理

**指示：**
1. 定义错误码映射：
   - 401: 认证失败
   - 429: 请求过于频繁
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

### 步骤 4.3: 添加环境变量配置

**指示：**
1. 修改配置读取逻辑
2. 支持通过环境变量覆盖配置文件：
   - TAIJI_ACCOUNT
   - TAIJI_PASSWORD
   - TAIJI_API_BASE
   - MAX_CONCURRENT

**测试：**
1. 设置不同的环境变量
2. 启动服务
3. 验证使用环境变量中的值

---

### 步骤 4.4: 创建 Docker 配置

**指示：**
1. 创建 `Dockerfile`：
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. 创建 `docker-compose.yml`：
   ```yaml
   services:
     web2api:
       build: .
       environment:
         - TAIJI_ACCOUNT=${TAIJI_ACCOUNT}
         - TAIJI_PASSWORD=${TAIJI_PASSWORD}
       ports:
         - "8000:8000"
   ```

**测试：**
1. 构建 Docker 镜像
2. 运行 `docker-compose up`
3. 验证服务正常运行
4. 从宿主机访问 API 测试

---

### 步骤 4.5: 编写 README 文档

**指示：**
1. 创建 `README.md`，包含：
   - 项目简介
   - 功能特性
   - 快速开始（安装、配置、运行）
   - API 使用示例
   - 配置说明
   - Docker 部署指南
   - 注意事项（频率限制、会话管理等）

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

   # 测试非流式
   response = client.chat.completions.create(
       model="gpt-4.1-mini",
       messages=[{"role": "user", "content": "hello"}]
   )

   # 测试流式
   stream = client.chat.completions.create(
       model="gpt-4.1-mini",
       messages=[{"role": "user", "content": "hello"}],
       stream=True
   )
   for chunk in stream:
       print(chunk.choices[0].delta.content or "", end="")
   ```

3. 测试多轮对话

**测试：**
1. 运行测试脚本
2. 验证 SDK 可以正常调用
3. 验证多轮对话上下文正确传递

---

### 步骤 5.2: Anthropic SDK 兼容性测试

**指示：**
1. 安装 anthropic Python 库
2. 创建测试脚本：
   ```python
   from anthropic import Anthropic
   client = Anthropic(
       base_url="http://localhost:8000/v1",
       api_key="any"
   )
   message = client.messages.create(
       model="claude-opus-4-6",
       max_tokens=1024,
       messages=[{"role": "user", "content": "hello"}]
   )
   ```

**测试：**
1. 运行测试脚本
2. 验证 SDK 可以正常调用

---

### 步骤 5.3: 上下文隔离测试（新增 - 关键）

**指示：**
1. 创建测试脚本，模拟两个同时进行的对话：
   ```python
   import asyncio

   async def conversation_1():
       client = OpenAI(...)
       # 对话 A：询问 Python
       response = client.chat.completions.create(
           model="gpt-4.1-mini",
           messages=[
               {"role": "user", "content": "我叫小红，我喜欢编程"}
           ]
       )
       # 然后问：我叫什么名字？

   async def conversation_2():
       client = OpenAI(...)
       # 对话 B：询问烹饪
       response = client.chat.completions.create(
           model="gpt-4.1-mini",
           messages=[
               {"role": "user", "content": "我想学做菜"}
           ]
       )
       # 然后问：我想学什么？

   # 同时运行
   await asyncio.gather(conversation_1(), conversation_2())
   ```

2. 验证：
   - 对话 A 的回答是"小红"（不是"做菜"）
   - 对话 B 的回答是"做菜"（不是"小红"）
   - 两个对话没有串线

**测试：**
1. 运行测试脚本
2. 验证上下文完全隔离
3. 如果发现串线，说明会话管理有 bug

---

### 步骤 5.4: 压力测试

**指示：**
1. 使用 Locust 或类似工具
2. 配置并发用户数：5、10、20
3. 测试场景：连续发送 100 条消息
4. 记录响应时间和错误率

**测试：**
1. 运行压力测试
2. 分析结果
3. 确认错误率 < 1%
4. 确认平均响应时间 < 5 秒
5. 确认没有上下文串线

---

## 阶段 6: 部署上线

### 步骤 6.1: 服务器准备

**指示：**
1. 选择服务器（推荐：有稳定网络的服务器）
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
5. ✅ **多轮对话上下文正确传递**（关键）
6. ✅ **不同会话完全隔离，无串线**（关键）
7. ✅ **客户端断开时正确停止消耗**（关键）
8. ✅ 错误处理完善
9. ✅ 可以通过 Docker 一键部署
10. ✅ 有完整的 README 文档
11. ✅ 通过所有集成测试

---

## 预计时间

- 阶段 0: 30 分钟
- 阶段 1: 3-4 小时（增加了关键步骤）
- 阶段 2: 2-3 小时
- 阶段 3: 1-2 小时
- 阶段 4: 2-3 小时
- 阶段 5: 2-3 小时（增加了上下文隔离测试）
- 阶段 6: 1-2 小时

**总计：约 12-20 小时**

---

## v2.0 主要修正总结

| 修正点 | 原方案 | 新方案 |
|--------|--------|--------|
| 会话管理 | 复用 session_id 字典 | **每次请求创建新会话** |
| 历史消息 | 依赖太极AI 维护 | **将 messages 数组转为 prompt** |
| 会话清理 | 无 | **请求结束后删除会话** |
| 客户端断开 | 未处理 | **捕获 CancelledError** |
| 错误检测 | 未检查 | **先 peek 第一块数据** |
| 并发限制 | 局部 Semaphore | **全局单例 Semaphore** |
| 上下文测试 | 无 | **新增隔离测试** |
| 请求头管理 | 未详细说明 | **新增请求头规范附录** |
| Cookie 管理 | 未处理 | **自动管理 server_name_session** |
