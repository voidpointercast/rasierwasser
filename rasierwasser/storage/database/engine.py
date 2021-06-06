from typing import Optional, Iterable, Dict, Any
from datetime import datetime
from functools import partial
from sqlalchemy import create_engine, and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from rasierwasser.storage.algebra import Storage, PackageData, FileName, PackageName, CertificateData, PackageActivity
from rasierwasser.storage.database.model import Certificate, PackageFile, Base
from rasierwasser.storage.validation import verify_package_data


class SessionGuard:
    def __init__(self, create_session: sessionmaker) -> None:
        self._session: Session = create_session()

    def __enter__(self) -> Session:
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._session.rollback()
        self._session.close()


def index(create_session: sessionmaker, package: PackageName) -> Iterable[PackageData]:
    with SessionGuard(create_session) as session:
        return tuple(
            map(
                PackageFile.as_package_data,
                session.query(PackageFile).filter(PackageFile.package == package)
            )
        )


def retrieve(create_session: sessionmaker, package: PackageName, file: FileName) -> PackageData:
    with SessionGuard(create_session) as session:
        try:
            data: PackageFile = session.query(
                PackageFile
            ).filter(PackageFile.package == package).filter(PackageFile.file == file).one()
        except NoResultFound:
            raise FileNotFoundError(f'{package}/{file}')
        else:
            return data.as_package_data()


def get_certificate(create_session: sessionmaker, name: str) -> CertificateData:
    with SessionGuard(create_session) as session:
        try:
            certificate: Certificate = session.query(Certificate).filter(Certificate.name == name).one()
            return certificate.as_certificate_data()
        except NoResultFound:
            raise FileNotFoundError(f'Found no certificate with name: {certificate}')


def store(create_session: sessionmaker, verify: bool, package: PackageData) -> None:
    if verify:
        verify_package_data(package, get_certificate(create_session, package.certificate))

    with SessionGuard(create_session) as session:
        data: PackageFile = PackageFile(
            package=package.package_name, file=package.file_name, content=package.file_content,
            signature=package.signature, certificate=package.certificate
        )
        session.add(data)
        session.commit()


def packages(create_session: sessionmaker) -> Iterable[str]:
    with SessionGuard(create_session) as session:
        return set(
            result.package
            for result in session.query(PackageFile)
        )


def certificates(create_session: sessionmaker) -> Iterable[CertificateData]:
    with SessionGuard(create_session) as session:
        return tuple(
            map(Certificate.as_certificate_data, session.query(Certificate))
        )


def add_certificate(create_session: sessionmaker, certificate: CertificateData) -> None:
    with SessionGuard(create_session) as session:
        session.add(Certificate(name=certificate.name, public_key=certificate.public_key))
        session.commit()


def get_package_activities(create_session: sessionmaker, begin: datetime, end: datetime) -> Iterable[PackageActivity]:
    with SessionGuard(create_session) as session:
        return sorted(
            map(
                lambda r: PackageActivity.from_package_data(PackageFile.as_package_data(r)),
                session.query(PackageFile).filter(and_(PackageFile.upload_time >= begin, PackageFile.upload_time < end))
            ),
            key=lambda a: a.upload_time,
            reverse=True
        )


def create_database_storage(db_url: str, verify: bool = True, options: Optional[Dict[str, Any]] = None) -> Storage:
    """
    Args:
        db_url:
        verify:
        **options:

    Returns:
    >>> create_database_storage('sqlite:///test.sqlite')
    """
    engine: Engine = create_engine(db_url, **(options if options else dict()))
    Base.metadata.create_all(engine, checkfirst=True)
    create_session: sessionmaker = sessionmaker(engine)

    return Storage(
        store=partial(store, create_session, verify),
        retrieve=partial(retrieve, create_session),
        index=partial(index, create_session),
        packages=partial(packages, create_session),
        add_certificate=partial(add_certificate, create_session),
        certificates=partial(certificates, create_session),
        verify=verify,
        package_activities=partial(get_package_activities, create_session)
    )

