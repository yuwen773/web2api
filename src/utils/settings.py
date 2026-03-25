from __future__ import annotations

import os
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"
DEFAULT_TAIJI_API_BASE = "https://ai.aurod.cn"
DEFAULT_TAIJI_APP_VERSION = "2.14.0"
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 8000
DEFAULT_MAX_CONCURRENT = 5


class Settings(BaseSettings):
    """应用配置，支持环境变量和配置文件"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
    )

    # Taiji API 配置
    taiji_api_base: str = Field(default=DEFAULT_TAIJI_API_BASE, description="Taiji API 基础 URL")
    taiji_account: str | None = Field(default=None, description="Taiji 账号")
    taiji_password: str | None = Field(default=None, description="Taiji 密码")
    taiji_app_version: str = Field(default=DEFAULT_TAIJI_APP_VERSION, description="Taiji App 版本")

    # 服务器配置
    server_host: str = Field(default=DEFAULT_SERVER_HOST, description="服务器监听地址")
    server_port: int = Field(default=DEFAULT_SERVER_PORT, description="服务器端口")
    max_concurrent: int = Field(default=DEFAULT_MAX_CONCURRENT, description="最大并发数")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="both", description="日志格式: text/json/both")
    log_directory: str = Field(default="./logs", description="日志目录")

    # 日志轮转配置
    log_max_size_mb: int = Field(default=100, description="单个日志文件最大大小(MB)")
    log_backup_count: int = Field(default=30, description="保留的日志文件数量")
    # 注意：RotatingFileHandler 不支持自动压缩，此配置保留供未来实现
    # 后续任务将实现基于时间的日志轮转和压缩功能
    log_compress_days: int = Field(default=7, description="压缩天数（注意：RotatingFileHandler 不支持自动压缩，此配置保留供未来实现）")

    # 敏感字段脱敏配置（在后续任务中实现）
    # 实际脱敏功能将在 Task 2-3 中实现，包括日志中间件和敏感数据过滤
    sensitive_fields: list[str] = Field(
        default=["authorization", "password", "token", "session_id", "account"],
        description="需要脱敏的字段（注：实际脱敏功能在后续任务中实现）"
    )

    # 监控配置
    monitoring_enabled: bool = Field(default=True, description="是否启用监控")
    metrics_endpoint: str = Field(default="/metrics", description="metrics 端点路径")
    stats_endpoint: str = Field(default="/stats", description="stats 端点路径")
    stats_refresh_sec: int = Field(default=5, description="stats 页面刷新间隔(秒)")

    @field_validator('log_directory')
    @classmethod
    def validate_log_directory(cls, v: str) -> str:
        """验证日志目录路径安全性

        确保日志目录路径是相对路径或在项目目录内，
        防止路径遍历安全风险。
        """
        # 不允许包含路径遍历序列的相对路径
        if '..' in v.replace('\\', '/').split('/'):
            raise ValueError(
                f"log_directory cannot contain '..' for security reasons. "
                f"Use a simple relative path like 'logs' or an absolute path within the project directory."
            )

        path = Path(v).resolve()
        # 获取项目根目录
        project_root = Path(__file__).resolve().parents[2]

        # 如果是绝对路径，必须确保在项目目录内
        if path.is_absolute():
            try:
                # 检查路径是否在项目目录内
                path.relative_to(project_root)
            except ValueError:
                raise ValueError(
                    f"log_directory must be a relative path or within project directory. "
                    f"Got: {v} (resolved to: {path})"
                )
        return v


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    normalized = value.strip()
    return normalized if normalized else None


def _read_config_file(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle) or {}

    if not isinstance(raw_config, dict):
        raise ValueError(f"Config file {config_path} must contain a top-level mapping.")
    return raw_config


def _get_section(config: dict[str, Any], key: str) -> dict[str, Any]:
    section = config.get(key)
    if isinstance(section, dict):
        return section
    return {}


def _get_env(*names: str) -> str | None:
    for name in names:
        value = _normalize_text(os.getenv(name))
        if value is not None:
            return value
    return None


def _to_positive_int(value: Any, *, name: str, default: int) -> int:
    normalized = _normalize_text(value)
    if normalized is None:
        return default

    try:
        number = int(normalized)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc

    if number < 1:
        raise ValueError(f"{name} must be greater than 0.")
    return number


def _to_port(value: Any, *, default: int) -> int:
    port = _to_positive_int(value, name="WEB2API_PORT/SERVER_PORT", default=default)
    if port > 65535:
        raise ValueError("WEB2API_PORT/SERVER_PORT must be <= 65535.")
    return port


# 全局配置实例
_settings: Settings | None = None


def load_settings(
    config_path: Path | None = None,
    *,
    load_env_file: bool = True,
) -> Settings:
    """从配置文件和环境变量加载设置"""
    global _settings

    if load_env_file:
        with suppress(Exception):
            load_dotenv(override=False)

    final_config_path = config_path or DEFAULT_CONFIG_PATH
    config = _read_config_file(final_config_path)
    taiji = _get_section(config, "taiji")
    server = _get_section(config, "server")
    limits = _get_section(config, "limits")
    logging_config = _get_section(config, "logging")
    monitoring_config = _get_section(config, "monitoring")

    # 构建配置字典
    settings_dict = {}

    # Taiji API 配置
    taiji_api_base = (
        _get_env("TAIJI_API_BASE")
        or _normalize_text(taiji.get("api_base"))
        or DEFAULT_TAIJI_API_BASE
    )
    if taiji_api_base:
        settings_dict["taiji_api_base"] = taiji_api_base

    taiji_account = _get_env("TAIJI_ACCOUNT") or _normalize_text(taiji.get("account"))
    if taiji_account:
        settings_dict["taiji_account"] = taiji_account

    taiji_password = _get_env("TAIJI_PASSWORD") or _normalize_text(taiji.get("password"))
    if taiji_password:
        settings_dict["taiji_password"] = taiji_password

    taiji_app_version = (
        _get_env("TAIJI_APP_VERSION")
        or _normalize_text(taiji.get("app_version"))
        or DEFAULT_TAIJI_APP_VERSION
    )
    if taiji_app_version:
        settings_dict["taiji_app_version"] = taiji_app_version

    # 服务器配置
    server_host = (
        _get_env("WEB2API_HOST", "SERVER_HOST")
        or _normalize_text(server.get("host"))
        or DEFAULT_SERVER_HOST
    )
    if server_host:
        settings_dict["server_host"] = server_host

    server_port = _to_port(
        _get_env("WEB2API_PORT", "SERVER_PORT") or server.get("port"),
        default=DEFAULT_SERVER_PORT,
    )
    settings_dict["server_port"] = server_port

    max_concurrent = _to_positive_int(
        _get_env("MAX_CONCURRENT") or limits.get("max_concurrent"),
        name="MAX_CONCURRENT",
        default=DEFAULT_MAX_CONCURRENT,
    )
    settings_dict["max_concurrent"] = max_concurrent

    # 日志配置
    if logging_config:
        if log_level := _normalize_text(logging_config.get("level")):
            settings_dict["log_level"] = log_level
        if log_format := _normalize_text(logging_config.get("format")):
            settings_dict["log_format"] = log_format
        if log_dir := _normalize_text(logging_config.get("directory")):
            settings_dict["log_directory"] = log_dir
        if max_size := logging_config.get("max_size_mb"):
            settings_dict["log_max_size_mb"] = int(max_size)
        if backup_count := logging_config.get("backup_count"):
            settings_dict["log_backup_count"] = int(backup_count)
        if compress_days := logging_config.get("compress_days"):
            settings_dict["log_compress_days"] = int(compress_days)
        if sensitive_fields := logging_config.get("sensitive_fields"):
            if isinstance(sensitive_fields, list):
                settings_dict["sensitive_fields"] = sensitive_fields

    # 监控配置
    if monitoring_config:
        if enabled := monitoring_config.get("enabled"):
            settings_dict["monitoring_enabled"] = bool(enabled)
        if metrics_endpoint := _normalize_text(monitoring_config.get("metrics_endpoint")):
            settings_dict["metrics_endpoint"] = metrics_endpoint
        if stats_endpoint := _normalize_text(monitoring_config.get("stats_endpoint")):
            settings_dict["stats_endpoint"] = stats_endpoint
        if refresh_sec := monitoring_config.get("stats_refresh_sec"):
            settings_dict["stats_refresh_sec"] = int(refresh_sec)

    _settings = Settings(**settings_dict)
    return _settings


def get_settings() -> Settings:
    """获取全局配置实例"""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


# 向后兼容：保留旧的 AppSettings 类
@dataclass(frozen=True)
class AppSettings:
    taiji_api_base: str
    taiji_account: str | None
    taiji_password: str | None
    taiji_app_version: str
    server_host: str
    server_port: int
    max_concurrent: int


def _convert_to_app_settings(settings: Settings) -> AppSettings:
    """将新的 Settings 转换为旧的 AppSettings（向后兼容）"""
    return AppSettings(
        taiji_api_base=settings.taiji_api_base,
        taiji_account=settings.taiji_account,
        taiji_password=settings.taiji_password,
        taiji_app_version=settings.taiji_app_version,
        server_host=settings.server_host,
        server_port=settings.server_port,
        max_concurrent=settings.max_concurrent,
    )
