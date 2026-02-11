from typing import Annotated

from fastapi import APIRouter, Query

from exchanger.rates.schemas import (
    AverageRateResponse,
    CurrenciesResponse,
    CurrencyRatesResponse,
    RatesListResponse,
)
from exchanger.rates.service import RateServiceDependency

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("/latest")
async def get_latest_rates(
    service: RateServiceDependency,
) -> RatesListResponse:
    return await service.list_latest_rates()


@router.get("/average")
async def get_average_rate(
    base: Annotated[str, Query(min_length=3, max_length=3, examples="EUR")],  # type: ignore
    quote: Annotated[str, Query(min_length=3, max_length=3, examples="USD")],  # type: ignore
    service: RateServiceDependency,
) -> AverageRateResponse:
    return await service.calculate_average_rate(base, quote)


@router.post("/currencies/sync")
async def sync_currencies(
    service: RateServiceDependency,
) -> CurrenciesResponse | None:
    return await service.sync_currencies()


@router.get("/currencies")
async def get_currencies_from_db(
    service: RateServiceDependency,
) -> CurrenciesResponse:
    return await service.list_currencies_from_db()


@router.get("/currencies/rates/{currshort}")
async def get_currency_rates(
    currshort: str,
    service: RateServiceDependency,
    date: str = "latest",
) -> CurrencyRatesResponse | None:
    return await service.fetch_currency_rates(date, currshort)
