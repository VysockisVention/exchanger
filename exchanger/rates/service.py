from dataclasses import dataclass
from datetime import datetime
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
    CurrenciesResponse,
    CurrencyHistoryRatesResponse,
    CurrencyRatesResponse,
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
        except Exception:
            await self.session.rollback()
            log.exception("currencies_db_sync_failed")
            return None

        return resp

    async def list_currencies_from_db(self) -> CurrenciesResponse:
        return await repository.list_currencies(self.session)

    def parse_date(self, date_str):
        try:
            date_parsed = (
                datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_str != "latest"
                else datetime.now().date()
            )
        except ValueError:
            return None
        else:
            return date_parsed

    async def fetch_currency_rates(self, date, currshort) -> dict | None:
        currshort = currshort.lower()

        log_ = log.bind(date=date, currency=currshort)

        date = self.parse_date(date)
        currency = await repository.get_currency(self.session, currshort)

        if date is None or currency is None:
            log_.warning("currency_rates_invalid_date_or_currency")
            return None

        try:
            async with JSDlivir() as api:
                data = await api.get_rates(date=date, currshort=currshort)

            validated_data = CurrencyRatesResponse.model_validate(data)

            await repository.upsert_currency_rates(self.session, date, currency, validated_data)

        except ResponseValidationError:
            log_.exception("currency_rates_model_validation_failed")
        except httpx.HTTPError:
            log_.exception("currency_rates_fetch_failed")
        except Exception:
            log_.exception("currency_rates_unhandeled")
        else:
            return validated_data.model_dump(include={"rates"})

        return None

    async def fetch_currency_rate_history(
        self, currshort, datefrom, dateto
    ) -> list[CurrencyHistoryRatesResponse] | None:
        log_ = log.bind(currshort=currshort, dateFrom=datefrom, dateTo=dateto)

        parsed_date_from = self.parse_date(datefrom)
        parsed_date_to = self.parse_date(dateto)
        currency = await repository.get_currency(self.session, currshort)

        if parsed_date_from is None or parsed_date_to is None:
            log_.warning("currency_rates_invalid_date_tofrom")
            return None

        if currency is None:
            return None

        try:
            return await repository.get_currency_rates(
                self.session, parsed_date_from, parsed_date_to, currency
            )
        except httpx.HTTPError:
            log_.exception("currency_rates_history_fetch_failed")
        except Exception:
            log_.exception("currency_rates_history_unhandeled")

        return None

    def iter_relevant_rates(self, data, base_currency: str, quote_currency: str):
        for r in data.items:
            if r.base_currency == base_currency and r.quote_currency == quote_currency:
                yield r.rate


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
