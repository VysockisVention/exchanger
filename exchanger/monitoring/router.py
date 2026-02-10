from fastapi import APIRouter

from exchanger.monitoring.schemas import LiveResponse, ReadyResponse

router = APIRouter(tags=["monitoring"])  # no prefix, base-level endpoints


@router.get("/livez")
async def health_live() -> LiveResponse:
    return LiveResponse(status="ok")


@router.get("/readyz")
async def health_ready() -> ReadyResponse:
    return ReadyResponse(status="ok")
