from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.utils.settings import Settings


def test_no_auth_when_keys_empty():
    """无 key 配置时请求正常通过"""
    mock_settings = Settings(api_keys=[], monitoring_enabled=False)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        # Import here to avoid lifespan issues with other tests
        from main import app
        client = TestClient(app)
        response = client.get("/v1/chat/completions")
        # 不应该是 401 auth 错误
        if response.status_code == 401:
            assert response.json()["error"]["code"] != "auth_failed"


def test_missing_api_key_returns_401():
    """配置 key 后请求无 key 返回 401"""
    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        from main import app
        client = TestClient(app)
        response = client.get("/v1/chat/completions")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "auth_failed"


def test_invalid_api_key_returns_401():
    """配置 key 后请求带错误 key 返回 401"""
    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        from main import app
        client = TestClient(app)
        response = client.get(
            "/v1/chat/completions",
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 401


def test_valid_api_key_passes_through():
    """配置 key 后请求带正确 key 通过"""
    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=False)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        from main import app
        client = TestClient(app)
        response = client.get(
            "/v1/chat/completions",
            headers={"X-API-Key": "test-key-123"}
        )
        # 不应该是 401 auth 错误（可能 422 因为缺少 body，或实际调用后端）
        if response.status_code == 401:
            assert response.json()["error"]["code"] != "auth_failed"


def test_metrics_endpoint_exempt():
    """/metrics 端点豁免鉴权"""
    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=True)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        from main import app
        client = TestClient(app)
        response = client.get("/metrics")
        # 应该不返回 401 鉴权错误
        if response.status_code == 401:
            assert response.json()["error"]["code"] != "auth_failed"


def test_stats_endpoint_exempt():
    """/stats 端点豁免鉴权"""
    mock_settings = Settings(api_keys=["test-key-123"], monitoring_enabled=True)
    with patch("src.middleware.api_key.get_settings", return_value=mock_settings):
        from main import app
        client = TestClient(app)
        response = client.get("/stats")
        if response.status_code == 401:
            assert response.json()["error"]["code"] != "auth_failed"
