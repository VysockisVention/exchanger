from typing import Annotated

from fastapi import APIRouter, Query

from exchanger.rates.models import AverageRateResponse, RatesListResponse
from exchanger.rates.service import RateServiceDependency

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("/latest")
async def get_latest_rates(
    service: RateServiceDependency,
) -> RatesListResponse:
    return await service.list_latest_rates()


@router.get("/average")
async def get_average_rate(
    base: Annotated[str, Query(min_length=3, max_length=3, examples="EUR")],
    quote: Annotated[str, Query(min_length=3, max_length=3, examples="USD")],
    service: RateServiceDependency,
) -> AverageRateResponse:
    return await service.calculate_average_rate(base, quote)
