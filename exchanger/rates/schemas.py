from typing import Any

from pydantic import BaseModel, ConfigDict, computed_field, model_validator


class CurrencyResponse(BaseModel):
    currencyshort: str
    currency: str


class CurrenciesResponse(BaseModel):
    currencies: list[CurrencyResponse]

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, raw: Any):
        # Case 1: API returns dict { "eur": "Euro", ... }
        if isinstance(raw, dict):
            return {"currencies": [{"currencyshort": k, "currency": v} for k, v in raw.items()]}

        # Case 2: repository passes list type
        if isinstance(raw, list):
            return {"currencies": [{"currencyshort": k, "currency": v} for k, v in raw]}

        return raw


class CurrencyRateResponse(BaseModel):
    currencyshort: str
    rate: float


class CurrencyRatesResponse(BaseModel):
    model_config = ConfigDict(extra="allow")  # captures dynamic keys into model_extra

    date: str

    def _dynamic_currency_and_map(self) -> tuple[str, dict[str, float]]:
        extra = self.model_extra or {}
        if not extra:
            return "", {}

        # your payload has exactly 1 dynamic currency key besides "date"
        currency, rate_map = next(iter(extra.items()))
        if not isinstance(rate_map, dict):
            return currency, {}
        return currency, rate_map

    @computed_field
    @property
    def currency(self) -> str:
        currency, _ = self._dynamic_currency_and_map()
        return currency

    @computed_field
    @property
    def rates(self) -> list[CurrencyRateResponse]:
        _, rate_map = self._dynamic_currency_and_map()
        return [CurrencyRateResponse(currencyshort=k, rate=v) for k, v in rate_map.items()]


class CurrencyHistoryRatesResponse(BaseModel):
    date: str
    rates: list[CurrencyRateResponse]
