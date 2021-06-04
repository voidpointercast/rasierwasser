from typing import Dict, Tuple, Callable, Any, Type
from pydantic import BaseModel, Field
from rasierwasser.storage.algebra import Storage
from rasierwasser.storage.database.engine import create_database_storage


class StorageBackend(BaseModel):
    backend: str
    parameter: Dict[str, Any]


class DatabaseBackend(BaseModel):
    db_url: str
    verify: bool = True
    options: Dict[str, str] = Field(default_factory=dict)


_BACKEND_MAP: Dict[str, Tuple[Type[BaseModel], Callable[..., Storage]]] = {
    'database': (DatabaseBackend, create_database_storage)
}

def create_storage_from_config(config: StorageBackend) -> Storage:
     config_type, create_backend = _BACKEND_MAP[config.backend]
     return create_backend(**config_type(**config.parameter).dict())
