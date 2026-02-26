# 待确认功能清单

## 已确认功能

### ✅ 1. Vision（图片理解）- 已确认

**确认时间**：2026-02-26

**支持情况**：
- ✅ 模型属性中 `multimodal: true`
- ✅ 支持图片上传（PNG、JPEG 等）
- ✅ 使用 Base64 Data URI 格式
- ❌ 不支持文档文件（PDF、Word 等）

**格式确认**（来自 `crawler/chat/chat4api-2.md`）：
```json
{
  "text": "描述这张图片",
  "sessionId": 462993,
  "files": [
    {
      "name": "Bean.png",
      "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}
```

**OpenAI 格式转换**：
- 输入：`content: [{"type": "text", ...}, {"type": "image_url", ...}]`
- 输出：`text` + `files: [{name, data}]`
- HTTP URL 图片需要下载并转为 base64

---

## 需要进一步抓包确认的功能

---

### 2. Usage Token 计算优化 - 中优先级

**当前计划**：
```python
"usage": {
    "prompt_tokens": estimate_tokens(prompt),
    "completion_tokens": estimate_tokens(response_text),
    "total_tokens": estimate_tokens(prompt + response_text)
}
```

**问题**：
- `estimate_tokens` 只是估算（按字符数除以系数）
- 不够准确

**优化方案**：

#### 方案 A：使用 tiktoken（推荐）
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

#### 方案 B：简单正则（轻量级）
```python
import re

def count_tokens_approx(text: str) -> int:
    # 中文字符约等于 1 token
    # 英文单词约等于 0.25 token
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english // 4
```

#### 方案 C：使用太极AI 返回的真实值
如果太极AI 在 SSE 的最后一块数据中返回了真实的 token 数：
```json
{
  "type": "object",
  "data": {
    "promptTokens": 273,
    "completionTokens": 314,
    "useTokens": 587  // 总 token
  }
}
```

**最优方案**：优先使用太极AI 返回的真实值，如果没有则用 tiktoken。

---

### 3. Tool Calling（函数调用）- 低优先级

**当前状态**：
- ✅ 架构预留了 `plugins`、`mcp` 字段
- ❌ 但所有模型的 `plugin: false`
- ❌ 不清楚是否真正支持

**需要确认**：
- 网页端是否有相关功能入口
- 是否需要特殊配置或权限

---

## 实施优先级

| 功能 | 优先级 | 是否阻塞主流程 |
|------|--------|----------------|
| 核心对话功能 | P0 | ✅ 必需 |
| Vision（图片理解） | P1 | ⚠️ 可后续添加 |
| Usage Token 优化 | P2 | ❌ 不阻塞 |
| Tool Calling | P3 | ❌ 可选 |

---

## 建议实施方式

### 阶段 1：核心功能（立即实施）
- ✅ 登录
- ✅ 获取模型列表
- ✅ 创建会话
- ✅ 发送消息（纯文本）
- ✅ 删除会话
- ✅ OpenAI/Anthropic 接口

### 阶段 2：Vision 支持（待抓包确认后）
- ❓ 等你提供图片上传的抓包
- ✅ 实现图片上传功能
- ✅ 支持 base64 格式
- ✅ OpenAI vision format 转换

### 阶段 3：优化改进（可选）
- ✅ 使用 tiktoken 优化 token 计算
- ✅ 使用太极AI 返回的真实 token 数
- ✅ 添加缓存机制

---

## 下一步

请你帮忙完成以下**抓包任务**：

### 任务 1：图片上传抓包（最重要）

1. 打开太极AI 网页
2. 上传一张图片（.jpg 或 .png）
3. 发送消息："描述这张图片"
4. 在 Network 中找到发送消息的请求
5. 记录 `files` 字段的完整格式
6. 保存到 `crawler/vision/image_upload.md`

### 任务 2：确认 token 返回值

1. 查看发送消息后的 SSE 响应
2. 最后一个 `type: "object"` 的数据块
3. 确认是否包含：
   - `promptTokens`
   - `completionTokens`
   - `useTokens`

---

完成后，我会更新实施计划，添加 Vision 支持和 Usage 优化。
