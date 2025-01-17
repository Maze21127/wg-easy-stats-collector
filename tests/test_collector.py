from unittest.mock import AsyncMock, patch
from urllib.parse import urljoin

import httpx
import pytest
from httpx import Request, Response

from collector.collector import Collector
from collector.schemas import ClientInfo
from tests.factories import ClientInfoFactory


def mock_auth_post(mock_post: AsyncMock, collector: Collector):
    mock_post.return_value = Response(
        httpx.codes.OK,
        json={"success": "true"},
        request=Request(
            method="post", url=urljoin(collector.url, "api/session")
        ),
    )


@pytest.mark.no_ch
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_collector_auth(
    mock_post: AsyncMock,
    collector: Collector,
):
    mock_auth_post(mock_post, collector)
    r = await collector.authenticate()
    assert r.is_success


@pytest.mark.no_ch
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
async def test_collector_get_data(
    mock_post: AsyncMock,
    mock_get: AsyncMock,
    collector: Collector,
    client_info_factory: ClientInfoFactory,
):
    mock_auth_post(mock_post, collector)
    mock_get.return_value = Response(
        httpx.codes.OK,
        request=Request(
            method="get", url=urljoin(collector.url, "api/wireguard/client")
        ),
        json=[
            client_info_factory.build().model_dump(mode="json")
            for _ in range(10)
        ],
    )

    async with collector as client:
        data = await client.get_data()
        assert isinstance(data, list)
        assert isinstance(data[0], ClientInfo)
