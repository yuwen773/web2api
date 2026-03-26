# 日志和监控体系实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 web2api 项目添加完整的日志和监控体系，支持本地文件持久化、日志轮转、结构化日志输出、业务指标收集和内置监控仪表盘。

**架构:** 使用 structlog 实现结构化日志，支持 JSON/文本双格式输出，通过 MetricsCollector 收集指标，暴露 /metrics 和 /stats 端点。

**技术栈:** structlog, prometheus-client, RotatingFileHandler, FastAPI

---

## 前置准备

### Task 0: 安装依赖

**Files:**
- Modify: `requirements.txt`

**Step 1: 添加新依赖到 requirements.txt**

在 requirements.txt 末尾添加：

```txt
structlog>=24.1.0
prometheus-client>=0.21.0
```

**Step 2: 安装依赖**

```bash
pip install structlog prometheus-client
```

**Step 3: 验证安装**

```bash
python -c "import structlog; import prometheus_client; print('OK')"
```

预期输出: `OK`

**Step 4: 提交**

```bash
git add requirements.txt
git commit -m "feat: add structlog and prometheus-client dependencies"
```

---

## 第一阶段：日志系统重构

### Task 1: 创建日志配置模块（使用 structlog）

**Files:**
- Create: `src/utils/logging_config.py`
- Modify: `src/utils/settings.py`

**Step 1: 更新 settings.py 添加日志配置**

在 `src/utils/settings.py` 的 `Settings` 类中添加日志配置：

```python
# 日志配置
log_level: str = Field(default="INFO", description="日志级别")
log_format: str = Field(default="both", description="日志格式: text/json/both")
log_directory: str = Field(default="./logs", description="日志目录")

# 日志轮转配置
log_max_size_mb: int = Field(default=100, description="单个日志文件最大大小(MB)")
log_backup_count: int = Field(default=30, description="保留的日志文件数量")
log_compress_days: int = Field(default=7, description="压缩天数")

# 敏感字段脱敏配置
sensitive_fields: list[str] = Field(
    default=["authorization", "password", "token", "session_id", "account"],
    description="需要脱敏的字段"
)

# 监控配置
monitoring_enabled: bool = Field(default=True, description="是否启用监控")
metrics_endpoint: str = Field(default="/metrics", description="metrics 端点路径")
stats_endpoint: str = Field(default="/stats", description="stats 端点路径")
stats_refresh_sec: int = Field(default=5, description="stats 页面刷新间隔(秒)")
```

**Step 2: 创建新的 logging_config.py（使用 structlog）**

完全重写 `src/utils/logging_config.py`：

```python
from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from src.utils.request_context import get_request_id
from src.utils.settings import get_settings


def setup_logging() -> None:
    """配置 structlog 和标准 logging"""
    settings = get_settings()

    # 确保日志目录存在
    log_dir = Path(settings.log_directory)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 配置标准 logging（用于文件和控制台）
    _setup_standard_logging(log_dir, settings)

    # 配置 structlog
    _setup_structlog(settings)


def _setup_standard_logging(log_dir: Path, settings: Any) -> None:
    """配置标准 logging 模块"""
    root_logger = logging.getLogger()

    # 避免重复配置
    if getattr(root_logger, "_web2api_structlog_configured", False):
        return

    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # 清除现有 handlers
    root_logger.handlers.clear()

    # 文件处理器 - JSON 格式（主日志）
    json_handler = _create_file_handler(
        log_dir / "app.log",
        settings,
    )
    root_logger.addHandler(json_handler)

    # 文件处理器 - 错误日志（仅 ERROR 及以上）
    error_handler = _create_file_handler(
        log_dir / "app-error.log",
        settings,
        level=logging.ERROR,
    )
    root_logger.addHandler(error_handler)

    # 控制台处理器 - 文本格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] [request_id=%(request_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 标记已配置
    setattr(root_logger, "_web2api_structlog_configured", True)


def _create_file_handler(
    log_path: Path,
    settings: Any,
    level: int = logging.DEBUG,
) -> logging.Handler:
    """创建文件处理器，支持轮转"""
    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=settings.log_max_size_mb * 1024 * 1024,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)

    # JSON 格式
    handler.setFormatter(
        logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"request_id": "%(request_id)s", "module": "%(name)s", '
            '"message": "%(message)s"}'
        )
    )

    return handler


def _setup_structlog(settings: Any) -> None:
    """配置 structlog"""

    def add_request_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        """添加 request_id 到日志上下文"""
        request_id = get_request_id()
        event_dict["request_id"] = request_id if request_id else "-"
        return event_dict

    # 共享的处理器列表
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_request_id,
        structlog.processors.format_exc_info,
    ]

    # 标准模式：用于文件
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 开发模式：用于控制台
    structlog.configure(
        processors=shared_processors
        + [
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取 structlog logger"""
    return structlog.get_logger(name)
```

**Step 3: 更新 request_context.py（如果需要）**

确保 `src/utils/request_context.py` 中的 `get_request_id()` 函数存在且工作正常。

**Step 4: 测试日志配置**

```bash
python -c "
from src.utils.logging_config import setup_logging, get_logger
setup_logging()
logger = get_logger('test')
logger.info('test message', extra_key='extra_value')
print('Logging test completed')
"
```

