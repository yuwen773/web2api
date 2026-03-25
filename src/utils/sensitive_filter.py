"""敏感信息脱敏处理器"""

from __future__ import annotations

from typing import Any

from structlog.types import EventDict, Processor


def _hide_account(value: str) -> str:
    """隐藏邮箱/账号，保留前2个字符"""
    if not value or len(value) <= 3:
        return "***"
    if "@" in value:
        # 邮箱格式: user@domain -> us***@domain
        parts = value.split("@")
        if len(parts[0]) <= 2:
            return "***"
        return f"{parts[0][:2]}***@{parts[1]}"
    return f"{value[:2]}***"


def _hide_token(value: str) -> str:
    """隐藏 token，保留前8个字符"""
    if len(value) > 8:
        return f"{value[:8]}***"
    return "***"


def _hide_session_id(value: str) -> str:
    """隐藏 session_id，保留前6个字符"""
    if len(value) > 6:
        return f"{value[:6]}***"
    return "***"


class SensitiveFilter:
    """敏感信息脱敏处理器"""

    # 需要完全隐藏的字段
    HIDDEN_FIELDS = {"authorization", "password"}

    # 需要部分隐藏的字段及处理函数
    PARTIAL_HIDDEN_FIELDS = {
        "account": _hide_account,
        "token": _hide_token,
        "session_id": _hide_session_id,
    }

    def __init__(self, sensitive_fields: list[str] | None = None) -> None:
        """
        Args:
            sensitive_fields: 需要脱敏的字段列表
        """
        self.sensitive_fields = set(sensitive_fields or [])

    def __call__(
        self, logger: object, method_name: str, event_dict: EventDict
    ) -> EventDict:
        """过滤事件字典中的敏感信息"""
        return self._filter_dict(event_dict)

    def _filter_dict(self, data: dict) -> dict:
        """递归过滤字典中的敏感信息"""
        result = {}
        for key, value in data.items():
            # 检查是否是敏感字段（预定义的或用户指定的）
            is_sensitive = (
                key in self.HIDDEN_FIELDS
                or key in self.PARTIAL_HIDDEN_FIELDS
                or key in self.sensitive_fields
            )
            if is_sensitive:
                result[key] = self._hide_value(key, value)
            elif isinstance(value, dict):
                result[key] = self._filter_dict(value)
            else:
                result[key] = value
        return result

    def _hide_value(self, key: str, value: Any) -> str:
        """根据字段名隐藏值"""
        if key in self.HIDDEN_FIELDS:
            return "***"
        elif key in self.PARTIAL_HIDDEN_FIELDS:
            return self.PARTIAL_HIDDEN_FIELDS[key](value)
        else:
            return "***"


def make_sensitive_filter(settings: Any) -> Processor:
    """从配置创建敏感信息过滤器工厂函数"""
    sensitive_fields = getattr(settings, "sensitive_fields", [])

    def filter_processor(
        logger: object, method_name: str, event_dict: EventDict
    ) -> EventDict:
        filter_obj = SensitiveFilter(sensitive_fields)
        return filter_obj(logger, method_name, event_dict)

    return filter_processor
