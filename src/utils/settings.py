from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "config.yaml"
DEFAULT_TAIJI_API_BASE = "https://ai.aurod.cn"
DEFAULT_TAIJI_APP_VERSION = "2.14.0"
DEFAULT_SERVER_HOST = "0.0.0.0"
DEFAULT_SERVER_PORT = 8000
DEFAULT_MAX_CONCURRENT = 5


@dataclass(frozen=True)
class AppSettings:
    taiji_api_base: str
    taiji_account: str | None
    taiji_password: str | None
    taiji_app_version: str
    server_host: str
    server_port: int
    max_concurrent: int


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


def load_settings(
    config_path: Path | None = None,
    *,
    load_env_file: bool = True,
) -> AppSettings:
    if load_env_file:
        load_dotenv(override=False)

    final_config_path = config_path or DEFAULT_CONFIG_PATH
    config = _read_config_file(final_config_path)
    taiji = _get_section(config, "taiji")
    server = _get_section(config, "server")
    limits = _get_section(config, "limits")

    taiji_api_base = (
        _get_env("TAIJI_API_BASE")
        or _normalize_text(taiji.get("api_base"))
        or DEFAULT_TAIJI_API_BASE
    )
    taiji_account = _get_env("TAIJI_ACCOUNT") or _normalize_text(taiji.get("account"))
    taiji_password = _get_env("TAIJI_PASSWORD") or _normalize_text(taiji.get("password"))
    taiji_app_version = (
        _get_env("TAIJI_APP_VERSION")
        or _normalize_text(taiji.get("app_version"))
        or DEFAULT_TAIJI_APP_VERSION
    )

    server_host = (
        _get_env("WEB2API_HOST", "SERVER_HOST")
        or _normalize_text(server.get("host"))
        or DEFAULT_SERVER_HOST
    )
    server_port = _to_port(
        _get_env("WEB2API_PORT", "SERVER_PORT") or server.get("port"),
        default=DEFAULT_SERVER_PORT,
    )
    max_concurrent = _to_positive_int(
        _get_env("MAX_CONCURRENT") or limits.get("max_concurrent"),
        name="MAX_CONCURRENT",
        default=DEFAULT_MAX_CONCURRENT,
    )

    return AppSettings(
        taiji_api_base=taiji_api_base,
        taiji_account=taiji_account,
        taiji_password=taiji_password,
        taiji_app_version=taiji_app_version,
        server_host=server_host,
        server_port=server_port,
        max_concurrent=max_concurrent,
    )
