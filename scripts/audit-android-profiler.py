#!/usr/bin/env python3
"""Offline, read-only preflight for a private, release-mode CPU profiler APK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile


def run(*args):
    return subprocess.check_output([str(arg) for arg in args], text=True)


def sha256(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check_manifest(badging, tree, expected_code):
    match = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
    if not match or match[1] != 'dev.kartpad.android' or int(match[2]) != expected_code:
        raise ValueError('Wrong package or unexpected version code')
    if 'application-debuggable' in badging:
        raise ValueError('Profiler must be non-debuggable; use a release bundle, not assembleDebug')
    # Only accept the shell attribute belonging to the profileable element.
    profileable = re.search(r'E: profileable[^\n]*\n((?:(?!\s*E:)[^\n]*\n)*)', tree + '\n')
    if not profileable or not re.search(r'android:shell\([^)]*\)=true\s*$', profileable[1], re.M):
        raise ValueError('APK does not enable shell profileability')
    return {'package': match[1], 'version_code': int(match[2]), 'version_name': match[3]}


def allocated_sections(path, readelf, require_symbols=False):
    elf = json.loads(run(readelf, '--elf-output-style=JSON', '-S', path))[0]
    if elf['FileSummary']['Format'] != 'elf64-littleaarch64':
        raise ValueError('Expected an ARM64 ELF library')
    sections = [item['Section'] for item in elf['Sections']]
    if require_symbols and not any(s['Name']['Name'] == '.symtab' for s in sections):
        raise ValueError('Native symbol file is stripped')
    result = {}
    with open(path, 'rb') as stream:
        for section in sections:
            if not section['Flags']['Value'] & 2:  # SHF_ALLOC
                continue
            name = section['Name']['Name']
            if name in result:
                raise ValueError('Duplicate allocated section name')
            stream.seek(section['Offset'])
            digest = None
            if section['Type']['Name'] != 'SHT_NOBITS':
                data = stream.read(section['Size'])
                if len(data) != section['Size']:
                    raise ValueError('Truncated ELF section')
                digest = hashlib.sha256(data).hexdigest()
            result[name] = [section['Address'], section['Size'], section['Flags']['Value'], digest]
    if '.text' not in result or '.note.gnu.build-id' not in result:
        raise ValueError('Missing native code or build identity')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path)
    parser.add_argument('symbols', type=Path, help='Exact unstripped libmain.so (kept private)')
    parser.add_argument('--version-code', type=int, required=True)
    parser.add_argument('--signer-sha256', required=True, help='Expected recipient-compatible certificate digest')
    parser.add_argument('--sdk', type=Path, default=Path(os.environ.get('ANDROID_SDK_ROOT', os.environ.get('ANDROID_HOME', str(Path.home() / 'Library/Android/sdk')))))
    args = parser.parse_args()
    versions = (Path(__file__).with_name('android-toolchain-versions.sh')).read_text()
    version = lambda key: re.search(r'^' + key + r'="([^"]+)"', versions, re.M)[1]
    build_tools = args.sdk / 'build-tools' / version('KARTPAD_ANDROID_BUILD_TOOLS')
    readelf = args.sdk / 'ndk' / version('KARTPAD_ANDROID_NDK') / 'toolchains/llvm/prebuilt/darwin-x86_64/bin/llvm-readelf'
    expected_signer = args.signer_sha256.lower().replace(':', '')
    if not re.fullmatch('[0-9a-f]{64}', expected_signer):
        raise ValueError('Expected signer must be a SHA-256 certificate digest')
    receipt = check_manifest(run(build_tools / 'aapt2', 'dump', 'badging', args.apk),
                             run(build_tools / 'aapt2', 'dump', 'xmltree', '--file', 'AndroidManifest.xml', args.apk), args.version_code)
    signing = run(build_tools / 'apksigner', 'verify', '--print-certs', args.apk)
    signers = re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)$', signing, re.M)
    if [s.lower() for s in signers] != [expected_signer]:
        raise ValueError('APK signer differs from the expected recipient-compatible signer')
    with tempfile.TemporaryDirectory(prefix='kartpad-profiler-audit-') as temporary:
        with zipfile.ZipFile(args.apk) as package:
            native = Path(package.extract('lib/arm64-v8a/libmain.so', temporary))
        packaged = allocated_sections(native, readelf)
        symbols = allocated_sections(args.symbols, readelf, require_symbols=True)
        if packaged != symbols:
            raise ValueError('Native symbols do not match every allocated APK library section')
        receipt.update(native_sha256=sha256(native), allocated_sections=packaged)
    receipt.update(apk_sha256=sha256(args.apk), symbols_sha256=sha256(args.symbols),
                   signer_sha256=expected_signer, debuggable=False, shell_profileable=True,
                   scope='Offline artifact checks only; installed identity and gameplay not checked')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
