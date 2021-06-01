from typing import TypeVar
from rasierwasser.server.fastapi import create_fastapi_server
from rasierwasser.storage.algebra import Storage

WSGIServer = TypeVar('WSGIServer')


def default_server(storage: Storage, debug: bool = False) -> WSGIServer:
    return create_fastapi_server(storage, debug)