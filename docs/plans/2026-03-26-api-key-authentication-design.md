# API Key 鉴权设计

## 1. 目标

为所有 API 端点添加一层访问控制，防止未授权访问。通过静态配置的 API Key 白名单进行校验。

## 2. 方案

### 中间件校验

新增 FastAPI 中间件 `ApiKeyAuthMiddleware`，在请求处理前校验 `X-API-Key` 请求头。

- 请求头存在且匹配白名单 → 通过，继续处理
- 请求头存在但不匹配 → 返回 401
- 请求头不存在但 `api_keys` 配置为空 → 通过（向后兼容）

### 配置项

在 `Settings` 中新增字段：

```python
api_keys: list[str] = Field(default=[], description="API Key 白名单，空列表表示不启用鉴权")
```

配置来源优先级：环境变量 `WEB2API_API_KEYS` > 配置文件 `api.api_keys`

环境变量支持逗号分隔多个 key：
```
WEB2API_API_KEYS=key1,key2,key3
```

### 请求头规范

客户端请求时需在 HTTP 头中携带：
```
X-API-Key: <配置的key>
```

### 错误响应

校验失败时返回 401：
```json
{
  "error": {
    "code": "auth_failed",
    "message": "Invalid or missing API key.",
    "status": 401,
    "request_id": "<request-id>"
  },
  "detail": "Invalid or missing API key."
}
```

### 豁免路径

以下路径跳过鉴权（可选，后续按需扩展）：
- `/metrics` — Prometheus 监控端点
- `/stats` — 统计信息端点

## 3. 文件变更

| 文件 | 操作 |
|------|------|
| `src/utils/settings.py` | 新增 `api_keys` 配置项 |
| `src/middleware/api_key.py` | 新增鉴权中间件 |
| `src/middleware/__init__.py` | 导出中间件 |
| `src/__init__.py` | 注册中间件 |

## 4. 测试

- 单元测试：无 key 配置时请求正常通过
- 单元测试：配置 key 后请求无 key 返回 401
- 单元测试：配置 key 后请求带正确 key 通过
- 单元测试：配置 key 后请求带错误 key 返回 401

## 5. 向后兼容

- `api_keys` 默认为空列表
- 空列表时不进行任何校验
- 不影响现有启动和调用方式
