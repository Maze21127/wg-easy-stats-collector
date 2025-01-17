from types import TracebackType
from typing import Self
from urllib.parse import urljoin

from httpx import AsyncClient, Response
from loguru import logger
from pydantic import HttpUrl, SecretStr

from collector.schemas import ClientInfo


class Collector:
    def __init__(self, url: HttpUrl, password: SecretStr) -> None:
        self.url = url.unicode_string()
        self.password = password
        self._client = AsyncClient()

    async def authenticate(self) -> Response:
        url = urljoin(self.url, "api/session")
        r = await self._client.post(
            url, json={"password": self.password.get_secret_value()}
        )
        r.raise_for_status()
        logger.info("Auth success")
        return r

    async def get_data(self) -> list[ClientInfo]:
        url = urljoin(self.url, "api/wireguard/client")
        r = await self._client.get(url)
        r.raise_for_status()
        clients = [ClientInfo.model_validate(i) for i in r.json()]
        logger.info(f"Fetched {len(clients)} clients")
        return clients

    async def __aenter__(self) -> Self:
        await self.authenticate()
        logger.debug("Auth success")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        await self._client.aclose()
        logger.debug("Closed client")
