import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.responses import Response as StarletteResponse

logger = logging.getLogger("exchanger")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.perf_counter()

    endpoint = f"{request.method} {request.url.path}"

    try:
        response: StarletteResponse = await call_next(request)

    except Exception as exc:
        duration = round((time.perf_counter() - start) * 1000, 2)

        logger.exception(
            f"{endpoint} | UNHANDLED_EXCEPTION | {type(exc).__name__}",
            extra={
                "request_id": request_id,
                "duration_ms": duration,
            },
        )
        raise

    duration = round((time.perf_counter() - start) * 1000, 2)

    response.headers["x-request-id"] = request_id

    status = response.status_code

    if status < 400:
        logger.info(f"{endpoint} | OK | {status}", extra={"request_id": request_id})
        return response

    if 400 <= status < 500:
        logger.warning(
            f"{endpoint} | CLIENT_ERROR | {status}",
            extra={"request_id": request_id, "duration_ms": duration},
        )
        return response

    logger.error(
        f"{endpoint} | SERVER_ERROR | {status}",
        extra={"request_id": request_id, "duration_ms": duration},
    )
    return response