预期输出: 控制台显示日志信息，logs/app.log 文件被创建。

**Step 5: 提交**

```bash
git add src/utils/logging_config.py src/utils/settings.py
git commit -m "feat: implement structlog-based logging configuration"
```

---

### Task 2: 创建敏感信息脱敏处理器

**Files:**
- Create: `src/utils/sensitive_filter.py`
- Test: `tests/test_sensitive_filter.py`

**Step 1: 编写失败的测试**

创建 `tests/test_sensitive_filter.py`：

```python
import pytest

from src.utils.sensitive_filter import SensitiveFilter


def test_filter_authorization():
    """测试 authorization 字段完全隐藏"""
    filter_obj = SensitiveFilter(["authorization"])
    event = {"authorization": "Bearer secret-token"}
    result = filter_obj(None, None, event)
    assert result["authorization"] == "***"


def test_filter_password():
    """测试 password 字段完全隐藏"""
    filter_obj = SensitiveFilter(["password"])
    event = {"password": "my-secret-password"}
    result = filter_obj(None, None, event)
    assert result["password"] == "***"


def test_filter_account_partial():
    """测试 account 字段部分隐藏"""
    filter_obj = SensitiveFilter(["account"])
    event = {"account": "yuwen@example.com"}
    result = filter_obj(None, None, event)
    assert result["account"] == "yu***@example.com"


def test_filter_token_partial():
    """测试 token 字段保留前8位"""
    filter_obj = SensitiveFilter(["token"])
    event = {"token": "eyJhbGciOiJUzI1NiIsInR5cCI6IkpXVCJ9.secret"}
    result = filter_obj(None, None, event)
    assert result["token"].startswith("eyJhbGci")
    assert "***" in result["token"]


def test_filter_session_id_partial():
    """测试 session_id 保留前6位"""
    filter_obj = SensitiveFilter(["session_id"])
    event = {"session_id": "sess_abc123def456"}
    result = filter_obj(None, None, event)
    assert result["session_id"].startswith("sess_")
    assert "***" in result["session_id"]


def test_nested_dict_filtering():
    """测试嵌套字典中的敏感字段过滤"""
    filter_obj = SensitiveFilter(["password", "token"])
    event = {
        "user": {"name": "test", "password": "secret"},
        "headers": {"authorization": "Bearer token"}
    }
    result = filter_obj(None, None, event)
    assert result["user"]["password"] == "***"
    assert result["headers"]["authorization"] == "***"


def test_no_sensitive_data():
    """测试没有敏感数据时不修改"""
    filter_obj = SensitiveFilter(["password"])
    event = {"name": "test", "value": 123}
    result = filter_obj(None, None, event)
    assert result == event


def test_multiple_sensitive_fields():
    """测试多个敏感字段同时过滤"""
    filter_obj = SensitiveFilter(["password", "token", "account"])
    event = {
        "password": "pwd",
        "token": "tok",
        "account": "acc",
        "safe": "value"
    }
    result = filter_obj(None, None, event)
    assert result["password"] == "***"
    assert result["token"] == "***"
    assert result["account"] == "***"
    assert result["safe"] == "value"
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_sensitive_filter.py -v
```

预期: FAIL - `ModuleNotFoundError: No module named 'src.utils.sensitive_filter'`

**Step 3: 实现敏感信息过滤器**

创建 `src/utils/sensitive_filter.py`：

```python
"""敏感信息脱敏处理器"""

from __future__ import annotations

from structlog.types import EventDict, Processor


class SensitiveFilter:
    """敏感信息脱敏处理器"""

    # 需要完全隐藏的字段
    HIDDEN_FIELDS = {"authorization", "password"}

    # 需要部分隐藏的字段及处理函数
    PARTIAL_HIDDEN_FIELDS = {
        "account": _hide_account,
        "token": _hide_token,
        "session_id": _hide_session_id,
    }

    def __init__(self, sensitive_fields: list[str] | None = None) -> None:
        """
        Args:
            sensitive_fields: 需要脱敏的字段列表
        """
        self.sensitive_fields = set(sensitive_fields or [])

    def __call__(
        self, logger: object, method_name: str, event_dict: EventDict
    ) -> EventDict:
        """过滤事件字典中的敏感信息"""
        return self._filter_dict(event_dict)

    def _filter_dict(self, data: dict) -> dict:
        """递归过滤字典中的敏感信息"""
        result = {}
        for key, value in data.items():
            if key in self.sensitive_fields:
                result[key] = self._hide_value(key, value)
            elif isinstance(value, dict):
                result[key] = self._filter_dict(value)
            else:
                result[key] = value
        return result

    def _hide_value(self, key: str, value: Any) -> str:
        """根据字段名隐藏值"""
        if key in self.HIDDEN_FIELDS:
            return "***"
        elif key in self.PARTIAL_HIDDEN_FIELDS:
            return self.PARTIAL_HIDDEN_FIELDS[key](value)
        else:
            return "***"


def _hide_account(value: str) -> str:
    """隐藏邮箱/账号，保留前2个字符"""
    if "@" in value:
        # 邮箱格式: user@domain -> us***@domain
        parts = value.split("@")
        return f"{parts[0][:2]}***@{parts[1]}"
    return f"{value[:2]}***"


def _hide_token(value: str) -> str:
    """隐藏 token，保留前8个字符"""
    if len(value) > 8:
        return f"{value[:8]}***"
    return "***"


def _hide_session_id(value: str) -> str:
    """隐藏 session_id，保留前6个字符"""
    if len(value) > 6:
        return f"{value[:6]}***"
    return "***"


def make_sensitive_filter(settings: Any) -> Processor:
    """从配置创建敏感信息过滤器工厂函数"""
    sensitive_fields = getattr(settings, "sensitive_fields", [])

    def filter_processor(
        logger: object, method_name: str, event_dict: EventDict
    ) -> EventDict:
        filter_obj = SensitiveFilter(sensitive_fields)
        return filter_obj(logger, method_name, event_dict)

    return filter_processor
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_sensitive_filter.py -v
```

