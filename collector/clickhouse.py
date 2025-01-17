from clickhouse_driver import Client
from loguru import logger
from pydantic import ClickHouseDsn as _ClickHouseDsn
from pydantic import UrlConstraints

from collector.schemas import ClientInfo


class ClickHouseDsn(_ClickHouseDsn):
    _constraints = UrlConstraints(
        allowed_schemes=[
            "clickhouse+native",
            "clickhouse+asynch",
            "clickhouse",
        ],
        default_host="localhost",
        default_port=9000,
    )


CREATE_STATS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS wg_stats (
    id String,
    name String,
    transfer_rx UInt64,
    transfer_tx UInt64,
    address String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;
"""

INSERT_STATS_QUERY = """
INSERT INTO wg_stats (id, name, transfer_rx, transfer_tx, address) VALUES
"""


class ClickhouseClient:
    def __init__(self, client: Client) -> None:
        self._client = client

    def create_tables(self) -> None:
        self._create_stats_table()
        logger.info("Created all tables")

    def insert_stats(self, stats: list[ClientInfo]) -> int:
        data_to_add = [
            {
                "id": str(stat.id),
                "name": stat.name,
                "transfer_rx": stat.transfer_rx,
                "transfer_tx": stat.transfer_tx,
                "address": str(stat.address),
            }
            for stat in stats
        ]
        new_rows = self._client.execute(INSERT_STATS_QUERY, data_to_add)
        logger.info(f"Inserted {new_rows} rows into wg_stats table")
        return new_rows

    def _create_stats_table(self) -> None:
        self._client.execute(CREATE_STATS_TABLE_QUERY)
        logger.info("Created stats table")
