import httpx
import pytest
import respx

from exchanger.integrations.jsdelivr import JSDlivir


@pytest.mark.asyncio
async def test_client_property_raises_if_not_initialized():
    api = JSDlivir()
    with pytest.raises(RuntimeError, match="Client not initialized"):
        _ = api.client


@pytest.mark.asyncio
@respx.mock
async def test_get_currencies_success():
    currencies_payload = {
        "usd": "US Dollar",
        "eur": "Euro",
        "ltl": "Lithuanian Litas",
    }

    # JSDlivir uses base_url + relative path
    route = respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.min.json"
    ).mock(return_value=httpx.Response(200, json=currencies_payload))

    async with JSDlivir() as api:
        data = await api.get_currencies()

    assert route.called
    assert data["eur"] == "Euro"
    assert data["usd"] == "US Dollar"


@pytest.mark.asyncio
@respx.mock
async def test_get_rates_success():
    rates_payload = {
        "date": "2026-02-08",
        "eur": {
            "usd": 1.18187619,
            "gbp": 0.86818295,
            "jpy": 185.69184021,
        },
    }

    # date + currShort are interpolated
    route = respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-02-08/v1/currencies/eur.json"
    ).mock(return_value=httpx.Response(200, json=rates_payload))

    async with JSDlivir() as api:
        data = await api.get_rates("eur", "2026-02-08")

    assert route.called
    assert data["date"] == "2026-02-08"
    assert data["eur"]["usd"] == pytest.approx(1.18187619)
    assert data["eur"]["gbp"] == pytest.approx(0.86818295)


@pytest.mark.asyncio
@respx.mock
async def test_get_currencies_http_error_raises():
    # raise_for_status should raise for 4xx/5xx
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.min.json"
    ).mock(return_value=httpx.Response(500, json={"error": "boom"}))

    async with JSDlivir() as api:
        with pytest.raises(httpx.HTTPStatusError):
            await api.get_currencies()


@pytest.mark.asyncio
@respx.mock
async def test_get_rates_http_error_raises():
    respx.get(
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-02-08/v1/currencies/eur.json"
    ).mock(return_value=httpx.Response(404, json={"detail": "not found"}))

    async with JSDlivir() as api:
        with pytest.raises(httpx.HTTPStatusError):
            await api.get_rates("eur", "2026-02-08")


@pytest.mark.asyncio
async def test_context_manager_closes_client():
    api = JSDlivir()

    async with api as opened:
        assert opened._client is not None  # internal check OK for unit test

    # after exit, it should be cleared
    assert api._client is None
