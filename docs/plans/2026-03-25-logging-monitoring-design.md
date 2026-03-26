# 日志和监控体系设计文档

**日期**: 2026-03-25
**状态**: 已批准
**方案**: 方案 A - 轻量级自建

---

## 1. 概述

为 web2api 项目设计一套完整的日志和监控体系，支持本地文件持久化、日志轮转、结构化日志输出、业务指标收集和内置监控仪表盘。

**适用场景**: 单机小规模部署（QPS < 10）

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI 应用                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐  │
│  │  API 路由层    │  │  中间件           │  │  业务逻辑层      │  │
│  │  (openai.py)  │  │  (request_       │  │  (taiji_client) │  │
│  │               │  │   middleware.py) │  │                 │  │
│  └───────┬───────┘  └────────┬─────────┘  └────────┬────────┘  │
│          │                    │                      │            │
│          ▼                    ▼                      ▼            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    统一日志接口 (structlog)                   │ │
│  │                   + 日志过滤 (敏感信息脱敏)                    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│          │                                                    │ │
│          ▼                                                    ▼ │
│  ┌─────────────────────┐                          ┌──────────────┐
│  │   文件日志处理器      │                          │ 控制台处理器  │
│  │  - app.log (JSON)    │                          │ (文本格式)    │
│  │  - app.log (TEXT)    │                          │              │
│  │  - error.log         │                          │              │
│  └─────────────────────┘                          └──────────────┘
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   MetricsCollector                          │ │
│  │  - 请求计数 (QPS)                                            │ │
│  │  - 响应时间 (P50/P95/P99)                                    │ │
│  │  - 错误率                                                     │ │
│  │  - Token 消耗                                                 │ │
│  │  - 模型调用分布                                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│          │                                                    │ │
│          ▼                                                    ▼ │
│  ┌─────────────────────┐                          ┌──────────────┐
│  │   GET /metrics      │                          │ GET /stats   │
│  │  (Prometheus 格式)   │                          │  (HTML 页面)  │
│  └─────────────────────┘                          └──────────────┘
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 日志系统

### 3.1 日志文件结构

```
logs/
├── app.log              # 主日志 (JSON 格式，轮转)
├── app-error.log        # 错误日志 (ERROR 及以上，独立文件)
├── access.log           # 访问日志 (API 调用记录)
└── metrics.log          # 指标日志 (可选，定期汇总)
```

### 3.2 日志轮转策略

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| max_size_mb | 100 | 单个文件最大 100MB |
| backup_count | 30 | 保留 30 个历史文件 |
| compress_days | 7 | 超过 7 天的旧日志压缩为 .gz |

### 3.3 日志格式

**JSON 格式：**
```json
{
  "timestamp": "2026-03-25T10:30:15.123Z",
  "level": "info",
  "request_id": "abc123",
  "module": "src.api.openai",
  "message": "Chat completion request completed",
  "context": {
    "method": "POST",
    "path": "/v1/chat/completions",
    "model": "claude-opus-4-6",
    "status_code": 200,
    "duration_ms": 1234,
    "prompt_tokens": 100,
    "completion_tokens": 200
  }
}
```

**文本格式：**
```
2026-03-25 10:30:15 [INFO] [request_id=abc123] src.api.openai: Chat completion request completed
```

### 3.4 敏感信息脱敏

| 字段 | 脱敏方式 | 示例 |
|------|----------|------|
| authorization | 完全隐藏 | `***` |
| password | 完全隐藏 | `***` |
| account | 部分隐藏 | `yu***@example.com` |
| token | 保留前8位 | `eyJhbGc***` |
| session_id | 保留前6位 | `sess_***` |

### 3.5 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | SSE 流式数据细节（仅在开发环境） |
| INFO | 请求开始/结束、认证、会话管理 |
| WARNING | 重试、会话删除失败 |
| ERROR | API 错误、上游错误 |
| CRITICAL | 服务无法启动、认证彻底失败 |

---

## 4. 监控指标

