#!/usr/bin/env python3
"""Read public identity fields from a raw Wii ISO or extracted sys/boot.bin."""
import argparse
import json
from pathlib import Path


def inspect_header(header: bytes) -> dict:
    if header[:4] in (b'WBFS', b'RVZ\x01', b'WIA\x01'):
        raise ValueError('Compressed/container images are not supported. Use a raw ISO or extracted sys/boot.bin.')
    if len(header) < 28 or header[24:28] != bytes.fromhex('5d1c9ea3'):
        raise ValueError('No raw Wii disc header found. Use a raw ISO or extracted sys/boot.bin.')
    identity = header[:6]
    if not all(48 <= value <= 57 or 65 <= value <= 90 for value in identity):
        raise ValueError('The disc ID contains invalid characters.')
    return {'disc_id': identity.decode('ascii'), 'disc_number': header[6],
            'revision': header[7]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path, help='local raw ISO or sys/boot.bin; never uploaded')
    args = parser.parse_args()
    try:
        with args.image.open('rb') as stream:
            result = inspect_header(stream.read(28))
    except OSError:
        parser.exit(1, 'Cannot read the local file. Check the path and read permission.\n')
    except ValueError as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
