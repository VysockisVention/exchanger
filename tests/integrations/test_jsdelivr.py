import httpx
import pytest

from exchanger.integrations.jsdelivr import JSDlivir


@pytest.mark.asyncio
async def test_client_property_raises_if_not_initialized():
    api = JSDlivir()
    with pytest.raises(RuntimeError, match="Client not initialized"):
        _ = api.client


@pytest.mark.asyncio
async def test_get_currencies_success(httpx_mock):
    currencies_payload = {
        "usd": "US Dollar",
        "eur": "Euro",
        "ltl": "Lithuanian Litas",
    }

    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.min.json"
    httpx_mock.add_response(method="GET", url=url, json=currencies_payload, status_code=200)

    async with JSDlivir() as api:
        data = await api.get_currencies()

    assert data["eur"] == "Euro"
    assert data["usd"] == "US Dollar"


@pytest.mark.asyncio
async def test_get_rates_success(httpx_mock):
    rates_payload = {
        "date": "2026-02-08",
        "eur": {
            "usd": 1.18187619,
            "gbp": 0.86818295,
            "jpy": 185.69184021,
        },
    }

    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-02-08/v1/currencies/eur.json"
    httpx_mock.add_response(method="GET", url=url, json=rates_payload, status_code=200)

    async with JSDlivir() as api:
        data = await api.get_rates("eur", "2026-02-08")

    assert data["date"] == "2026-02-08"
    assert data["eur"]["usd"] == pytest.approx(1.18187619)
    assert data["eur"]["gbp"] == pytest.approx(0.86818295)


@pytest.mark.asyncio
async def test_get_currencies_http_error_raises(httpx_mock):
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.min.json"
    httpx_mock.add_response(method="GET", url=url, json={"error": "boom"}, status_code=500)

    async with JSDlivir() as api:
        with pytest.raises(httpx.HTTPStatusError):
            await api.get_currencies()


@pytest.mark.asyncio
async def test_get_rates_http_error_raises(httpx_mock):
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-02-08/v1/currencies/eur.json"
    httpx_mock.add_response(method="GET", url=url, json={"detail": "not found"}, status_code=404)

    async with JSDlivir() as api:
        with pytest.raises(httpx.HTTPStatusError):
            await api.get_rates("eur", "2026-02-08")


@pytest.mark.asyncio
async def test_context_manager_closes_client():
    api = JSDlivir()

    async with api as opened:
        assert opened._client is not None  # internal check OK for unit test

    assert api._client is None
