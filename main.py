from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.anthropic import router as anthropic_router
from src.api.openai import router as openai_router
from src.client.taiji_client import TaijiClient
from src.middleware import RequestContextAndErrorMiddleware
from src.utils.concurrency import configure_semaphore
from src.utils.logging_config import configure_logging
from src.utils.settings import load_settings


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
    settings = load_settings()
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )
