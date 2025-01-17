import datetime as dt
import uuid
from ipaddress import IPv4Address

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ClientInfo(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
    address: IPv4Address
    created_at: dt.datetime
    downloadable_config: bool
    enabled: bool
    id: uuid.UUID
    latest_handshake_at: dt.datetime
    name: str
    persistent_keepalive: str
    public_key: str
    transfer_rx: int
    transfer_tx: int
    updated_at: dt.datetime
