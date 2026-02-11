from contextlib import asynccontextmanager

from fastapi import FastAPI

from exchanger.api import api_router, root_router
from exchanger.core.config import get_settings
from exchanger.core.middleware.logging import request_logging_middleware, setup_logging
from exchanger.db.session import setup_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with setup_db():
        yield


def create_app() -> FastAPI:
    settings = get_settings()

    setup_logging()  # later can use settings.debug

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    app.middleware("http")(request_logging_middleware)

    app.include_router(root_router)
    app.include_router(api_router)

    return app


app = create_app()
