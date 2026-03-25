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


def test_concurrent_requests():
    """测试并发场景下的并发请求计数"""
    import threading
    collector = MetricsCollector()

    def increment_decrement():
        for _ in range(100):
            collector.increment_in_flight()
            collector.decrement_in_flight()

    threads = [threading.Thread(target=increment_decrement) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert collector.get_metrics()["http_requests_in_flight"] == 0


def test_concurrent_http_requests():
    """测试并发记录 HTTP 请求"""
    import threading
    collector = MetricsCollector()

    def record_requests():
        for i in range(50):
            collector.record_http_request("GET", f"/test/{i}", 200, 100.0)

    threads = [threading.Thread(target=record_requests) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    metrics = collector.get_metrics()
    assert metrics["http_requests_total"] == 250  # 5 threads * 50 requests


def test_export_metrics():
    """测试导出 Prometheus 格式指标"""
    collector = MetricsCollector()
    collector.record_http_request("GET", "/test", 200, 100)

    metrics = collector.export_metrics()
    assert isinstance(metrics, bytes)
    assert b"http_requests_total" in metrics
    assert b"http_request_duration_seconds" in metrics
