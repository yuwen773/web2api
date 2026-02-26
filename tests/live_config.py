from __future__ import annotations

import os
from dataclasses import dataclass

import pytest
from dotenv import load_dotenv


@dataclass(frozen=True)
class LiveConfig:
    api_base: str
    app_version: str
    account: str
    password: str


def get_live_config() -> LiveConfig:
    load_dotenv(override=False)

    account = os.getenv("TAIJI_ACCOUNT", "").strip()
    password = os.getenv("TAIJI_PASSWORD", "").strip()
    if not account or account == "your_account":
        pytest.skip("Set TAIJI_ACCOUNT before running live integration tests.")
    if not password or password == "your_password":
        pytest.skip("Set TAIJI_PASSWORD before running live integration tests.")

    return LiveConfig(
        api_base=os.getenv("TAIJI_API_BASE", "https://ai.aurod.cn").strip(),
        app_version=os.getenv("TAIJI_APP_VERSION", "2.14.0").strip(),
        account=account,
        password=password,
    )