预期: PASS - 所有测试通过

**Step 5: 提交**

```bash
git add src/utils/sensitive_filter.py tests/test_sensitive_filter.py
git commit -m "feat: add sensitive data filter for logging"
```

---

### Task 3: 集成敏感信息过滤器到日志配置

**Files:**
- Modify: `src/utils/logging_config.py`
- Test: `tests/test_logging_integration.py`

**Step 1: 编写集成测试**

创建 `tests/test_logging_integration.py`：

```python
import pytest
from structlog.testing import capture_logs

from src.utils.logging_config import setup_logging, get_logger
from src.utils.settings import Settings


def test_sensitive_data_in_logs():
    """测试敏感信息在日志中被过滤"""
    settings = Settings(sensitive_fields=["password", "token"])
    setup_logging()

    logger = get_logger("test")

    with capture_logs() as logs:
        logger.info("user login", password="secret123", token="abc123def", username="test")

    assert len(logs) == 1
    assert logs[0]["password"] == "***"
    assert "***" in logs[0]["token"]
    assert logs[0]["username"] == "test"


def test_request_id_in_logs():
    """测试 request_id 正确添加到日志"""
    setup_logging()
    logger = get_logger("test")

    with capture_logs() as logs:
        logger.info("test message")

    assert len(logs) == 1
    assert "request_id" in logs[0]
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_logging_integration.py -v
```

预期: FAIL - 日志中没有敏感信息过滤

**Step 3: 修改 logging_config.py 集成过滤器**

在 `src/utils/logging_config.py` 中：

1. 添加导入：
```python
from src.utils.sensitive_filter import make_sensitive_filter
```

2. 修改 `_setup_structlog` 函数，在处理器列表中添加敏感信息过滤器：

```python
def _setup_structlog(settings: Any) -> None:
    """配置 structlog"""

    def add_request_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
        """添加 request_id 到日志上下文"""
        request_id = get_request_id()
        event_dict["request_id"] = request_id if request_id else "-"
        return event_dict

    # 创建敏感信息过滤器
    sensitive_filter = make_sensitive_filter(settings)

    # 共享的处理器列表
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_request_id,
        sensitive_filter,  # 添加敏感信息过滤器
        structlog.processors.format_exc_info,
    ]

    # ... 其余代码保持不变
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_logging_integration.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/utils/logging_config.py tests/test_logging_integration.py
git commit -m "feat: integrate sensitive data filter into logging"
```

---

### Task 4: 更新 main.py 使用新的日志配置

**Files:**
- Modify: `main.py`

**Step 1: 备份当前 main.py**

```bash
cp main.py main.py.bak
```

**Step 2: 修改 main.py 的日志配置导入和使用**

在 `main.py` 中：

1. 修改导入：
```python
from src.utils.logging_config import setup_logging, get_logger
```

2. 替换 `configure_logging()` 为 `setup_logging()`：
```python
@app.on_event("startup")
async def on_startup() -> None:
    """应用启动时的初始化"""
    logger.info("Starting up web2api...")

    # 配置日志
    setup_logging()
    logger.info("Logging configured")

    # 配置并发限制
    logger.info("Configured max_concurrent=%s", settings.max_concurrent)

    # 初始化 Taiji 客户端并登录
    taiji_client.login()
    logger.info("Taiji client logged in during startup.")
```

3. 修改 logger 初始化：
```python
# 在文件开头，setup_logging() 调用之前
logger = get_logger(__name__)
```

**Step 3: 测试启动服务**

```bash
python main.py
```

预期: 服务启动，日志正确输出，logs/ 目录下创建日志文件。

按 `Ctrl+C` 停止服务。

**Step 4: 提交**

```bash
git add main.py
git commit -m "refactor: use new structlog-based logging in main"
```

---

## 第二阶段：指标收集系统

### Task 5: 创建 MetricsCollector 指标收集器

**Files:**
- Create: `src/utils/metrics_collector.py`
- Test: `tests/test_metrics_collector.py`

**Step 1: 编写失败的测试**

创建 `tests/test_metrics_collector.py`：

```python
import pytest
import time

from src.utils.metrics_collector import MetricsCollector, get_metrics_collector


def test_record_http_request():
    """测试记录 HTTP 请求"""
    collector = MetricsCollector()
    collector.record_http_request("POST", "/v1/chat/completions", 200, 123.5)

    metrics = collector.get_metrics()
    assert metrics["http_requests_total"] == 1


def test_record_token_usage():
    """测试记录 token 使用"""
    collector = MetricsCollector()
    collector.record_token_usage("claude-opus-4-6", 100, 200)

    metrics = collector.get_metrics()
    assert metrics["taiji_tokens_total"] == 300


def test_record_error():
    """测试记录错误"""
    collector = MetricsCollector()
    collector.record_error("api_error", "Taiji API timeout")

    metrics = collector.get_metrics()
    assert metrics["http_errors_total"] == 1


def test_increment_in_flight():
    """测试增加/减少并发请求计数"""
    collector = MetricsCollector()

    collector.increment_in_flight()
    assert collector.get_metrics()["http_requests_in_flight"] == 1

    collector.decrement_in_flight()
    assert collector.get_metrics()["http_requests_in_flight"] == 0


def test_record_session():
    """测试记录会话"""
    collector = MetricsCollector()

    collector.increment_session()
    assert collector.get_metrics()["taiji_session_active"] == 1

    collector.decrement_session()
    assert collector.get_metrics()["taiji_session_active"] == 0


def test_singleton():
    """测试单例模式"""
    collector1 = get_metrics_collector()
    collector2 = get_metrics_collector()
    assert collector1 is collector2
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_metrics_collector.py -v
```

预期: FAIL - 模块不存在

**Step 3: 实现 MetricsCollector**

创建 `src/utils/metrics_collector.py`：

```python
"""指标收集器"""

from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock
from typing import Any

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


class MetricsCollector:
    """指标收集器"""

    def __init__(self) -> None:
        """初始化指标收集器"""
        self._lock = Lock()

        # Prometheus 指标
        self._registry = CollectorRegistry()

        # HTTP 请求指标
        self._http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "path", "status"],
            registry=self._registry,
        )
        self._http_request_duration_ms = Histogram(
            "http_request_duration_ms",
            "HTTP request duration in milliseconds",
            ["method", "path"],
            buckets=(10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, float("inf")),
            registry=self._registry,
        )
        self._http_requests_in_flight = Gauge(
            "http_requests_in_flight",
            "Number of HTTP requests in flight",
            registry=self._registry,
        )
        self._http_errors_total = Counter(
            "http_errors_total",
            "Total HTTP errors",
            ["error_type"],
            registry=self._registry,
        )

        # 业务指标
        self._taiji_tokens_total = Counter(
            "taiji_tokens_total",
            "Total tokens consumed",
            ["model"],
            registry=self._registry,
        )
        self._taiji_requests_total = Counter(
            "taiji_requests_total",
            "Total Taiji API requests",
            ["model"],
            registry=self._registry,
        )
        self._taiji_session_active = Gauge(
            "taiji_session_active",
            "Number of active Taiji sessions",
            registry=self._registry,
        )
        self._taiji_reauth_total = Counter(
            "taiji_reauth_total",
            "Total re-authentication attempts",
            registry=self._registry,
        )
        self._images_generated_total = Counter(
            "images_generated_total",
            "Total images generated",
            ["model"],
            registry=self._registry,
        )

        # 系统指标
        self._semaphore_available = Gauge(
            "semaphore_available",
            "Available semaphore slots",
            registry=self._registry,
        )

        # 内部统计（用于快速查询）
        self._stats: dict[str, Any] = {
            "start_time": time.time(),
            "http_requests_total": 0,
            "http_errors_total": 0,
            "taiji_tokens_total": 0,
            "taiji_requests_total": 0,
            "taiji_reauth_total": 0,
            "images_generated_total": 0,
        }

    def record_http_request(
        self, method: str, path: str, status_code: int, duration_ms: float
    ) -> None:
        """记录 HTTP 请求"""
        self._http_requests_total.labels(
            method=method, path=self._normalize_path(path), status=str(status_code)
        ).inc()
        self._http_request_duration_ms.labels(
            method=method, path=self._normalize_path(path)
        ).observe(duration_ms)
        with self._lock:
            self._stats["http_requests_total"] += 1

    def record_error(self, error_type: str, message: str | None = None) -> None:
        """记录错误"""
        self._http_errors_total.labels(error_type=error_type).inc()
        with self._lock:
            self._stats["http_errors_total"] += 1

    def record_token_usage(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        """记录 token 使用"""
        total = prompt_tokens + completion_tokens
        self._taiji_tokens_total.labels(model=model).inc(total)
        self._taiji_requests_total.labels(model=model).inc()
        with self._lock:
            self._stats["taiji_tokens_total"] += total
            self._stats["taiji_requests_total"] += 1

    def increment_in_flight(self) -> None:
        """增加并发请求计数"""
        self._http_requests_in_flight.inc()

    def decrement_in_flight(self) -> None:
        """减少并发请求计数"""
        self._http_requests_in_flight.dec()

    def increment_session(self) -> None:
        """增加活跃会话计数"""
        self._taiji_session_active.inc()

    def decrement_session(self) -> None:
        """减少活跃会话计数"""
        self._taiji_session_active.dec()

    def record_reauth(self) -> None:
        """记录重新认证"""
        self._taiji_reauth_total.inc()
        with self._lock:
            self._stats["taiji_reauth_total"] += 1

    def record_image_generated(self, model: str, count: int = 1) -> None:
        """记录图片生成"""
        self._images_generated_total.labels(model=model).inc(count)
        with self._lock:
            self._stats["images_generated_total"] += count

    def set_semaphore_available(self, count: int) -> None:
        """设置可用信号槽数"""
        self._semaphore_available.set(count)

    def get_metrics(self) -> dict[str, Any]:
        """获取当前指标快照"""
        return {
            "http_requests_total": self._stats["http_requests_total"],
            "http_errors_total": self._stats["http_errors_total"],
            "taiji_tokens_total": self._stats["taiji_tokens_total"],
            "taiji_requests_total": self._stats["taiji_requests_total"],
            "taiji_session_active": self._taiji_session_active._value._value,
            "taiji_reauth_total": self._stats["taiji_reauth_total"],
            "images_generated_total": self._stats["images_generated_total"],
            "http_requests_in_flight": self._http_requests_in_flight._value._value,
            "semaphore_available": self._semaphore_available._value._value,
            "uptime_seconds": time.time() - self._stats["start_time"],
        }

    def export_prometheus(self) -> bytes:
        """导出 Prometheus 格式的指标"""
        return generate_latest(self._registry)

    def get_content_type(self) -> str:
        """获取 Prometheus 内容类型"""
        return CONTENT_TYPE_LATEST

    @contextmanager
    def track_request(self, method: str, path: str):
        """上下文管理器：跟踪请求"""
        start_time = time.time()
        self.increment_in_flight()
        try:
            yield
            duration_ms = (time.time() - start_time) * 1000
            self.record_http_request(method, path, 200, duration_ms)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.record_error(type(e).__name__)
            raise
        finally:
            self.decrement_in_flight()

    def _normalize_path(self, path: str) -> str:
        """标准化路径，将动态部分替换为占位符"""
        # 简单的路径标准化
        if path.startswith("/v1/chat/"):
            return "/v1/chat/completions"
        if path.startswith("/v1/images/"):
            return "/v1/images/*"
        return path


# 全局单例
_collector: MetricsCollector | None = None
_collector_lock = Lock()


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器单例"""
    global _collector
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = MetricsCollector()
    return _collector
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_metrics_collector.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/utils/metrics_collector.py tests/test_metrics_collector.py
git commit -m "feat: add MetricsCollector for collecting metrics"
```

