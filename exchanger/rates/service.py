from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends

from exchanger.rates.models import (
    AverageRateResponse,
    CurrencyRate,
    RatesListResponse,
)


@dataclass
class RatesService:
    """
    Rates Service class.

    Stage 2:
        • returns demo data
        • contains domain logic
    Stage 3:
        • will call Lithuanian bank APIs
    Stage 4:
        • will read/write PostgreSQL
    """

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
