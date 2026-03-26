# API Key 鉴权实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为所有 API 端点添加 API Key 鉴权，通过中间件校验 `X-API-Key` 请求头。

**Architecture:** 新增 FastAPI 中间件 `ApiKeyAuthMiddleware`，基于白名单校验请求头。配置项 `api_keys` 默认为空列表，空列表时不启用鉴权（向后兼容）。

**Tech Stack:** FastAPI Middleware, Pydantic Settings, Starlette

---

## Task 1: 添加配置项

**Files:**
- Modify: `src/utils/settings.py:64-69` — 在 `Settings` 类中添加 `api_keys` 字段
- Modify: `src/utils/settings.py:180-181` — 在配置加载逻辑中添加 api_keys 解析
- Modify: `tests/test_phase4_settings.py` — 添加配置加载测试

**Step 1: 添加测试用例**

在 `tests/test_phase4_settings.py` 中添加：

```python
def test_load_settings_with_api_keys():
    """测试 api_keys 配置项加载"""
    import tempfile, yaml
    config = {"api": {"api_keys": ["key1", "key2"]}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.safe_dump(config, f)
        f.flush()
        from src.utils.settings import load_settings
        settings = load_settings(config_path=Path(f.name), load_env_file=False)
    assert settings.api_keys == ["key1", "key2"]

def test_load_settings_api_keys_from_env():
    """测试环境变量配置 api_keys"""
    import os
    os.environ["WEB2API_API_KEYS"] = "env_key1,env_key2"
    try:
        from src.utils.settings import load_settings
        settings = load_settings(load_env_file=False)
        assert settings.api_keys == ["env_key1", "env_key2"]
    finally:
        del os.environ["WEB2API_API_KEYS"]
```

**Step 2: 添加配置字段**

在 `src/utils/settings.py` 的 `Settings` 类中，`monitoring_enabled` 字段后添加：

```python
    # API 鉴权配置
    api_keys: list[str] = Field(default=[], description="API Key 白名单，空列表表示不启用鉴权")
```

**Step 3: 添加配置加载逻辑**

在 `load_settings` 函数的监控配置块后（大约第 262 行）添加：

```python
    # API 鉴权配置
    api_section = _get_section(config, "api")
    if api_keys_raw := _normalize_text(api_section.get("api_keys")):
        # 支持逗号分隔的字符串
        settings_dict["api_keys"] = [k.strip() for k in api_keys_raw.split(",") if k.strip()]
```

同时在函数开头 `with suppress(Exception):` 块前添加环境变量读取：

```python
    # API 鉴权配置（从环境变量）
    api_keys_env = _normalize_text(os.getenv("WEB2API_API_KEYS"))
    if api_keys_env:
        settings_dict["api_keys"] = [k.strip() for k in api_keys_env.split(",") if k.strip()]
```

**Step 4: 运行测试验证**

```bash
cd D:\Work\code\web2api && python -m pytest tests/test_phase4_settings.py -v
```

---

## Task 2: 编写鉴权中间件

**Files:**
- Create: `src/middleware/api_key.py` — 新增鉴权中间件
- Modify: `src/middleware/__init__.py` — 导出中间件

**Step 1: 创建中间件文件**

```python
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.utils.settings import get_settings


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key 鉴权中间件"""

    EXEMPT_PATHS = {"/metrics", "/stats", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # 豁免路径
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        settings = get_settings()
        api_keys = settings.api_keys

        # 空列表 = 不启用鉴权
        if not api_keys:
            return await call_next(request)

        # 获取请求头中的 API Key
        provided_key = request.headers.get("x-api-key")
        if not provided_key:
            return _unauthorized_response(request, "Missing API key.")

        if provided_key not in api_keys:
            return _unauthorized_response(request, "Invalid API key.")

        return await call_next(request)


def _unauthorized_response(request: Request, message: str) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    return JSONResponse(
        status_code=401,
        content={
            "error": {
                "code": "auth_failed",
                "message": message,
                "status": 401,
                "request_id": request_id,
            },
            "detail": message,
        },
        headers={"WWW-Authenticate": "ApiKey"},
    )
```

**Step 2: 更新 middleware __init__.py**

