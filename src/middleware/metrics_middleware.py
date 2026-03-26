"""指标收集中间件"""

from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.metrics_collector import MetricsCollector


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""

    def __init__(self, app: ASGIApp, collector: MetricsCollector) -> None:
        """
        Args:
            app: ASGI 应用
            collector: 指标收集器
        """
        super().__init__(app)
        self.collector = collector

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求，收集指标"""
        start_time = time.time()
        method = request.method
        path = request.url.path

        self.collector.increment_in_flight()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            self.collector.record_http_request(
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.collector.record_error(type(e).__name__, str(e))
            raise

        finally:
            self.collector.decrement_in_flight()
