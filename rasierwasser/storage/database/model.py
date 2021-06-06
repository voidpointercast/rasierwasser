from sqlalchemy import Column, BLOB, TEXT, ForeignKey, DATETIME
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from rasierwasser.storage.algebra import PackageData, CertificateData

Base = declarative_base()


class Certificate(Base):
    __tablename__ = 'certificates'

    name = Column(TEXT, primary_key=True)
    public_key = Column(BLOB)
    upload_time = Column(DATETIME, default=datetime.utcnow)
    disabled = Column(DATETIME, default=None, nullable=True)
    compromised = Column(DATETIME, default=None, nullable=True)

    def as_certificate_data(self) -> CertificateData:
        return CertificateData(
            name=self.name,
            public_key=self.public_key,
            upload_time=self.upload_time,
            disabled=self.disabled,
            compromised=self.compromised
        )


class PackageFile(Base):
    __tablename__ = 'packages'

    package = Column(TEXT, primary_key=True)
    file = Column(TEXT, primary_key=True)
    content = Column(BLOB)
    signature = Column(BLOB)
    certificate = Column(TEXT, ForeignKey('certificates.name'))
    digest = Column(TEXT)
    upload_time = Column(DATETIME, default=datetime.utcnow)

    def as_package_data(self) -> PackageData:
        return PackageData(
            package_name=self.package,
            file_name=self.file,
            file_content=self.content,
            signature=self.signature,
            certificate=self.certificate,
            upload_time=self.upload_time
        )


