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


def test_none_values():
    """测试 None 值的处理"""
    filter_obj = SensitiveFilter(["token", "password"])
    event = {"token": None, "password": None}
    result = filter_obj(None, None, event)
    assert result["token"] == "***"
    assert result["password"] == "***"


def test_non_string_values():
    """测试非字符串值的处理"""
    filter_obj = SensitiveFilter(["token"])
    event = {"token": 12345, "active": True}
    result = filter_obj(None, None, event)
    assert result["token"] == "***"
    assert result["active"] is True


def test_empty_string():
    """测试空字符串的处理"""
    filter_obj = SensitiveFilter(["token"])
    event = {"token": ""}
    result = filter_obj(None, None, event)
    assert result["token"] == "***"
