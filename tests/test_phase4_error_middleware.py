from __future__ import annotations

import logging

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.middleware import RequestContextAndErrorMiddleware
from src.utils.logging_config import configure_logging


class ValidationBody(BaseModel):
    text: str


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextAndErrorMiddleware)

    @app.get("/ok")
    async def ok() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/http401")
    async def http401() -> dict[str, str]:
        raise HTTPException(status_code=401, detail="invalid credential")

    @app.post("/validate")
    async def validate(body: ValidationBody) -> dict[str, str]:
        return {"text": body.text}

    @app.get("/boom")
    async def boom() -> dict[str, str]:
        raise RuntimeError("boom")

    return app


@pytest.mark.asyncio
async def test_request_middleware_returns_request_id_header_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    configure_logging()
    app = _build_app()

    caplog.set_level(logging.INFO)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/ok", headers={"x-request-id": "req-from-test"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-from-test"
    assert any("API request started" in record.getMessage() for record in caplog.records)
    assert any("API request finished" in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_http_exception_is_mapped_to_standard_error_format() -> None:
    app = _build_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/http401")

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "auth_failed"
    assert body["error"]["status"] == 401
    assert body["detail"] == "invalid credential"
    assert body["error"]["request_id"]


@pytest.mark.asyncio
async def test_validation_error_is_mapped_to_400() -> None:
    app = _build_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/validate", json={})

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "bad_request"
    assert body["error"]["status"] == 400
    assert "body.text" in body["detail"]


@pytest.mark.asyncio
async def test_unhandled_exception_is_mapped_to_500() -> None:
    app = _build_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_server_error"
    assert body["error"]["status"] == 500
    assert body["detail"] == "Internal server error."