### 4.1 基础性能指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| http_requests_total | Counter | HTTP 请求总数（按状态码、路径分组） |
| http_request_duration_ms | Histogram | 请求耗时（P50/P95/P99） |
| http_requests_in_flight | Gauge | 当前正在处理的请求数 |
| http_errors_total | Counter | 错误总数（按错误类型分组） |

### 4.2 业务指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| taiji_tokens_total | Counter | Token 消耗总数（按模型分组） |
| taiji_requests_total | Counter | 太极 API 调用总数（按模型分组） |
| taiji_session_active | Gauge | 当前活跃会话数 |
| taiji_reauth_total | Counter | 重新认证次数 |
| images_generated_total | Counter | 图片生成总数（按模型分组） |

### 4.3 系统指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| semaphore_available | Gauge | 可用并发槽位数 |
| semaphore_wait_duration_ms | Histogram | 获取信号量等待时长 |

---

## 5. 监控仪表盘

### 5.1 新增端点

| 端点 | 格式 | 说明 |
|------|------|------|
| GET /metrics | Prometheus 文本格式 | 对接监控系统 |
| GET /stats | HTML 页面 | 可视化仪表盘 |
| GET /stats/json | JSON | API 方式获取统计 |

### 5.2 仪表盘内容

- 服务状态（运行时间、当前请求数、并发槽位、活跃会话）
- 请求统计（总数、成功率、平均响应时间、P95/P99）
- 状态码分布
- 模型使用统计（调用次数、Token 消耗）
- 最近错误列表

---

## 6. 技术实现

### 6.1 新增文件

```
src/
├── utils/
│   ├── logging_config.py       # 重构：使用 structlog
│   ├── metrics_collector.py    # 新增：指标收集器
│   └── sensitive_filter.py     # 新增：敏感信息脱敏
│
├── api/
│   └── monitoring.py           # 新增：/metrics 和 /stats 端点
│
├── middleware/
│   ├── request_middleware.py   # 修改：集成 metrics 收集
│   └── metrics_middleware.py   # 新增：自动记录 HTTP 指标

logs/                            # 新增：日志目录
└── .gitkeep
```

### 6.2 新增依赖

```txt
structlog>=24.1.0          # 结构化日志
prometheus-client>=0.21.0  # Prometheus 指标格式
```

### 6.3 配置项

```yaml
logging:
  level: INFO               # DEBUG/INFO/WARNING/ERROR
  format: both              # text/json/both
  directory: ./logs
  rotation:
    max_size_mb: 100
    backup_count: 30
    compress_days: 7
  sensitive_fields:         # 需脱敏的字段
    - authorization
    - password
    - token
    - session_id
    - account

monitoring:
  enabled: true
  metrics_endpoint: /metrics
  stats_endpoint: /stats
  stats_refresh_sec: 5
```

### 6.4 实现关键点

1. 使用 `structlog` 配置双处理器（文件 JSON + 控制台文本）
2. 使用 `contextvars` 传递请求上下文到日志
3. `MetricsCollector` 使用线程安全的数据结构
4. 中间件自动记录 HTTP 请求指标
5. 业务逻辑层调用 `record_token_usage()` 等

---

## 7. 后续扩展

如需扩展到大规模部署，可以考虑：

1. 对接 ELK/Loki 进行日志收集
2. 使用 Prometheus + Grafana 进行监控
3. 添加分布式追踪（如 OpenTelemetry）
4. 添加告警机制

---

## 附录：Prometheus 格式示例

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",path="/v1/chat/completions",status="200"} 1234
http_requests_total{method="POST",path="/v1/chat/completions",status="500"} 5

# HELP http_request_duration_ms HTTP request duration in milliseconds
# TYPE http_request_duration_ms histogram
http_request_duration_ms_bucket{le="10"} 100
http_request_duration_ms_bucket{le="50"} 500
http_request_duration_ms_bucket{le="100"} 800
http_request_duration_ms_bucket{le="+Inf"} 1000
http_request_duration_ms_sum 45678
http_request_duration_ms_count 1000
```
