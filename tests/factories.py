from polyfactory.factories.pydantic_factory import ModelFactory

from collector.schemas import ClientInfo


class ClientInfoFactory(ModelFactory[ClientInfo]): ...
