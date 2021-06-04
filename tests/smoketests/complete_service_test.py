from os import unlink
from pathlib import Path
from multiprocessing import Process
from rasierwasser.service.server import start_service


def service_test():
    start_service(str(Path(__file__).parent.joinpath('rasierwasser.json')), 'utf-8')


if __name__ == '__main__':
    process: Process = Process(target=service_test)
    process.start()
    input('Hint any key to continue and end server.')
    process.terminate()
    process.join()

