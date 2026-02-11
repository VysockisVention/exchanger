from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

import httpx
import structlog
from fastapi import Depends
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from exchanger.db.session import DatabaseSession
from exchanger.integrations.jsdelivr import JSDlivir
from exchanger.rates import repository
from exchanger.rates.schemas import (
    AverageRateResponse,
    CurrenciesResponse,
    CurrencyRate,
    CurrencyRatesResponse,
    RatesListResponse,
)

log = structlog.get_logger(__name__)


@dataclass
class RatesService:
    """
    Rates Service class.

    Documentation
    """

    session: AsyncSession

    async def fetch_currencies(self) -> CurrenciesResponse | None:
        try:
            async with JSDlivir() as api:
                data = await api.get_currencies()
            validated_data = CurrenciesResponse.model_validate(data)
        except ResponseValidationError:
            log.exception("currencies_model_validation_failed")
        except httpx.HTTPError:
            log.exception("currencies_fetch_failed")
        except Exception:
            log.exception("currencies_unhandeled")
        else:
            return validated_data

        return None

    async def sync_currencies(self) -> CurrenciesResponse | None:
        resp = await self.fetch_currencies()
        if resp is None:
            return None

        try:
            await repository.upsert_currencies(self.session, resp)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            log.exception("currencies_db_sync_failed")
            return None

        return resp

    async def list_currencies_from_db(self) -> CurrenciesResponse:
        return await repository.list_currencies(self.session)

    def is_valid_date(self, date_str):
        if date_str == "latest":
            return True

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False
        else:
            return True

    async def is_valid_currency(self, currshort: str) -> bool:
        return await repository.get_currency(self.session, currshort) is not None

    async def fetch_currency_rates(self, date, currshort):
        currshort = currshort.lower()

        log_ = log.bind(date=date, currency=currshort)

        if not self.is_valid_date(date):
            log_.warning("currency_rates_invalid_date")
            return None

        if not await self.is_valid_currency(currshort):
            log_.warning("currency_rates_invalid_currency")
            return None

        try:
            async with JSDlivir() as api:
                data = await api.get_rates(date=date, currshort=currshort)

            return CurrencyRatesResponse.model_validate(data)

        except ResponseValidationError:
            log_.exception("currency_rates_model_validation_failed")
        except httpx.HTTPError:
            log_.exception("currency_rates_fetch_failed")
        except Exception:
            log_.exception("currency_rates_unhandeled")

        return None

    async def list_latest_rates(self) -> RatesListResponse:
        now = datetime.now(UTC)

        demo_rates = [
            CurrencyRate(
                provider="swedbank",
                base_currency="EUR",
                quote_currency="USD",
                rate=1.09,
                timestamp=now,
            ),
            CurrencyRate(
                provider="seb",
                base_currency="EUR",
                quote_currency="USD",
                rate=1.10,
                timestamp=now,
            ),
        ]

        return RatesListResponse(items=demo_rates)

    def iter_relevant_rates(self, data, base_currency: str, quote_currency: str):
        for r in data.items:
            if r.base_currency == base_currency and r.quote_currency == quote_currency:
                yield r.rate

    async def calculate_average_rate(
        self,
        base_currency: str,
        quote_currency: str,
    ) -> AverageRateResponse:
        data = await self.list_latest_rates()

        total = 0.0
        count = 0

        for rate in self.iter_relevant_rates(data, base_currency, quote_currency):
            total += rate
            count += 1

        average_rate = total / count if count else 0.0
        return AverageRateResponse(
            base_currency=base_currency,
            quote_currency=quote_currency,
            average_rate=average_rate,
            providers=count,
        )


def get_rates_service(session: DatabaseSession) -> RatesService:
    """
    FastAPI dependency provider.

    Later:
        • inject DB session
        • inject HTTP clients
        • inject config
    """
    return RatesService(session=session)


RateServiceDependency = Annotated[RatesService, Depends(get_rates_service)]
