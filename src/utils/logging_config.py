from __future__ import annotations

import logging
from typing import Final

from src.utils.request_context import get_request_id


LOG_FORMAT: Final[str] = (
    "%(asctime)s [%(levelname)s] [request_id=%(request_id)s] %(name)s: %(message)s"
)
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = get_request_id()
        record.request_id = request_id if request_id else "-"
        return True


def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()

    if getattr(root_logger, "_web2api_logging_configured", False):
        root_logger.setLevel(level)
        return

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    request_id_filter = RequestIdFilter()

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.addFilter(request_id_filter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)
            handler.addFilter(request_id_filter)

    root_logger.setLevel(level)
    setattr(root_logger, "_web2api_logging_configured", True)
