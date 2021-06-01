from argparse import ArgumentParser
from pydantic import BaseModel
from uvicorn import run
from rasierwasser.server import WSGIServer
from rasierwasser.server import default_server
from rasierwasser.configuration.storage import create_storage_from_config, Storage
from rasierwasser.configuration.main import RasierwasserConfig, load_config_from_file


class RasierwasserInstance(BaseModel):
    storage: Storage
    application: WSGIServer
    config: RasierwasserConfig


def create_rasierwasser_instance(config: RasierwasserConfig) -> RasierwasserInstance:
    storage: Storage = create_storage_from_config(config.storage)
    return RasierwasserInstance(
        storage=storage,
        application=default_server(storage, config.server.debug),
        config=config
    )


def start_service(config: str, encoding: str) -> None:
    config: RasierwasserConfig = load_config_from_file(config, encoding)
    rasierwasser: RasierwasserInstance = create_rasierwasser_instance(config)
    run(rasierwasser.application, host=config.server.hostname, port=config.server.port)


def main():
    parser: ArgumentParser = ArgumentParser(description='Start Rasierwasser service')
    parser.add_argument('--config', default='/etc/rasierwasser/rasierwasser.yml', help='Config file location.')
    parser.add_argument('--encoding', default='utf-8', help='Config file encoding.')
    args = parser.parse_args()
    start_service(args.config, args.encoding)