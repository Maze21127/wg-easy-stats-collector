from typing import Callable

import pytest
from clickhouse_driver import Client

from collector.clickhouse import ClickhouseClient
from tests.factories import ClientInfoFactory


@pytest.fixture
def client(ch_client: Callable[[], Client]) -> ClickhouseClient:
    ch_client = ch_client()
    return ClickhouseClient(ch_client)


def test_create_tables(client: ClickhouseClient):
    client.create_tables()
    res = client._client.execute("SHOW TABLES")

    assert len(res) == 1
    assert res[0][0] == "wg_stats"


@pytest.mark.usefixtures("prepare_database")
def test_insert_many_clients_info(
    client_info_factory: ClientInfoFactory,
    client: ClickhouseClient,
):
    clients_count = 10
    clients = [client_info_factory.build() for _ in range(clients_count)]
    rows = client.insert_stats(clients)
    assert rows == clients_count

    res = client._client.execute("SELECT count(*) from wg_stats")
    assert res[0][0] == clients_count


@pytest.mark.usefixtures("prepare_database")
def test_insert_one_client_info(
    client_info_factory: ClientInfoFactory,
    client: ClickhouseClient,
):
    rows = client.insert_stats([client_info_factory.build()])
    assert rows == 1

    res = client._client.execute("SELECT count(*) from wg_stats")
    assert res[0][0] == 1
