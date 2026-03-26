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
