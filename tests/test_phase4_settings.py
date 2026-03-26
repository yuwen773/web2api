from __future__ import annotations

from pathlib import Path

import pytest

from src.utils.settings import load_settings


def _clear_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in [
        "TAIJI_API_BASE",
        "TAIJI_ACCOUNT",
        "TAIJI_PASSWORD",
        "TAIJI_APP_VERSION",
        "MAX_CONCURRENT",
        "WEB2API_HOST",
        "WEB2API_PORT",
        "SERVER_HOST",
        "SERVER_PORT",
        "WEB2API_API_KEYS",
    ]:
        monkeypatch.delenv(env_name, raising=False)


def test_load_settings_reads_config_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_settings_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "taiji:",
                "  api_base: https://example.taiji",
                "  account: from_config_account",
                "  password: from_config_password",
                "  app_version: 9.9.9",
                "server:",
                "  host: 127.0.0.1",
                "  port: 9000",
                "limits:",
                "  max_concurrent: 11",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(config_path=config_path, load_env_file=False)
    assert settings.taiji_api_base == "https://example.taiji"
    assert settings.taiji_account == "from_config_account"
    assert settings.taiji_password == "from_config_password"
    assert settings.taiji_app_version == "9.9.9"
    assert settings.server_host == "127.0.0.1"
    assert settings.server_port == 9000
    assert settings.max_concurrent == 11


def test_load_settings_with_api_keys(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """测试 api_keys 配置项加载"""
    import yaml

    _clear_settings_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    config = {"api": {"api_keys": ["key1", "key2"]}}
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    settings = load_settings(config_path=config_path, load_env_file=False)
    assert settings.api_keys == ["key1", "key2"]


def test_load_settings_api_keys_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """测试环境变量配置 api_keys"""
    _clear_settings_env(monkeypatch)
    monkeypatch.setenv("WEB2API_API_KEYS", "env_key1,env_key2")

    settings = load_settings(load_env_file=False)
    assert settings.api_keys == ["env_key1", "env_key2"]


def test_load_settings_api_keys_env_overrides_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """测试环境变量覆盖配置文件中的 api_keys"""
    import yaml

    _clear_settings_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    config = {"api": {"api_keys": ["key_from_config"]}}
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    monkeypatch.setenv("WEB2API_API_KEYS", "key_from_env")

    settings = load_settings(config_path=config_path, load_env_file=False)
    assert settings.api_keys == ["key_from_env"]


def test_env_overrides_config_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _clear_settings_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "taiji:",
                "  api_base: https://from-config",
                "  account: config_account",
                "  password: config_password",
                "limits:",
                "  max_concurrent: 3",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("TAIJI_API_BASE", "https://from-env")
    monkeypatch.setenv("TAIJI_ACCOUNT", "env_account")
    monkeypatch.setenv("TAIJI_PASSWORD", "env_password")
    monkeypatch.setenv("MAX_CONCURRENT", "7")

    settings = load_settings(config_path=config_path, load_env_file=False)
    assert settings.taiji_api_base == "https://from-env"
    assert settings.taiji_account == "env_account"
    assert settings.taiji_password == "env_password"
    assert settings.max_concurrent == 7
