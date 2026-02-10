import pytest

from exchanger.rates.service import RatesService

pytestmark = pytest.mark.asyncio


async def test_list_latest_rates_returns_demo_items():
    service = RatesService()

    data = await service.list_latest_rates()

    assert len(data.items) == 2
    assert {r.provider for r in data.items} == {"swedbank", "seb"}


async def test_calculate_average_rate_for_existing_pair():
    service = RatesService()

    result = await service.calculate_average_rate("EUR", "USD")

    assert result.base_currency == "EUR"
    assert result.quote_currency == "USD"
    assert result.providers == 2
    # (1.09 + 1.10) / 2 = 1.095
    assert result.average_rate == pytest.approx(1.095)


async def test_calculate_average_rate_for_missing_pair_returns_zero():
    service = RatesService()

    result = await service.calculate_average_rate("EUR", "JPY")

    assert result.base_currency == "EUR"
    assert result.quote_currency == "JPY"
    assert result.providers == 0
    assert result.average_rate == 0.0
