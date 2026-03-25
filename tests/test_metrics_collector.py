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
