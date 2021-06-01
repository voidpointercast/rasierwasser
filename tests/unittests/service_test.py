from unittest import TestCase
from pathlib import Path
from multiprocessing import Process
from requests import get
from rasierwasser.service.server import start_service


class ServiceTest(TestCase):

    def setUp(self) -> None:
        self.data_dir: Path = Path(__file__).parent.joinpath('data', 'service_test')

    def test_service_start(self):
        process: Process = Process(
            target=start_service,
            args=(str(self.data_dir.joinpath('rasierwasser.json')), 'utf-8')
        )
        process.start()
        with get('http://localhost:10010/docs') as response:
            self.assertTrue(response.status_code == 200, f'Could not connect to service: {response.status_code}')
        process.terminate()
        process.join()