from typing import TypeVar
from rasierwasser.server.fastapi.fastapi import create_fastapi_server
from rasierwasser.storage.algebra import Storage
from rasierwasser.configuration.main import AuthConfig, DEFAULT_AUTH_CONFIG

WSGIServer = TypeVar('WSGIServer')


def default_server(storage: Storage, debug: bool = False, auth: AuthConfig = DEFAULT_AUTH_CONFIG) -> WSGIServer:
    return create_fastapi_server(storage, debug, auth)