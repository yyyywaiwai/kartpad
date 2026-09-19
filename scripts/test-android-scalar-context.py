#!/usr/bin/env python3
"""Compare actual old/new scalar adapters; run only when an explicit ADB target is supplied."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-header', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, default=Path('vendor/runtimes/android'))
    parser.add_argument('--output', type=Path, default=Path('build/scalar-context'))
    parser.add_argument('--serial', help='Explicit emulator or authorized physical device; omitted builds only')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    runtime = args.runtime.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    baseline = out / 'baseline-ppc_runtime.h'
    baseline.write_bytes(args.baseline_header.read_bytes())
    # Preparation downloads this pinned compatibility header. Keep test-only
    # dependencies in the output tree, not in the maintained runtime checkout.
    sse_hash = '44b9fa3dec3a52ea473246e04b9f692a4e5b0ed654299eef7fe7ec3049e223e0'
    sse = repo / 'build/dependency-cache' / f'sse2neon-{sse_hash}.h'
    if not sse.is_file() or hashlib.sha256(sse.read_bytes()).hexdigest() != sse_hash:
        parser.error('Prepare the Android runtime first to cache the pinned sse2neon header')
    (out / 'third_party/sse2neon').mkdir(parents=True, exist_ok=True)
    (out / 'include/isa').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sse, out / 'third_party/sse2neon/sse2neon.h')
    sdk = Path(os.environ.get('ANDROID_SDK_ROOT', str(Path.home() / 'Library/Android/sdk')))
    ndk = sdk / 'ndk/29.0.14206865'
    cxx = ndk / 'toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android28-clang++'
    flags = [str(cxx), '-std=c++20', '-O2', '-fno-fast-math', '-ffp-contract=off',
             '-fno-slp-vectorize', '-DKARTPAD_ANDROID_COMBINED_FENV=1',
             '-I' + str(repo / 'runtime/include'), '-I' + str(runtime / 'runtime/include'),
             '-I' + str(out / 'include/isa')]
    # Distinct inline symbols prevent the linker from coalescing old and new adapters.
    names = re.findall(r'inline (?:bool|uint32_t|double) (Ppc\w+)\(', baseline.read_text())
    for variant, header in [('baseline', baseline), ('candidate', runtime / 'runtime/include/ppc_runtime.h')]:
        definitions = [f'-D{name}={variant}_{name}' for name in sorted(set(names))]
        subprocess.run(flags + definitions + [f'-DTEST_ENTRY={variant}',
                       f'-DTEST_RUNTIME_HEADER="{header}"', '-c',
                       str(repo / 'runtime/tests/android_scalar_context_case.cpp'),
                       '-o', str(out / (variant + '.o'))], check=True)
    subprocess.run(flags + ['-static-libstdc++',
                   str(repo / 'runtime/tests/android_scalar_context_differential.cpp'),
                   str(repo / 'runtime/src/android/scalar_fenv.cpp'),
                   str(out / 'baseline.o'), str(out / 'candidate.o'),
                   '-o', str(out / 'differential')], check=True)
    print('Built differential:', out / 'differential', flush=True)
    if args.serial:
        adb = [str(sdk / 'platform-tools/adb'), '-s', args.serial]
        target = '/data/local/tmp/kartpad-scalar-context-differential'
        subprocess.run(adb + ['push', str(out / 'differential'), target], check=True)
        subprocess.run(adb + ['shell', target], check=True)


if __name__ == '__main__':
    main()
