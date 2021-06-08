from typing import List, Optional
from datetime import datetime
from jinja2 import Template
from pkg_resources import resource_string
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import Response, HTMLResponse
from rasierwasser.storage.algebra import PackageData, CertificateData, Storage, PackageName, FileName
from rasierwasser.configuration.server import AuthConfig, DEFAULT_AUTH_CONFIG
from rasierwasser.server.fastapi.auth import parse_auth_config, AuthPolicy


class CertificateUpload(BaseModel):
    name: str
    public_key_base64: str


class FileUpload(BaseModel):
    package: str
    filename: str
    content_base64: str
    certificate: str
    signature_base64: str
    hash_algorithm: str = 'sha512'


def create_fastapi_server(
        storage: Storage,
        debug: bool = False,
        auth_config: AuthConfig = DEFAULT_AUTH_CONFIG
) -> FastAPI:

    app: FastAPI = FastAPI(debug=debug)
    auth: AuthPolicy = parse_auth_config(auth_config)

    @app.get('/packages')
    def base_index() -> HTMLResponse:
        index: Template = Template(resource_string('rasierwasser', 'server/data/base_index.html').decode('utf-8'))
        packages: List[str] = sorted(storage.packages())
        return HTMLResponse(index.render(packages=packages))

    @app.get('/packages/{package}')
    def package_index(package: str) -> HTMLResponse:
        index: Template = Template(resource_string('rasierwasser', 'server/data/package_index.html').decode('utf-8'))
        files: List[str] = sorted(file.file_name for file in storage.index(package))
        return HTMLResponse(index.render(files=files, package=package))

    @app.get('/packages/{package}/{file}')
    def download_file(package: PackageName, file: FileName) -> Response:
        return Response(storage.retrieve(package, file).file_content, media_type='application/octet-stream')

    @app.get('/metadata')
    async def base_index_metadata():
        return sorted(storage.packages())

    @app.get('/metadata/{package}')
    async def index(package: PackageName):
        return list(map(PackageData.canonical, storage.index(package)))

    @app.post('/packages', status_code=201)
    async def upload_file(upload: FileUpload):
        try:
            storage.store(
                PackageData.from_base64(
                    upload.package, upload.filename, upload.content_base64, upload.signature_base64,
                    upload.certificate, upload.hash_algorithm
                )
            )
        except PermissionError:
            raise HTTPException(403)

    @app.get('/activities/packages')
    async def activities(begin: Optional[datetime] = None, end: Optional[datetime] = None):
        begin = begin if begin else datetime.min
        end = end if end else datetime.max
        return storage.package_activities(begin, end)

    @app.get('/activities/certificates')
    async def certificate_activities(begin: Optional[datetime] = None, end: Optional[datetime] = None):
        begin = begin if begin else datetime.min
        end = end if end else datetime.max
        return sorted(
            (
                dict(**certificate.canonic, last_activity=last_activity)
                for certificate in storage.certificates()
                if begin <= (
                    last_activity := max(
                        filter(None, (certificate.upload_time, certificate.disabled, certificate.compromised))
                    )
                ) < end
            ),
            key=lambda c: c['last_activity'],
            reverse=True
        )


    @app.get('/certificates')
    async def get_certificates():
        return dict(
            (certificate.name, certificate.canonic)
            for certificate in storage.certificates()
        )

    @app.post('/certificates', status_code=201)
    async def upload_certificate(
            certificate: CertificateUpload,
            credentials: auth.credential_type = Depends(auth.security)
    ):
        try:
            auth.check_credentials(credentials)
        except PermissionError:
            raise HTTPException(403)
        storage.add_certificate(CertificateData.from_base64(certificate.name, certificate.public_key_base64))

    return app



