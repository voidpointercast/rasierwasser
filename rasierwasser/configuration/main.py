from typing import Callable, TextIO, Dict, Any, Optional, Union
from pathlib import Path
from pydantic import BaseModel
from json import load as json_load
from yaml import load as yaml_load
from toml import load as toml_load
from rasierwasser.configuration.storage import StorageBackend
from rasierwasser.configuration.server import ServerConfig, AuthConfig, DEFAULT_AUTH_CONFIG


class RasierwasserConfig(BaseModel):
    server: ServerConfig
    storage: StorageBackend
    auth: AuthConfig = DEFAULT_AUTH_CONFIG


_EXTENSION_MAP: Dict[str, Callable[[TextIO], Dict[str, Any]]] = dict(
    yaml=yaml_load,
    yml=yaml_load,
    toml=toml_load,
    json=json_load
)


def load_config_from_file(filepath: Union[Path, str], encoding: str = 'utf-8') -> RasierwasserConfig:
    filepath = filepath if isinstance(filepath, str) else str(filepath)
    extension: str = filepath.rsplit('.', 1)[-1].lower()
    extension_handler: Optional[Callable[[TextIO], Dict[str, Any]]] = _EXTENSION_MAP.get(extension)
    if not extension_handler:
        raise TypeError(f'Could not parse configuration file {filepath}, unknown extension: {extension}')
    with open(filepath, encoding=encoding) as src:
        return RasierwasserConfig(**extension_handler(src))





