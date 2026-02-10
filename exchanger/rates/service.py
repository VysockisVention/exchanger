from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.exceptions import ResponseValidationError

from exchanger.core.middleware.logging import logger
from exchanger.integrations.jsdelivr import JSDlivir
from exchanger.rates.models import (
    AverageRateResponse,
    CurrenciesResponse,
    CurrencyRate,
    CurrencyRatesResponse,
    RatesListResponse,
)


@dataclass
class RatesService:
    """
    Rates Service class.

    Documentation
    """

    async def fetch_currencies(self) -> CurrenciesResponse | None:
        try:
            async with JSDlivir() as api:
                data = await api.get_currencies()
            validated_data = CurrenciesResponse.model_validate(data)
        except ResponseValidationError:
            logger.warning("Currency API returned bad format returning none")
        except httpx.HTTPError as httpError:
            logger.error(f"Currency fetch failed: {httpError}")
        except Exception as e:
            logger.error(f"UNHANDELED ERROR: {e}")
        else:
            return validated_data

        return None

    async def is_valid_date(self, date_str):
        if date_str == "latest":
            return True

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False
        else:
            return True

    async def is_valid_currency(self, currshort: str) -> bool:
        resp = await self.fetch_currencies()
        if resp is None:
            return False

        return any(c.currencyshort == currshort for c in resp.currencies)

    async def fetch_currency_rates(self, date, currshort):
        currshort = currshort.lower()
        if not await self.is_valid_date(date):
            return None

        if not await self.is_valid_currency(currshort):
            return None

        try:
            async with JSDlivir() as api:
                data = await api.get_rates(date=date, currshort=currshort)

            return CurrencyRatesResponse.model_validate(data)
        except ResponseValidationError:
            logger.warning("Currency rates API returned bad format returning none")
        except httpx.HTTPError as httpError:
            logger.error(f"Currency rates fetch failed: {httpError}")
        except Exception as e:
            logger.error(f"UNHANDELED ERROR: {e}")

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


def get_rates_service() -> RatesService:
    """
    FastAPI dependency provider.

    Later:
        • inject DB session
        • inject HTTP clients
        • inject config
    """
    return RatesService()


RateServiceDependency = Annotated[RatesService, Depends(get_rates_service)]
