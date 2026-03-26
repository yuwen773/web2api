import pytest
from fastapi import FastAPI
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
