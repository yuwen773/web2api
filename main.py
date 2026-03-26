from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.anthropic import router as anthropic_router
from src.api.images import router as images_router
from src.api.monitoring import metrics, stats, stats_json
from src.api.openai import router as openai_router
from src.client.taiji_client import TaijiClient
from src.middleware import RequestContextAndErrorMiddleware
from src.middleware.api_key import ApiKeyAuthMiddleware
from src.middleware.metrics_middleware import MetricsMiddleware
from src.utils.concurrency import configure_semaphore
from src.utils.logging_config import get_logger, setup_logging
from src.utils.metrics_collector import get_metrics_collector
from src.utils.settings import load_settings


setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 日志已在模块级别配置，这里确认配置成功
    logger.info("Logging configured successfully")

    settings = load_settings()
    configure_semaphore(settings.max_concurrent)
    logger.info("Configured max_concurrent=%s", settings.max_concurrent)

    taiji_client = TaijiClient(
        base_url=settings.taiji_api_base,
        app_version=settings.taiji_app_version,
    )
    app.state.taiji_client = taiji_client

    account = settings.taiji_account
    password = settings.taiji_password
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

app.add_middleware(RequestContextAndErrorMiddleware)
app.add_middleware(ApiKeyAuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware, collector=get_metrics_collector())

app.include_router(openai_router)
app.include_router(anthropic_router)
app.include_router(images_router)

# 监控端点
settings = load_settings()
app.add_route(settings.metrics_endpoint, metrics, methods=["GET"])
app.add_route(settings.stats_endpoint + "/json", stats_json, methods=["GET"])
app.add_route(settings.stats_endpoint, stats, methods=["GET"])


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    settings = load_settings()
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )
