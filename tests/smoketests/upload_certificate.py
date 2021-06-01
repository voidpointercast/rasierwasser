#!/usr/bin/env python3.9

from argparse import ArgumentParser
from base64 import b64encode
from requests import post


def main():
    parser: ArgumentParser = ArgumentParser(description='Upload a certificate file')
    parser.add_argument('name', help='Name of the certificate.')
    parser.add_argument('file', help='Path to the certificate to upload.')
    parser.add_argument('--port', type=int, default=10010, help='Rasierwasser port.')
    parser.add_argument('--host', default='localhost', help='Rasierwasser host.')

    args = parser.parse_args()
    with open(args.file, 'rb') as src:
        with post(
                f'http://{args.host}:{args.port}/certificates',
                json=dict(name=args.name, public_key_base64=b64encode(src.read()).decode())
        ) as response:
            print(response.status_code, response.text)

if __name__ == '__main__':
    main()