---

### Task 6: 创建指标中间件

**Files:**
- Create: `src/middleware/metrics_middleware.py`
- Test: `tests/test_metrics_middleware.py`

**Step 1: 编写失败的测试**

创建 `tests/test_metrics_middleware.py`：

```python
import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from src.middleware.metrics_middleware import MetricsMiddleware
from src.utils.metrics_collector import MetricsCollector


def test_metrics_middleware_records_request():
    """测试中间件记录请求"""
    app = FastAPI()
    collector = MetricsCollector()

    app.add_middleware(MetricsMiddleware, collector=collector)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200

    metrics = collector.get_metrics()
    assert metrics["http_requests_total"] == 1


def test_metrics_middleware_records_error():
    """测试中间件记录错误"""
    app = FastAPI()
    collector = MetricsCollector()

    app.add_middleware(MetricsMiddleware, collector=collector)

    @app.get("/error")
    def error_endpoint():
        raise ValueError("Test error")

    client = TestClient(app)
    with pytest.raises(ValueError):
        client.get("/error")

    metrics = collector.get_metrics()
    assert metrics["http_errors_total"] == 1
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_metrics_middleware.py -v
```

预期: FAIL - 模块不存在

**Step 3: 实现指标中间件**

创建 `src/middleware/metrics_middleware.py`：

```python
"""指标收集中间件"""

from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.metrics_collector import MetricsCollector


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""

    def __init__(self, app: ASGIApp, collector: MetricsCollector) -> None:
        """
        Args:
            app: ASGI 应用
            collector: 指标收集器
        """
        super().__init__(app)
        self.collector = collector

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求，收集指标"""
        start_time = time.time()
        method = request.method
        path = request.url.path

        self.collector.increment_in_flight()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            self.collector.record_http_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.collector.record_error(type(e).__name__)
            raise

        finally:
            self.collector.decrement_in_flight()
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_metrics_middleware.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/middleware/metrics_middleware.py tests/test_metrics_middleware.py
git commit -m "feat: add MetricsMiddleware for automatic metrics collection"
```

---

### Task 7: 在业务代码中集成指标收集

**Files:**
- Modify: `src/client/taiji_client.py`
- Modify: `src/api/openai.py`
- Modify: `src/api/anthropic.py`
- Modify: `src/api/images.py`

**Step 1: 修改 taiji_client.py 集成指标收集**

在 `src/client/taiji_client.py` 中：

1. 添加导入：
```python
from src.utils.metrics_collector import get_metrics_collector
```

2. 在 `login()` 方法中记录重新认证：
```python
async def _do_login_with_retry(self) -> None:
    """执行登录并重试一次"""
    # ... 现有代码 ...
    if response.status_code == 401:
        logger.warning("Taiji token expired (HTTP 401), re-authenticating and retrying once.")
        get_metrics_collector().record_reauth()  # 添加这行
        # ... 其余代码 ...
```

