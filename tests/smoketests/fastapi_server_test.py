from tempfile import TemporaryDirectory
from base64 import b64encode
from argparse import ArgumentParser
from os.path import join
from multiprocessing import Process
from requests import post, Response
from uvicorn import run
from rasierwasser.storage.database.engine import create_database_storage, Storage
from rasierwasser.server.fastapi import create_fastapi_server, FastAPI


def main():
    parser: ArgumentParser = ArgumentParser(description='Rasierwasser FastAPI smoketest.')
    parser.add_argument('--port', type=int, help='Port to run Rasierwasser server on.', default=10010)
    args = parser.parse_args()
    with TemporaryDirectory() as tempdir:
        db_path: str = join(tempdir, 'rasierwassser.sqlite')
        print(f"Path to database is {db_path}")
        storage: Storage = create_database_storage(f'sqlite:////{db_path}')
        server: FastAPI = create_fastapi_server(storage, True)
        run(server, host='localhost', port=args.port)


if __name__ == '__main__':
    main()