from typing import Callable, Iterable, Dict, Optional
from datetime import datetime
from hashlib import sha512
from base64 import b64decode, b64encode
from pydantic import BaseModel, Field

PackageName: type = str
FileName: type = str


class CertificateData(BaseModel):
    """
    >>> CertificateData(name='test', public_key=b'A')
    CertificateData(name='test', public_key=b'A')
    """
    name: str
    public_key: bytes
    upload_time: datetime = Field(default_factory=datetime.now)
    disabled: Optional[datetime] = Field(default=None)
    compromised: Optional[datetime] = Field(default=None)

    @property
    def canonic(self) -> Dict[str, str]:
        return dict(
            name=self.name,
            sha512=sha512(self.public_key).hexdigest(),
            public_key_base64=b64encode(self.public_key),
            upload_time=self.upload_time.isoformat(),
            disabled=self.disabled.isoformat() if self.disabled else self.disabled,
            compromised=self.compromised.isoformat() if self.compromised else self.compromised
        )

    @classmethod
    def from_base64(cls, name: str, public_key: str) -> 'CertificateData':
        return CertificateData(name=name, public_key=b64decode(public_key))


class PackageData(BaseModel):
    package_name: PackageName
    file_name: FileName
    file_content: bytes
    signature: bytes
    certificate: str
    digest: str = 'sha512'
    upload_time: datetime = Field(default_factory=datetime.now)

    def canonical(self) -> Dict[str, str]:
        print(self)
        return dict(
            package=self.package_name,
            filename=self.file_name,
            content_sha512=sha512(self.file_content).hexdigest(),
            content_base64=b64encode(self.file_content).decode(errors='replace'),
            signature_base64=b64encode(self.signature).decode(errors='replace'),
            signature_sha512=sha512(self.signature).hexdigest(),
            certificate=self.certificate,
            digest=self.digest,
            upload_time=self.upload_time.isoformat()
        )

    @classmethod
    def from_base64(
            cls,
            package_name: PackageName,
            file_name: FileName,
            file_content_base64: str,
            signature_base64: str,
            certificate: str,
            digest: str
    ) -> 'PackageData':
        return PackageData(
            package_name=package_name, file_name=file_name, file_content=b64decode(file_content_base64),
            signature=b64decode(signature_base64), certificate=certificate, digest=digest
        )


class PackageActivity(BaseModel):
    package: PackageName
    file: FileName
    upload_time: datetime
    certificate: str

    @classmethod
    def from_package_data(cls, package: PackageData) -> 'PackageActivity':
        return PackageActivity(
            package=package.package_name, file=package.file_name,
            upload_time=package.upload_time, certificate=package.certificate
        )


StorePackage = Callable[[PackageData], None]
RetrievePackage = Callable[[PackageName, FileName], PackageData]
GetPackageIndex = Callable[[PackageName], Iterable[PackageData]]
GetPackages = Callable[[], Iterable[str]]
GetPackageActivities = Callable[[datetime, datetime], Iterable[PackageActivity]]
GetCertificates = Callable[[], Iterable[CertificateData]]
StoreCertificate = Callable[[CertificateData], None]


class Storage(BaseModel):
    store: StorePackage
    retrieve: RetrievePackage
    index: GetPackageIndex
    packages: GetPackages
    add_certificate: StoreCertificate
    certificates: GetCertificates
    package_activities: GetPackageActivities
    hash_algorithm: str = 'sha512'
    verify: bool = True
