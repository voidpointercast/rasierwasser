from hashlib import sha1
from OpenSSL.crypto import verify, load_certificate, FILETYPE_PEM, X509, Error
from rasierwasser.storage.algebra import CertificateData, PackageData


def verify_package_data(package: PackageData, certificate: CertificateData) -> None:
    cert: X509 = load_certificate(FILETYPE_PEM, certificate.public_key)
    try:
        verify(cert, package.signature, package.file_content, package.digest)
    except Error:
        sig_fingerprint: str = sha1(package.signature).hexdigest()
        raise ValueError(
            f'Got invalid signature for {package.package_name}/{package.file_name}: {sig_fingerprint} (SHA1)'
        )