3. 在 `create_session()` 中记录会话创建：
```python
async def create_session(self, model: str) -> str:
    """创建聊天会话"""
    # ... 创建会话代码 ...
    get_metrics_collector().increment_session()  # 添加这行
    return session_id
```

4. 在 `delete_session()` 中记录会话删除：
```python
async def delete_session(self, session_id: str) -> bool:
    """删除聊天会话"""
    # ... 删除代码 ...
    if response.status_code == 204:
        get_metrics_collector().decrement_session()  # 添加这行
    # ... 其余代码 ...
```

**Step 2: 修改 openai.py 集成指标收集**

在 `src/api/openai.py` 中：

1. 添加导入：
```python
from src.utils.metrics_collector import get_metrics_collector
```

2. 在 `chat_completions()` 中记录 token 使用：
```python
async def chat_completions(request: ChatCompletionRequest) -> Response:
    """OpenAI Chat Completions API"""

    # ... 现有代码 ...

    try:
        # 获取响应
        response = await _process_chat_completion(request)

        # 记录 token 使用
        if hasattr(response, "usage") and response.usage:
            get_metrics_collector().record_token_usage(
                model=request.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )

        return response

    except Exception as e:
        # ... 错误处理 ...
```

**Step 3: 修改 images.py 集成指标收集**

在 `src/api/images.py` 中：

1. 添加导入：
```python
from src.utils.metrics_collector import get_metrics_collector
```

2. 在图片生成成功后记录：
```python
# 在成功提取图片后
get_metrics_collector().record_image_generated(
    model=request.model,
    count=len(image_urls),
)
```

**Step 4: 测试集成效果**

```bash
python main.py
# 在另一个终端发送测试请求
curl http://localhost:8000/v1/models
# 检查日志中是否有指标相关信息
```

**Step 5: 提交**

```bash
git add src/client/taiji_client.py src/api/openai.py src/api/images.py
git commit -m "feat: integrate metrics collection into business logic"
```

---

## 第三阶段：监控端点

### Task 8: 创建监控 API 端点

**Files:**
- Create: `src/api/monitoring.py`
- Test: `tests/test_monitoring_api.py`

**Step 1: 编写失败的测试**

创建 `tests/test_monitoring_api.py`：

```python
import pytest
from fastapi.testclient import TestClient

from main import app


def test_metrics_endpoint():
    """测试 /metrics 端点"""
    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert b"http_requests_total" in response.content


def test_stats_json_endpoint():
    """测试 /stats/json 端点"""
    client = TestClient(app)
    response = client.get("/stats/json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "http_requests_total" in data
    assert "uptime_seconds" in data


def test_stats_html_endpoint():
    """测试 /stats 端点"""
    client = TestClient(app)
    response = client.get("/stats")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_monitoring_api.py -v
```

预期: FAIL - 端点不存在

**Step 3: 实现监控端点**

创建 `src/api/monitoring.py`：

```python
"""监控 API 端点"""

from __future__ import annotations

from fastapi import APIResponse, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from src.utils.metrics_collector import get_metrics_collector
from src.utils.settings import get_settings


async def metrics() -> PlainTextResponse:
    """Prometheus 格式的指标端点"""
    collector = get_metrics_collector()
    metrics_data = collector.export_prometheus()

    return PlainTextResponse(
        content=metrics_data.decode("utf-8"),
        media_type=collector.get_content_type(),
    )


async def stats_json() -> JSONResponse:
    """JSON 格式的统计端点"""
    collector = get_metrics_collector()
    return JSONResponse(content=collector.get_metrics())


async def_stats(request: Request) -> HTMLResponse:
    """HTML 统计仪表盘"""
    collector = get_metrics_collector()
    settings = get_settings()
    metrics = collector.get_metrics()
    refresh_sec = settings.stats_refresh_sec

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>web2api 监控仪表盘</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="{refresh_sec}">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            .update-time {{ color: #666; font-size: 14px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 6px; }}
            .section h2 {{ color: #007bff; margin-top: 0; }}
            .stat-row {{ display: flex; justify-content: space-between; margin: 10px 0; }}
            .stat-label {{ font-weight: bold; color: #555; }}
            .stat-value {{ color: #333; }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .error {{ color: #dc3545; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #007bff; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>web2api 监控仪表盘 <span class="update-time">最后更新: 实时</span></h1>

            <div class="section">
                <h2>服务状态</h2>
                <div class="stat-row">
                    <span class="stat-label">运行时间:</span>
                    <span class="stat-value">{_format_uptime(metrics['uptime_seconds'])}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">当前请求数:</span>
                    <span class="stat-value">{metrics['http_requests_in_flight']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">并发槽位:</span>
                    <span class="stat-value">{metrics['semaphore_available']} 可用</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">活跃会话:</span>
                    <span class="stat-value">{metrics['taiji_session_active']}</span>
                </div>
            </div>

            <div class="section">
                <h2>请求统计</h2>
                <div class="stat-row">
                    <span class="stat-label">总请求数:</span>
                    <span class="stat-value">{metrics['http_requests_total']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">错误数:</span>
                    <span class="stat-value {'error' if metrics['http_errors_total'] > 0 else 'success'}">{metrics['http_errors_total']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">成功率:</span>
                    <span class="stat-value">{_calculate_success_rate(metrics)}</span>
                </div>
            </div>

            <div class="section">
                <h2>业务指标</h2>
                <div class="stat-row">
                    <span class="stat-label">太极 API 调用:</span>
                    <span class="stat-value">{metrics['taiji_requests_total']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Token 消耗:</span>
                    <span class="stat-value">{metrics['taiji_tokens_total']:,}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">图片生成:</span>
                    <span class="stat-value">{metrics['images_generated_total']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">重新认证:</span>
                    <span class="stat-value {'warning' if metrics['taiji_reauth_total'] > 0 else ''}">{metrics['taiji_reauth_total']}</span>
                </div>
            </div>

            <div class="section">
                <h2>快捷操作</h2>
                <p>
                    <a href="/metrics" target="_blank">查看 Prometheus 指标</a> |
                    <a href="/stats/json" target="_blank">获取 JSON 数据</a> |
                    <a href="javascript:location.reload()">刷新页面</a>
                </p>
            </div>
        </div>

        <script>
            // 简单的自动刷新时间更新
            document.addEventListener('DOMContentLoaded', function() {{
                const updateTime = document.querySelector('.update-time');
                setInterval(function() {{
                    updateTime.textContent = '最后更新: ' + new Date().toLocaleTimeString();
                }}, 1000);
            }});
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


def _format_uptime(seconds: float) -> str:
    """格式化运行时间"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{days}天 {hours}小时 {minutes}分钟"


def _calculate_success_rate(metrics: dict) -> str:
    """计算成功率"""
    total = metrics['http_requests_total']
    errors = metrics['http_errors_total']
    if total == 0:
        return "100%"
    rate = ((total - errors) / total) * 100
    return f"{rate:.1f}%"
```

