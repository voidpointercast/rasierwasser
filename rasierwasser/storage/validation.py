from typing import Union
from hashlib import sha1
from io import BytesIO
from OpenSSL.crypto import verify, load_certificate, FILETYPE_PEM, X509, Error
from zipfile import ZipFile
from rasierwasser.storage.algebra import CertificateData, PackageData


def get_normalised_package_content(package: Union[PackageData, bytes]) -> bytes:
    with ZipFile(BytesIO(package.file_content if isinstance(package, PackageData) else package)) as zipfile:
        return b''.join(
            zipfile.read(file)
            for file in sorted(zipfile.namelist())
        )


def verify_package_data(package: PackageData, certificate: CertificateData) -> None:
    cert: X509 = load_certificate(FILETYPE_PEM, certificate.public_key)
    try:
        verify(cert, package.signature, get_normalised_package_content(package), package.digest)
    except Error:
        sig_fingerprint: str = sha1(package.signature).hexdigest()
        raise ValueError(
            f'Got invalid signature for {package.package_name}/{package.file_name}: {sig_fingerprint} (SHA1)'
        )
