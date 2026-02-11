from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from exchanger.db.models import Currency
from exchanger.rates.schemas import CurrenciesResponse


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


async def list_currencies(session: AsyncSession) -> CurrenciesResponse:
    stmt = select(Currency.currencyshort, Currency.currency).order_by(Currency.currencyshort)
    result = await session.execute(stmt)

    return CurrenciesResponse.model_validate(result.all())


async def get_currency(session: AsyncSession, currencyshort: str) -> str | None:
    stmt = select(Currency.currency).where(Currency.currencyshort == currencyshort.lower())
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