**Step 4: 在 main.py 中注册监控路由**

修改 `main.py`：

```python
from src.api.monitoring import metrics, stats_json, stats

# ... 在路由注册部分添加 ...

# 监控端点
app.add_route(get_settings().metrics_endpoint, metrics, methods=["GET"])
app.add_route(get_settings().stats_endpoint + "/json", stats_json, methods=["GET"])
app.add_route(get_settings().stats_endpoint, stats, methods=["GET"])
```

**Step 5: 运行测试确认通过**

```bash
pytest tests/test_monitoring_api.py -v
```

预期: PASS

**Step 6: 提交**

```bash
git add src/api/monitoring.py tests/test_monitoring_api.py main.py
git commit -m "feat: add monitoring endpoints (/metrics, /stats)"
```

---

### Task 9: 在 main.py 中集成指标中间件

**Files:**
- Modify: `main.py`

**Step 1: 添加指标中间件**

在 `main.py` 的 `on_startup()` 函数中初始化指标收集器，并添加中间件：

```python
from src.middleware.metrics_middleware import MetricsMiddleware
from src.utils.metrics_collector import get_metrics_collector

# ... 在 on_startup 中 ...

# 初始化指标收集器
collector = get_metrics_collector()
logger.info("Metrics collector initialized")

# ... 在 create_app 后添加中间件 ...

app.add_middleware(MetricsMiddleware, collector=collector)
logger.info("Metrics middleware added")
```

**Step 2: 测试完整流程**

```bash
python main.py
# 访问 http://localhost:8000/stats 查看仪表盘
# 访问 http://localhost:8000/metrics 查看 Prometheus 指标
```

**Step 3: 提交**

```bash
git add main.py
git commit -m "feat: integrate metrics middleware in main"
```

---

## 第四阶段：完善和测试

### Task 10: 更新现有中间件集成日志和指标

**Files:**
- Modify: `src/middleware/request_middleware.py`

**Step 1: 修改 request_middleware.py 使用新的日志系统**

在 `src/middleware/request_middleware.py` 中：

1. 修改导入：
```python
from src.utils.logging_config import get_logger
```

2. 替换 logger 初始化：
```python
logger = get_logger(__name__)
```

3. 确保日志使用 structlog 格式：
```python
logger.info(
    "API request started",
    method=request.method,
    path=request.url.path,
    request_id=request_id,
)
```

**Step 2: 测试日志输出**

```bash
python main.py
# 发送请求，检查日志格式是否正确
curl http://localhost:8000/v1/models
```

**Step 3: 提交**

```bash
git add src/middleware/request_middleware.py
git commit -m "refactor: update request_middleware to use structlog"
```

---

### Task 11: 更新所有 API 文件使用新的日志系统

**Files:**
- Modify: `src/api/openai.py`
- Modify: `src/api/anthropic.py`
- Modify: `src/api/images.py`
- Modify: `src/client/taiji_client.py`

**Step 1: 批量替换 logger 导入和使用**

在每个文件中：

1. 替换导入：
```python
# 从
import logging
logger = logging.getLogger(__name__)

# 改为
from src.utils.logging_config import get_logger
logger = get_logger(__name__)
```

2. 更新日志调用为 structlog 格式（使用关键字参数）：
```python
# 从
logger.info("Client disconnected during streaming")

# 改为
logger.info("Client disconnected during streaming", endpoint="chat_completions")
```

**Step 2: 测试所有 API**

