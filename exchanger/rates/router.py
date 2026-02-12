from fastapi import APIRouter

from exchanger.rates.schemas import (
    CurrenciesResponse,
    CurrencyHistoryRatesResponse,
)
from exchanger.rates.service import RateServiceDependency

router = APIRouter(prefix="/rates", tags=["rates"])


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
) -> dict | None:
    return await service.fetch_currency_rates(date, currshort)


@router.get("/currencies/rates/history/{currshort}/{datefrom}")
async def get_currency_rates_history(
    currshort: str,
    service: RateServiceDependency,
    datefrom: str,
    dateto: str = "latest",
) -> list[CurrencyHistoryRatesResponse] | None:
    return await service.fetch_currency_rate_history(currshort, datefrom, dateto)
