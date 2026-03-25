from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from src.utils.request_context import get_request_id
from src.utils.settings import get_settings


class RequestIdFilter(logging.Filter):
    """为日志记录添加 request_id 的过滤器"""

    def filter(self, record: logging.LogRecord) -> bool:
        request_id = get_request_id()
        record.request_id = request_id if request_id else "-"
        return True


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

    # 控制台处理器 - 文本格式
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(RequestIdFilter())
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] [request_id=%(request_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 标记已配置
    setattr(root_logger, "_web2api_structlog_configured", True)


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

    # 配置文件处理器（JSON 格式）
    log_dir = Path(settings.log_directory)

    # 主日志文件（所有级别）
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=settings.log_max_size_mb * 1024 * 1024,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    # 使用 structlog 的 ProcessorFormatter 来处理 JSON 格式
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    )
    file_handler.setFormatter(file_formatter)

    # 错误日志文件（仅 ERROR 及以上）
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app-error.log",
        maxBytes=settings.log_max_size_mb * 1024 * 1024,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer()
    )
    error_handler.setFormatter(error_formatter)

    # 添加文件处理器到根 logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # 配置 structlog
    structlog.configure(
        processors=shared_processors
        + [
            # 将日志消息传递给标准 logging
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取 structlog logger"""
    return structlog.get_logger(name)


# 向后兼容：保留旧的 API
def configure_logging(level: int = logging.INFO) -> None:
    """向后兼容的日志配置函数"""
    setup_logging()
