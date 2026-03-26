import pytest
import structlog
from structlog.types import EventDict

from src.utils.logging_config import setup_logging, get_logger
from src.utils.settings import Settings
from src.utils.sensitive_filter import SensitiveFilter


def test_sensitive_data_filter():
    """测试敏感信息过滤处理器"""
    # 创建过滤器，包含 password 和 token 字段
    filter_obj = SensitiveFilter(sensitive_fields=["password", "token"])

    # 测试数据
    event_dict: EventDict = {
        "password": "secret123",
        "token": "abc123def",
        "username": "test",
        "event": "user login"
    }

    # 应用过滤器
    result = filter_obj(None, "info", event_dict)

    # 验证敏感字段被过滤
    assert result["password"] == "***"
    assert "***" in result["token"]
    assert result["username"] == "test"
    assert result["event"] == "user login"


def test_request_id_in_logs():
    """测试 request_id 正确添加到日志"""
    setup_logging()
    logger = get_logger("test")

    # 使用 StringIO 来捕获输出
    import io
    import logging

    # 创建一个 StringIO 来捕获日志
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)

    # 获取根 logger 并添加我们的 handler
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    root_logger.addHandler(handler)

    try:
        # 记录日志
        logger.info("test message")

        # 获取日志输出
        log_output = log_stream.getvalue()

        # 验证 request_id 在日志中
        assert "request_id" in log_output
    finally:
        # 恢复原始 handlers
        root_logger.handlers.clear()
        root_logger.handlers.extend(original_handlers)
        handler.close()
