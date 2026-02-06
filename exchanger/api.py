from fastapi import APIRouter

from exchanger.base import router as base_router
from exchanger.rates import router as rates_router

# from exchanger.auth import router as auth_router
# from exchanger.providers import router as providers_router

# Versioned API
api_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")

v1_router.include_router(rates_router)
# v1_router.include_router(auth_router)
# v1_router.include_router(providers_router)

api_router.include_router(v1_router)

# Root-level (non-versioned) endpoints
root_router = APIRouter()
root_router.include_router(base_router)
