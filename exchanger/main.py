from fastapi import FastAPI

from exchanger.api import api_router, root_router
from exchanger.core.middleware.logging import request_logging_middleware, setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title="Exchanger API", version="0.1.0")

    app.middleware("http")(request_logging_middleware)

    app.include_router(root_router)
    app.include_router(api_router)

    return app


app = create_app()
