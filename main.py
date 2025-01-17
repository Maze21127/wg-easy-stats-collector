import asyncio
import os

from clickhouse_driver import Client
from dotenv import load_dotenv
from loguru import logger
from pydantic import HttpUrl, SecretStr

from collector.clickhouse import ClickhouseClient, ClickHouseDsn
from collector.collector import Collector


async def main() -> None:
    load_dotenv(".env")
    wg_url = HttpUrl(os.environ["WG_URL"])
    wg_password = SecretStr(os.environ["WG_PASSWORD"])
    collector = Collector(
        url=wg_url,
        password=wg_password,
    )

    async with collector as client:
        data = await client.get_data()

    ch_dsn = ClickHouseDsn(os.environ["CH_DSN"])
    ch_client = Client(
        host=ch_dsn.host,
        port=ch_dsn.port,
        database=ch_dsn.path.replace("/", ""),
        user=ch_dsn.username,
        password=ch_dsn.password or "",
    )
    client = ClickhouseClient(ch_client)
    client.create_tables()
    inserted = client.insert_stats(data)
    logger.info(f"Inserted {inserted} rows")


if __name__ == "__main__":
    asyncio.run(main())
