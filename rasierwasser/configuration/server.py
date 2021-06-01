from pydantic import BaseModel


class ServerConfig(BaseModel):
    hostname: str
    port: int
    debug: bool = False
