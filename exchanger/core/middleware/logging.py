import time
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.responses import Response as StarletteResponse

log = structlog.get_logger("exchanger")


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),  # ← no stdlib logging
        cache_logger_on_first_use=True,
    )


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()

    method = request.method
    path = request.url.path
    request_id = request.headers.get("x-request-id")

    try:
        response: StarletteResponse = await call_next(request)

    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        evt = log.bind(method=method, path=path, duration_ms=duration_ms)
        if request_id:
            evt = evt.bind(request_id=request_id)

        evt.exception("unhandled_exception")
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    status = response.status_code

    if request_id:
        response.headers["x-request-id"] = request_id

    evt = log.bind(method=method, path=path, status=status, duration_ms=duration_ms)
    if request_id:
        evt = evt.bind(request_id=request_id)

    if status < 400:
        evt.info("request")
    elif status < 500:
        evt.warning("request")
    else:
        evt.error("request")

    return response
