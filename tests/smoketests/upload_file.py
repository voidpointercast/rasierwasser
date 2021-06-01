#!/usr/bin/env python3.9

from argparse import ArgumentParser
from os.path import split
from getpass import getpass
from base64 import b64encode
from OpenSSL.crypto import PKey, load_privatekey, FILETYPE_PEM, sign
from requests import post


def main():
    parser: ArgumentParser = ArgumentParser(description='Upload a certificate file')
    parser.add_argument('package', help='Name of the package.')
    parser.add_argument('file', help='Path to the file to upload.')
    parser.add_argument('key_file', help='Path to private key.')
    parser.add_argument('certificate', help='Name of certificate for signing.')
    parser.add_argument('--digest', default='sha512', help='Digest algorithm to use.')
    parser.add_argument('--port', type=int, default=10010, help='Rasierwasser port.')
    parser.add_argument('--host', default='localhost', help='Rasierwasser host.')

    args = parser.parse_args()

    with open(args.file, 'rb') as src:
        content: bytes = src.read()

    with open(args.key_file, 'rb') as src:
        private_key: PKey = load_privatekey(FILETYPE_PEM, src.read(), getpass('Private key password: ').encode())

    filename: str = split(args.file)[-1]
    signature: str = b64encode(sign(private_key, content, args.digest)).decode('ascii')
    with post(
        f'http://{args.host}:{args.port}/packages',
        json=dict(
            package=args.package,
            filename=filename,
            certificate=args.certificate,
            content_base64=b64encode(content).decode('ascii'),
            signature_base64=signature,
            hash_algorithm=args.digest

        )
    ) as response:
        print(response.status_code, response.text)

if __name__ == '__main__':
    main()