```bash
# 测试 OpenAI API
curl -X POST http://localhost:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"claude-opus-4-6","messages":[{"role":"user","content":"hello"}]}'

# 测试 Anthropic API
curl -X POST http://localhost:8000/v1/messages -H "Content-Type: application/json" -d '{"model":"claude-opus-4-6","max_tokens":100,"messages":[{"role":"user","content":"hello"}]}'

# 测试图片 API
curl -X POST http://localhost:8000/v1/images/generations -H "Content-Type: application/json" -d '{"model":"Nano-banana绘图模型","prompt":"a cat","n":1}'
```

**Step 3: 提交**

```bash
git add src/api/openai.py src/api/anthropic.py src/api/images.py src/client/taiji_client.py
git commit -m "refactor: update all modules to use structlog"
```

---

### Task 12: 创建 logs 目录和文档

**Files:**
- Create: `logs/.gitkeep`
- Create: `logs/README.md`

**Step 1: 创建日志目录结构**

```bash
mkdir -p logs
touch logs/.gitkeep
```

**Step 2: 创建日志说明文档**

创建 `logs/README.md`：

```markdown
# 日志目录

此目录用于存储 web2api 服务的日志文件。

## 日志文件

| 文件 | 说明 |
|------|------|
| `app.log` | 主日志文件，包含所有级别的日志（JSON 格式） |
| `app-error.log` | 错误日志，仅包含 ERROR 及以上级别的日志 |
| `app.log.*` | 轮转后的历史日志文件（自动压缩） |

## 日志轮转

- 单个日志文件最大 100MB
- 最多保留 30 个历史文件
- 超过 7 天的旧日志自动压缩为 .gz

## 查看 JSON 日志

使用 `jq` 工具可以方便地查看 JSON 格式的日志：

```bash
# 查看最近的日志
tail -f logs/app.log | jq

# 过滤特定级别的日志
cat logs/app.log | jq 'select(.level == "ERROR")'

# 查看特定请求的所有日志
grep "request-abc123" logs/app.log | jq
```

## 配置

日志配置在 `config/config.yaml` 中：

```yaml
logging:
  level: INFO
  format: both
  directory: ./logs
  rotation:
    max_size_mb: 100
    backup_count: 30
    compress_days: 7
```
```

**Step 3: 更新 .gitignore**

在 `.gitignore` 中添加：

```
# 日志文件
logs/*.log
logs/*.log.*
logs/*.gz
```

**Step 4: 提交**

```bash
git add logs/.gitkeep logs/README.md .gitignore
git commit -m "docs: add logging directory and documentation"
```

---

### Task 13: 更新配置文件

**Files:**
- Modify: `config/config.yaml`
- Modify: `.env.example`

**Step 1: 更新配置文件模板**

在 `config/config.yaml` 中添加日志和监控配置：

```yaml
# ... 现有配置 ...

# 日志配置
logging:
  level: INFO
  format: both  # text/json/both
  directory: ./logs
  rotation:
    max_size_mb: 100
    backup_count: 30
    compress_days: 7
  sensitive_fields:
    - authorization
    - password
    - token
    - session_id
    - account

# 监控配置
monitoring:
  enabled: true
  metrics_endpoint: /metrics
  stats_endpoint: /stats
  stats_refresh_sec: 5
```

**Step 2: 更新环境变量模板**

在 `.env.example` 中添加：

```bash
# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=both
LOG_DIRECTORY=./logs
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=30
LOG_COMPRESS_DAYS=7

# 监控配置
MONITORING_ENABLED=true
METRICS_ENDPOINT=/metrics
STATS_ENDPOINT=/stats
STATS_REFRESH_SEC=5
```

**Step 3: 提交**

```bash
git add config/config.yaml .env.example
git commit -m "config: add logging and monitoring configuration"
```

---

### Task 14: 运行完整测试套件

**Step 1: 运行所有测试**

```bash
pytest tests/ -v --tb=short
```

**Step 2: 修复任何失败的测试**

如果测试失败，逐个修复并提交。

**Step 3: 提交**

```bash
git commit -m "test: ensure all tests pass with new logging system"
```

---

### Task 15: 更新主 README 文档

**Files:**
- Modify: `README.md`

**Step 1: 在 README 中添加日志和监控章节**

在 `README.md` 中添加：

```markdown
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
```
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "docs: update README with logging and monitoring info"
```

---

## 验收检查清单

在认为完成之前，请验证：

- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 服务正常启动 (`python main.py`)
- [ ] 日志文件在 `logs/` 目录创建
- [ ] 访问 `/metrics` 返回 Prometheus 格式数据
- [ ] 访问 `/stats` 显示可视化仪表盘
- [ ] 敏感信息在日志中被正确脱敏
- [ ] JSON 日志格式正确
- [ ] 控制台日志格式正确
- [ ] 日志轮转正常工作
- [ ] 所有配置项在 `config/config.yaml` 中可用

---

## 完成

实施完成后，项目将具备：

1. **完整的日志系统**
   - 结构化日志（JSON + 文本）
   - 日志轮转和压缩
   - 敏感信息自动脱敏
   - 请求上下文追踪

2. **全面的监控指标**
   - HTTP 请求统计
   - 业务指标（tokens、调用量）
   - 错误追踪
   - 系统状态

3. **可视化仪表盘**
   - 实时监控面板
   - Prometheus 兼容接口
   - JSON 数据导出
