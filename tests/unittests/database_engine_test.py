from typing import List
from pathlib import Path
from unittest import TestCase
from tempfile import TemporaryDirectory
from os.path import join, exists
from OpenSSL.crypto import load_privatekey, FILETYPE_PEM, PKey, sign
from rasierwasser.storage.algebra import CertificateData, PackageData
from rasierwasser.storage.validation import verify_package_data
from rasierwasser.storage.database.engine import create_database_storage, Storage


class DatabaseEngineTest(TestCase):

    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.db_name = 'sample.sqlite'
        self.data_dir: Path = Path(__file__).parent.joinpath('data', 'database_engine_test')

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_create_database_storage(self):
        create_database_storage(f'sqlite:////{self.tempdir.name}/{self.db_name}')
        self.assertTrue(exists(join(self.tempdir.name, self.db_name)), 'No database file was found.')

    def test_certificate_handling(self):
        storage: Storage = create_database_storage(f'sqlite:////{self.tempdir.name}/{self.db_name}', verify=False)
        certificate: CertificateData = CertificateData(name='A', public_key=b'A')
        storage.add_certificate(certificate)
        certificates: List[CertificateData] = list(storage.certificates())
        self.assertTrue(len(certificates) == 1, f'Expected one certificate but got: {certificates}')
        self.assertTrue(certificates.pop() == certificate, 'Certificate has been changed during store/load cycle.')

    def test_file_handling(self):
        storage: Storage = create_database_storage(f'sqlite:////{self.tempdir.name}/{self.db_name}', verify=False)
        certificate: CertificateData = CertificateData(name='A', public_key=b'A')
        package: PackageData = PackageData(
            package_name='Alib', file_name='alib-0.0.1.whl', file_content=b'alib', signature='SIG', certificate='A'
        )
        storage.add_certificate(certificate)
        storage.store(package)
        self.assertTrue(list(storage.packages()) == ['Alib'], 'Created package does not appear in package list')
        self.assertTrue(
            storage.retrieve('Alib', 'alib-0.0.1.whl') == package,
            f'Package has been changed during store/load cycle. Original: {package}, got: {package}'
        )

    def test_signature_verification(self):
        with self.data_dir.joinpath('sample_file.txt').open('rb') as src:
            content: bytes = src.read()
        with self.data_dir.joinpath('cert.pem').open('rb') as src:
            cert_data: bytes = src.read()
        with self.data_dir.joinpath('key.pem').open('rb') as src:
            key: bytes = src.read()

        private_key: PKey = load_privatekey(FILETYPE_PEM, key, b'TEST')
        signature = sign(private_key, content, 'sha512')

        certificate: CertificateData = CertificateData(name='base', public_key=cert_data)
        package: PackageData = PackageData(
            package_name='sample', file_name='sample_file.txt', file_content=content, signature=signature,
            certificate='base'
        )
        verify_package_data(package, certificate)

    def test_encryption_and_verification(self):
        storage: Storage = create_database_storage(f'sqlite:////{self.tempdir.name}/{self.db_name}')
        with self.data_dir.joinpath('cert.pem').open('rb') as src:
            certificate: CertificateData = CertificateData(name='base', public_key=src.read())
        with self.data_dir.joinpath('key.pem').open('rb') as src:
            private_key: PKey = load_privatekey(FILETYPE_PEM, src.read(), b'TEST')
        package: PackageData = PackageData(
            package_name='sample',
            file_name='sample.txt',
            file_content=b'Hello World',
            certificate='base',
            signature=sign(private_key, b'Hello World', 'sha512')
        )
        storage.add_certificate(certificate)
        storage.store(package)

