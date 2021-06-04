from unittest import TestCase
from base64 import b64encode
from hashlib import pbkdf2_hmac
from random import choice
from string import printable
from os import urandom
from rasierwasser.configuration.server import AuthConfig
from rasierwasser.server.fastapi.auth import parse_auth_config, AuthPolicy, HTTPBasicCredentials


class HTTPBasicAuthTest(TestCase):

    def setUp(self) -> None:
        self.username: str = ''.join(choice(printable) for _ in range(8))
        self.password: str = ''.join(choice(printable) for _ in range(32))
        self.salt: bytes = urandom(16)
        self.encoded_salt: str = b64encode(self.salt).decode()
        self.password_hash: str = pbkdf2_hmac('sha256', self.password.encode(), self.salt, 100000).hex()

    def build_policy(self) -> AuthPolicy:
        return parse_auth_config(
            AuthConfig(
                policy='http_basic',
                parameter=dict(salt=self.encoded_salt, username=self.username, password_hash=self.password_hash)
            )
        )

    def test_policy_parsing(self):
        policy: AuthPolicy = self.build_policy()
        self.assertTrue(isinstance(policy, AuthPolicy), f'Unexpected type: {type(policy).__name__}')

    def test_wrong_username(self):
        policy: AuthPolicy = self.build_policy()
        self.assertRaises(
            PermissionError,
            lambda: policy.check_credentials(HTTPBasicCredentials(username='FALSE', password=self.password_hash))
        )

    def test_wrong_password(self):
        policy: AuthPolicy = self.build_policy()
        self.assertRaises(
            PermissionError,
            lambda: policy.check_credentials(HTTPBasicCredentials(username=self.username, password='FALSE'))
        )

    def test_valid_credentials(self):
        policy: AuthPolicy = self.build_policy()
        self.assertIsNone(
            policy.check_credentials(HTTPBasicCredentials(username=self.username, password=self.password))
        )
