import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator
from typing import Callable

import pytest
from _pytest.fixtures import SubRequest
from clickhouse_driver import Client
from polyfactory.pytest_plugin import register_fixture
from pydantic import HttpUrl, SecretStr
from testcontainers.clickhouse import ClickHouseContainer

from collector.clickhouse import ClickhouseClient, ClickHouseDsn
from collector.collector import Collector
from tests.factories import ClientInfoFactory


@pytest.fixture(scope="session")
async def event_loop() -> AsyncGenerator[AbstractEventLoop, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def collector() -> Collector:
    return Collector(
        url=HttpUrl("http://127.0.0.1"),
        password=SecretStr("password"),
    )


@pytest.fixture(scope="session")
def clickhouse_container() -> AsyncGenerator[ClickHouseContainer, None, None]:
    with ClickHouseContainer() as ch:
        ch.start()
        yield ch


@pytest.fixture(scope="session")
def ch_client(
    request: SubRequest, clickhouse_container: ClickHouseContainer
) -> Callable[[], Client]:
    if request.node.get_closest_marker("no_ch"):
        yield
        return

    dsn = ClickHouseDsn(clickhouse_container.get_connection_url())
    client = Client(
        host=dsn.host,
        port=dsn.port,
        database=dsn.path.replace("/", ""),
        user=dsn.username,
        password=dsn.password or "",
    )

    def get_client() -> Client:
        request.addfinalizer(client.disconnect)
        return client

    yield get_client
    client.disconnect()


@pytest.fixture
def prepare_database(ch_client: Callable[[], Client]) -> None:
    client = ch_client()
    tables = client.execute("SHOW TABLES")
    for table in tables:
        table_name = table[0]
        client.execute(f"DROP TABLE IF EXISTS {table_name};")

    ClickhouseClient(client).create_tables()


client_info_factory_fixture = register_fixture(ClientInfoFactory)
