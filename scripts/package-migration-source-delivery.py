#!/usr/bin/env python3
"""Compose reviewed dependency sources with an exact migrated core snapshot."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--version', default='0.4.24')
p.add_argument('--ipa', type=Path, required=True)
p.add_argument('--release-tools', type=Path, required=True)
p.add_argument('--prior', type=Path, required=True)
p.add_argument('--core', type=Path, required=True)
p.add_argument('--core-manifest', type=Path, required=True)
p.add_argument('--runtime', type=Path, required=True)
p.add_argument('--apk', type=Path, required=True)
p.add_argument('--build-manifest', type=Path, required=True)
p.add_argument('output', type=Path)
a = p.parse_args()
sha = lambda data: hashlib.sha256(data).hexdigest()
if a.output.exists():
    p.error('output already exists')
files = {}
with tarfile.open(a.prior) as archive:
    old = json.load(archive.extractfile('SOURCE-MANIFEST.json'))
    names = archive.getnames()
    if len(names) != len(set(names)) or set(names) != set(old['files']) | {'SOURCE-MANIFEST.json'}:
        p.error('prior source manifest coverage mismatch')
    for member in archive.getmembers():
        if not member.isfile() or member.name.startswith('/') or '..' in Path(member.name).parts:
            p.error('unsafe prior source member')
        if member.name == 'SOURCE-MANIFEST.json':
            continue
        data = archive.extractfile(member).read()
        expected = old['files'][member.name]
        if len(data) != expected['bytes'] or sha(data) != expected['sha256']:
            p.error('prior source member failed integrity check')
        if member.name.startswith(('prepared-runtime/android/', 'supplement/')) or member.name.endswith('-release-tools.tar.gz'):
            continue
        if member.name.endswith('-core-source.tar.gz') or member.name == 'core-source-manifest.json':
            files['retained-base/' + member.name] = data
            continue
        files[member.name] = data
core = a.core.read_bytes()
core_manifest = json.loads(a.core_manifest.read_text())
if sha(core) != core_manifest['sha256'] or len(core) != core_manifest['bytes']:
    p.error('core snapshot does not match its manifest')
files[f'KartPad-{a.version}-core-source.tar.gz'] = core
files[f'KartPad-{a.version}-release-tools.tar.gz'] = a.release_tools.read_bytes()
files['core-source-manifest.json'] = a.core_manifest.read_bytes()
for path in a.runtime.rglob('*'):
    if path.is_symlink():
        p.error('runtime contains a symlink')
    if path.is_file():
        files['prepared-runtime/android/' + path.relative_to(a.runtime).as_posix()] = path.read_bytes()
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('provenance', Path(__file__).with_name('write-build-provenance.py'))
mod = module_from_spec(spec); spec.loader.exec_module(mod)
build = json.loads(a.build_manifest.read_text())
if build['source_dirty'] or mod.tree(a.runtime) != build['prepared_runtime']:
    p.error('prepared runtime is not the clean compiled input')
if core_manifest['archives'][0]['commit'] != build['source_revision']:
    p.error('core snapshot does not identify the compiled Android source')
files['REBUILD.md'] = Path(__file__).resolve().parents[1].joinpath('docs/releases/v0.4.24-source.md').read_bytes()
files['supplement/package-migration-source-delivery.py'] = Path(__file__).read_bytes()
files['supplement/write-build-provenance.py'] = Path(__file__).with_name('write-build-provenance.py').read_bytes()
manifest = {'schemaVersion': 1, 'applicationSources': {'android': build['source_revision'], 'iosBase': old['applicationSources']['iosBase']},
            'androidAPK_SHA256': sha(a.apk.read_bytes()), 'iosIPA_SHA256': sha(a.ipa.read_bytes()), 'preparedRuntime': {'android': build['prepared_runtime'], 'ios': old['preparedRuntime']['ios']},
            'files': {n: {'bytes': len(d), 'sha256': sha(d)} for n,d in sorted(files.items())}}
files['SOURCE-MANIFEST.json'] = (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode()
with a.output.open('xb') as output, gzip.GzipFile(filename='', fileobj=output, mode='wb', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w|') as archive:
    for name,data in sorted(files.items()):
        info=tarfile.TarInfo(name); info.size=len(data); info.mode=0o644; archive.addfile(info,io.BytesIO(data))
print(json.dumps({'bytes': a.output.stat().st_size, 'sha256': sha(a.output.read_bytes())}))
