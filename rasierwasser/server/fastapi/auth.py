from typing import TypeVar, Generic, Type, Callable, Dict
from hashlib import pbkdf2_hmac
from base64 import b64decode
from rasierwasser.configuration.server import AuthConfig
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from pydantic import BaseModel
from pydantic.types import SecretStr


SecurityDependant = TypeVar('SecurityDependant')
CredentialType = TypeVar('CredentialType')


class AuthPolicy(BaseModel, Generic[SecurityDependant, CredentialType]):
    credential_type: Type[CredentialType]
    security: SecurityDependant
    check_credentials: Callable[[CredentialType], None]

    class Config:
        arbitrary_types_allowed = True


class BasicHTTPAuthPolicy(AuthPolicy[HTTPBasic, HTTPBasicCredentials]):
    username: str
    salt: SecretStr
    password_hash: SecretStr
    credential_type = HTTPBasicCredentials


class SnakeoilAuthPolicy(AuthPolicy[HTTPBasic, HTTPBasicCredentials]):
    security: HTTPBasic = HTTPBasic()
    check_credentials: Callable[[HTTPBasicCredentials], None] = lambda _: None


def basic_http_auth_policy(
        username: str,
        salt: str,
        password_hash: str,
        hash_algorithm: str = 'sha256',
        iterations: int = 100000
) -> AuthPolicy:

    def check_credentials(credentials: HTTPBasicCredentials) -> None:
        hashed_password: bytes = pbkdf2_hmac(hash_algorithm, credentials.password.encode(), b64decode(salt), iterations)
        if hashed_password.hex() != password_hash or username != credentials.username:
            raise PermissionError('Invalid credentials.')

    return BasicHTTPAuthPolicy(
        username=username,
        salt=salt,
        password_hash=password_hash,
        credential_type=HTTPBasicCredentials,
        security=HTTPBasic(),
        check_credentials=check_credentials
    )


def snakeoil_auth_policy() -> AuthPolicy:
    return SnakeoilAuthPolicy(credential_type=HTTPBasicCredentials)


_AUTH_CONFIG_MAP: Dict[str, Callable[..., AuthPolicy]] = {
    'http_basic': basic_http_auth_policy,
    'snakeoil': snakeoil_auth_policy
}


def parse_auth_config(config: AuthConfig) -> AuthPolicy:
    return _AUTH_CONFIG_MAP[config.policy](**config.parameter)

