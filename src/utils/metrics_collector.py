"""
指标收集器 - 收集和导出应用指标

使用 Prometheus 格式导出指标，支持：
- HTTP 请求指标（请求数、延迟、并发）
- 业务指标（token 使用、会话数）
- 线程安全
"""

import threading
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST


class MetricsCollector:
    """
    指标收集器

    收集应用的各种指标，并以 Prometheus 格式导出。
    所有操作都是线程安全的。
    """

    def __init__(self, registry: CollectorRegistry = None):
        """
        初始化指标收集器

        Args:
            registry: Prometheus CollectorRegistry，如果为 None 则创建新的
        """
        self._lock = threading.Lock()

        # 如果没有提供 registry，创建一个新的
        if registry is None:
            registry = CollectorRegistry()

        self._registry = registry

        # HTTP 请求指标
        self._http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=registry
        )

        self._http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency',
            ['method', 'endpoint'],
            registry=registry
        )

        self._http_requests_in_flight = Gauge(
            'http_requests_in_flight',
            'Current number of HTTP requests in flight',
            registry=registry
        )

        self._http_errors_total = Counter(
            'http_errors_total',
            'Total HTTP errors',
            ['error_type'],
            registry=registry
        )

        # 业务指标 - Token 使用
        self._taiji_tokens_total = Counter(
            'taiji_tokens_total',
            'Total Taiji AI tokens used',
            ['model'],
            registry=registry
        )

        self._taiji_prompt_tokens = Counter(
            'taiji_prompt_tokens',
            'Total Taiji AI prompt tokens used',
            ['model'],
            registry=registry
        )

        self._taiji_completion_tokens = Counter(
            'taiji_completion_tokens',
            'Total Taiji AI completion tokens used',
            ['model'],
            registry=registry
        )

        # 业务指标 - 会话
        self._taiji_session_active = Gauge(
            'taiji_session_active',
            'Current number of active Taiji AI sessions',
            registry=registry
        )

        self._taiji_session_total = Counter(
            'taiji_session_total',
            'Total Taiji AI sessions created',
            registry=registry
        )

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float
    ):
        """
        记录 HTTP 请求

        Args:
            method: HTTP 方法 (GET, POST, etc.)
            endpoint: 请求端点
            status_code: HTTP 状态码
            duration_ms: 请求耗时（毫秒）
        """
        with self._lock:
            self._http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()

            self._http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration_ms / 1000.0)

    def increment_in_flight(self):
        """增加并发请求计数"""
        with self._lock:
            self._http_requests_in_flight.inc()

    def decrement_in_flight(self):
        """减少并发请求计数"""
        with self._lock:
            self._http_requests_in_flight.dec()

    def record_token_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ):
        """
        记录 token 使用情况

        Args:
            model: 模型名称
            prompt_tokens: 提示词 token 数
            completion_tokens: 完成 token 数
        """
        with self._lock:
            total_tokens = prompt_tokens + completion_tokens
            self._taiji_tokens_total.labels(model=model).inc(total_tokens)
            self._taiji_prompt_tokens.labels(model=model).inc(prompt_tokens)
            self._taiji_completion_tokens.labels(model=model).inc(completion_tokens)

    def increment_session(self):
        """增加活跃会话计数"""
        with self._lock:
            self._taiji_session_active.inc()
            self._taiji_session_total.inc()

    def decrement_session(self):
        """减少活跃会话计数"""
        with self._lock:
            self._taiji_session_active.dec()

    def record_error(self, error_type: str, error_message: str):
        """
        记录错误

        Args:
            error_type: 错误类型
            error_message: 错误消息
        """
        with self._lock:
            self._http_errors_total.labels(error_type=error_type).inc()

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取当前指标快照（用于测试）

        Returns:
            包含当前指标值的字典
        """
        with self._lock:
            return {
                "http_requests_total": self._get_metric_value(self._http_requests_total),
                "http_requests_in_flight": self._get_metric_value(self._http_requests_in_flight),
                "http_errors_total": self._get_metric_value(self._http_errors_total),
                "taiji_tokens_total": self._get_metric_value(self._taiji_tokens_total),
                "taiji_session_active": self._get_metric_value(self._taiji_session_active),
            }

    def _get_metric_value(self, metric) -> Any:
        """
        获取 Prometheus metric 的值

        Args:
            metric: Prometheus metric 对象

        Returns:
            metric 的值
        """
        try:
            # 收集 metric 的所有 Metric 对象
            metrics = metric.collect()
            if not metrics:
                return 0

            # 获取第一个 Metric 对象的所有样本
            total = 0.0
            for metric_obj in metrics:
                for sample in metric_obj.samples:
                    # 只计算主指标，忽略 _created 等辅助指标
                    if not sample.name.endswith('_created'):
                        total += sample.value
            return int(total)
        except Exception:
            return 0

    def export_metrics(self) -> bytes:
        """
        导出 Prometheus 格式的指标

        Returns:
            Prometheus 文本格式的指标数据
        """
        return generate_latest(self._registry)

    def get_content_type(self) -> str:
        """
        获取指标导出的 Content-Type

        Returns:
            Prometheus 的 Content-Type
        """
        return CONTENT_TYPE_LATEST


# 全局单例
_collector: MetricsCollector = None
_collector_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    获取全局单例 MetricsCollector

    Returns:
        全局唯一的 MetricsCollector 实例
    """
    global _collector

    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = MetricsCollector()

    return _collector
