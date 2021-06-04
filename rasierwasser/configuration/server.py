from typing import Dict, Any, TypeVar
from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    policy: str
    parameter: Dict[str, Any] = Field(default_factory=dict)


class ServerConfig(BaseModel):
    hostname: str
    port: int
    debug: bool = False


SecurityScheme = TypeVar('SecurityScheme')

DEFAULT_AUTH_CONFIG = AuthConfig(policy='snakeoil')





