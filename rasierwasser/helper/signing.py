#!/usr/bin/env python3.9

from typing import Dict, Any, Iterable, Pattern, Tuple, cast
from itertools import chain
from argparse import ArgumentParser
from re import compile as compile_regex
from yaml import safe_load
from json import dump
from pathlib import Path
from os import scandir, DirEntry
from getpass import getpass
from base64 import b64encode
from OpenSSL.crypto import PKey, load_privatekey, FILETYPE_PEM, sign


CONFIG_FILE_NAME: str = 'rasierwasser_config.yaml'
PACKAGE_PATTERN: Pattern = compile_regex(r'.*-(?P<major>\d+)\.(?P<minor>\d+)\.(?P<build>\d+)')


def decent_until_config_found(current: Path) -> Dict[str, Any]:
    target: Path = current.joinpath(CONFIG_FILE_NAME)
    if target.exists():
        with target.open('r', encoding='utf-8') as src:
            return dict(
                **safe_load(src),
                config_file=target.absolute().as_uri(),
                package_dir=str(target.parent.absolute())
            )
    next_decent: Path = current.parent
    if next_decent == current:
        raise FileNotFoundError(f'Could not find configuration file {CONFIG_FILE_NAME} in directory structure.')


def find_latest_package(package: Path) -> str:
    wheels: Iterable[DirEntry] = filter(lambda entry: entry.name.endswith('.whl'), scandir(package.joinpath('dist')))
    versions: Iterable[Tuple[int, int, int, Path]] = (
        cast(
            Tuple[int, int, int, Path],
            tuple(chain(map(int, PACKAGE_PATTERN.match(wheel.name).groups()), (wheel.path, )))
        )
        for wheel in wheels
    )
    return max(versions)[-1]


def main():
    parser: ArgumentParser = ArgumentParser(description='Sign and newest release for a python package')
    parser.add_argument('--package-dir', default='.', help='Path to python project.')
    parser.add_argument('--keyfile-override', default=None, help='Overrides keyfile in configuration file.')
    parser.add_argument('--password', default=None, help='Password for keyfile.')
    parser.add_argument('--out-dir', default=None, help='Alternative output dir for signature result.')

    args = parser.parse_args()
    config: Dict[str, Any] = decent_until_config_found(Path(args.package_dir))
    if args.keyfile_override:
        config['keyfile'] = args.keyfile_override

    digest: str = config.get('digest', 'sha512')
    target_wheel: str = find_latest_package(Path(config['package_dir']))
    with open(target_wheel, 'rb') as src:
        content: bytes = src.read()

    with open(config['keyfile'], 'rb') as src:
        private_key: PKey = load_privatekey(
            FILETYPE_PEM, src.read(),
            (args.password if args.password else getpass('Private key password: ')).encode()
        )

    package: str = Path(target_wheel).name.rsplit('-', 4)[0]
    signature: str = b64encode(sign(private_key, content, digest)).decode('ascii')
    output_path: Path = Path(args.out_dir) if args.out_dir else Path(config['package_dir'])
    with output_path.joinpath('rasierwasser_signature.json').open('w', encoding='utf-8') as out:
        dump(
            dict(
                package=package,
                filename=Path(target_wheel).name,
                signature_base64=signature,
                certificate=config['certificate'],
                hash_algorithm=digest,
                content_base64=b64encode(content).decode('ascii')
            ),
            out,
            ensure_ascii=False,
            indent=3
        )

if __name__ == '__main__':
    main()