```python
from src.middleware.request_middleware import RequestContextAndErrorMiddleware
from src.middleware.api_key import ApiKeyAuthMiddleware

__all__ = ["RequestContextAndErrorMiddleware", "ApiKeyAuthMiddleware"]
```

**Step 3: 验证语法正确**

```bash
cd D:\Work\code\web2api && python -c "from src.middleware.api_key import ApiKeyAuthMiddleware; print('OK')"
```

---

## Task 3: 注册中间件

**Files:**
- Modify: `src/__init__.py` — 注册中间件到应用

**Step 1: 查看当前 main.py 或应用入口**

```bash
cat D:\Work\code\web2api\main.py
```

根据入口文件，在 `RequestContextAndErrorMiddleware` 注册后添加 `ApiKeyAuthMiddleware`。

典型 FastAPI 应用结构：
```python
app.add_middleware(RequestContextAndErrorMiddleware)
app.add_middleware(ApiKeyAuthMiddleware)  # 新增
```

**Step 2: 验证中间件注册成功**

```bash
cd D:\Work\code\web2api && python -c "from main import app; print('Middleware registered:', [m.__name__ for m in app.user_middleware])"
```

---

## Task 4: 编写集成测试

**Files:**
- Create: `tests/test_api_key_auth.py` — API Key 鉴权集成测试

**Step 1: 编写测试用例**

```python
from fastapi.testclient import TestClient
from main import app


def test_no_auth_when_keys_empty():
    """无 key 配置时请求正常通过"""
    import os, tempfile, yaml
    from src.utils.settings import _settings, load_settings

    # 临时配置：无 api_keys
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.safe_dump({"taiji": {}, "server": {}, "monitoring": {"enabled": False}}, f)
        f.flush()
        settings = load_settings(config_path=Path(f.name), load_env_file=False)

    client = TestClient(app)
    # 假设 /v1/models 是有效端点
    # 实际项目中替换为真实端点或 mock
    # 这里测试中间件不会拦截
    response = client.get("/v1/models")
    # 由于无鉴权配置，响应不会是 401（具体取决于后端是否可用）


def test_missing_api_key_returns_401():
    """配置 key 后请求无 key 返回 401"""
    # Mock settings
    from unittest.mock import patch
    from src.utils.settings import Settings

    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)

    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        client = TestClient(app)
        response = client.get("/v1/chat/completions")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "auth_failed"


def test_invalid_api_key_returns_401():
    """配置 key 后请求带错误 key 返回 401"""
    from unittest.mock import patch
    from src.utils.settings import Settings

    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)

    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        client = TestClient(app)
        response = client.get(
            "/v1/chat/completions",
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 401


def test_valid_api_key_passes_through():
    """配置 key 后请求带正确 key 通过"""
    from unittest.mock import patch
    from src.utils.settings import Settings

    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)

    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        client = TestClient(app)
        # 带正确 key，期望通过（具体响应取决于后端）
        response = client.get(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key-123"}
        )
        # 不应该是 401（可能 422 因为 body 不对，或实际调用）
        assert response.status_code != 401 or "auth" not in response.json().get("error", {}).get("code", "")


def test_metrics_endpoint_exempt():
    """/metrics 端点豁免鉴权"""
    from unittest.mock import patch
    from src.utils.settings import Settings

    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=True)

    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        client = TestClient(app)
        response = client.get("/metrics")
        # 应该不返回 401 鉴权错误（可能返回其他错误，但不包含 auth_failed）
        if response.status_code == 401:
            assert response.json()["error"]["code"] != "auth_failed"
```

**Step 2: 运行测试**

```bash
cd D:\Work\code\web2api && python -m pytest tests/test_api_key_auth.py -v
```

---

## Task 5: 提交代码

**Step 1: 提交所有变更**

```bash
git add src/ tests/ && git commit -m "$(cat <<'EOF'
feat: 添加 API Key 鉴权中间件

- 新增 ApiKeyAuthMiddleware 中间件
- 支持静态配置的 API Key 白名单
- 空列表时不启用鉴权（向后兼容）
- /metrics, /stats 等监控端点豁免

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```
