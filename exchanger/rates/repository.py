from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from exchanger.db.models import Currency, CurrencyRates
from exchanger.rates.schemas import (
    CurrenciesResponse,
    CurrencyHistoryRatesResponse,
    CurrencyRatesResponse,
)


async def upsert_currencies(session: AsyncSession, resp: CurrenciesResponse) -> None:
    rows = [
        {"currencyshort": c.currencyshort.lower(), "currency": c.currency} for c in resp.currencies
    ]
    if not rows:
        return

    stmt = insert(Currency).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Currency.currencyshort],
        set_={"currency": stmt.excluded.currency},
    )

    await session.execute(stmt)
    await session.commit()


async def list_currencies(session: AsyncSession) -> CurrenciesResponse:
    stmt = select(Currency.currencyshort, Currency.currency).order_by(Currency.currencyshort)
    result = await session.execute(stmt)
    await session.commit()
    return CurrenciesResponse.model_validate(result.all())


async def get_currency(session: AsyncSession, currencyshort: str) -> str | None:
    stmt = select(Currency.currencyshort).where(Currency.currencyshort == currencyshort.lower())
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()


async def upsert_currency_rates(
    session: AsyncSession, day: date, base_currency: str, currencyrates: CurrencyRatesResponse
):
    payload = currencyrates.model_dump(include={"rates"})

    stmt = insert(CurrencyRates).values(
        date=day,
        base_currency=base_currency.lower(),
        rates=payload,
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[CurrencyRates.date, CurrencyRates.base_currency],
        set_={"rates": stmt.excluded.rates},
    )

    await session.execute(stmt)
    await session.commit()


async def get_currency_rates(
    session: AsyncSession, datefrom: date, dateto: date, currencyshort: str
) -> list[CurrencyHistoryRatesResponse] | None:
    stmt = (
        select(CurrencyRates)
        .where(CurrencyRates.base_currency == currencyshort)
        .where(CurrencyRates.date >= datefrom)
        .where(CurrencyRates.date <= dateto)
        .order_by(CurrencyRates.date.asc())
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        return None
    return [
        CurrencyHistoryRatesResponse(
            date=row.date.strftime("%Y-%m-%d"),
            rates=row.rates["rates"],
        )
        for row in rows
    ]
