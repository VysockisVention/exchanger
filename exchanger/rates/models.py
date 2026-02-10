from datetime import datetime

from pydantic import BaseModel, Field


class CurrencyRate(BaseModel):
    provider: str = Field(..., examples=["swedbank"])
    base_currency: str = Field(..., min_length=3, max_length=3, examples=["EUR"])
    quote_currency: str = Field(..., min_length=3, max_length=3, examples=["USD"])
    rate: float = Field(..., gt=0, examples=[1.0923])
    timestamp: datetime


class RatesListResponse(BaseModel):
    items: list[CurrencyRate]


class AverageRateResponse(BaseModel):
    base_currency: str
    quote_currency: str
    average_rate: float
    providers: int
