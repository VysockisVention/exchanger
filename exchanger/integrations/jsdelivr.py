from typing import ClassVar

import httpx


class JSDlivir:
    base_url: ClassVar[str] = "https://cdn.jsdelivr.net/npm/@fawazahmed0/"
    timeout: float = 30.0
    limits: ClassVar[httpx.Limits] = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    headers: ClassVar[dict[str, str]] = {"Accept": "application/json"}

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        limits: httpx.Limits | None = None,
        headers: dict[str, str] | None = None,
    ):
        self._base_url = base_url or self.base_url
        self._timeout = self.timeout if timeout is None else timeout
        self._limits = limits or self.limits
        # avoid sharing same dict object if you later mutate
        self._headers = dict(headers or self.headers)

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "JSDlivir":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            limits=self._limits,
            headers=self._headers,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with JSDlivir() as api:'")
        return self._client

    async def get_currencies(self) -> dict:
        path = "currency-api@latest/v1/currencies.min.json"

        resp = await self.client.get(path)
        resp.raise_for_status()
        return resp.json()

    async def get_rates(self, currshort, date):
        path = f"currency-api@{date}/v1/currencies/{currshort}.json"

        resp = await self.client.get(path)
        resp.raise_for_status()
        return resp.json()
