from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.anthropic import router as anthropic_router
from src.api.openai import router as openai_router
from src.client.taiji_client import TaijiClient


logger = logging.getLogger(__name__)


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _get_env_int(name: str, default: int) -> int:
    raw = _get_env(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    load_dotenv(override=False)

    taiji_client = TaijiClient(
        base_url=_get_env("TAIJI_API_BASE", "https://ai.aurod.cn") or "https://ai.aurod.cn",
        app_version=_get_env("TAIJI_APP_VERSION", "2.14.0") or "2.14.0",
    )
    app.state.taiji_client = taiji_client

    account = _get_env("TAIJI_ACCOUNT")
    password = _get_env("TAIJI_PASSWORD")
    if account and password:
        await taiji_client.login(account, password)
        logger.info("Taiji client logged in during startup.")
    else:
        logger.warning(
            "TAIJI_ACCOUNT/TAIJI_PASSWORD not set; skipping Taiji login during startup."
        )

    try:
        yield
    finally:
        await taiji_client.close()


app = FastAPI(
    title="web2api",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(openai_router)
app.include_router(anthropic_router)


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=_get_env("WEB2API_HOST", "0.0.0.0") or "0.0.0.0",
        port=_get_env_int("WEB2API_PORT", 8000),
        reload=False,
    )
