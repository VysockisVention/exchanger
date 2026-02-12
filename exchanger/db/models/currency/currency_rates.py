from datetime import date as localdate
from typing import Any
from sqlalchemy import Date, Integer, String, UniqueConstraint, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from exchanger.db.base import Base

from .currency import Currency


class CurrencyRates(Base):
    __tablename__ = "currency_rates"

    id:                 Mapped[int]                 = mapped_column(Integer, primary_key=True, autoincrement=True)
    date:               Mapped[localdate]           = mapped_column(Date, nullable=False)
    base_currency:      Mapped[str]                 = mapped_column(ForeignKey(Currency.currencyshort))
    rates:              Mapped[dict[str, Any]]    = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint("date", "base_currency", name="uq_currency_rates_date_base"),
        Index("ix_currency_rates_base_date", "base_currency", "date"),
    )
