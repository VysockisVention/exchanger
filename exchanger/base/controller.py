from fastapi import APIRouter

from exchanger.base.models import LiveResponse, ReadyResponse

router = APIRouter(tags=["base"])  # no prefix, base-level endpoints


@router.get("/health")
async def health_live() -> LiveResponse:
    return LiveResponse(status=True)


@router.get("/health/ready")
async def health_ready() -> ReadyResponse:
    return ReadyResponse(ready=True)
