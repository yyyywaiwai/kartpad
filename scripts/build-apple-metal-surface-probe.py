#!/usr/bin/env python3
"""Build the native recovery probe against an existing prepared Aurora and SDL.

Run the macOS executable directly. Install/launch simulator apps with simctl;
this builder does not operate devices or sign physical-device apps.
"""
import argparse
from pathlib import Path
import plistlib
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('aurora', 'sdl-include', 'sdl-library', 'dawn-include', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--dawn-library', type=Path,
                        help='Link Dawn and exercise real WebGPU surface recreation')
    parser.add_argument('--sdk', choices=('macosx', 'iphonesimulator', 'appletvsimulator',
                                         'iphoneos', 'appletvos'), required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sdk = subprocess.check_output(['xcrun', '--sdk', args.sdk, '--show-sdk-path'], text=True).strip()
    targets = {'macosx': 'arm64-apple-macos14.0', 'iphonesimulator': 'arm64-apple-ios16.0-simulator',
               'iphoneos': 'arm64-apple-ios16.0', 'appletvos': 'arm64-apple-tvos17.0',
               'appletvsimulator': 'arm64-apple-tvos17.0-simulator'}
    desktop = args.sdk == 'macosx'
    args.output.mkdir(parents=True, exist_ok=True)
    if desktop:
        binary = args.output / 'MetalProbe'
    else:
        app = args.output / 'MetalProbe.app'
        app.mkdir(exist_ok=True)
        binary = app / 'MetalProbe'
        with (app / 'Info.plist').open('wb') as f:
            plistlib.dump(dict(CFBundleIdentifier=('dev.kartpad.webgpu-recovery-probe' if args.dawn_library
                                                 else 'dev.kartpad.metal-recovery-probe'),
                              CFBundleName='Metal Recovery Probe', CFBundleExecutable='MetalProbe',
                              CFBundleVersion='1', CFBundleShortVersionString='1.0',
                              CFBundlePackageType='APPL', MinimumOSVersion='17.0' if 'tvos' in args.sdk else '16.0',
                              UIDeviceFamily=[3] if 'tvos' in args.sdk else [1, 2],
                              UIApplicationSupportsIndirectInputEvents=True, UILaunchScreen={},
                              UISupportedInterfaceOrientations=['UIInterfaceOrientationLandscapeLeft',
                                                               'UIInterfaceOrientationLandscapeRight']), f)
    frameworks = ('CoreVideo CoreAudio AudioToolbox GameController CoreHaptics Metal QuartzCore '
                  'UniformTypeIdentifiers AVFoundation Foundation CoreMedia').split()
    frameworks += ('Cocoa IOKit Carbon ForceFeedback' if desktop else
                   'UIKit OpenGLES CoreGraphics CoreBluetooth').split()
    if args.sdk.startswith('iphone'):
        frameworks.append('CoreMotion')
    cmd = ['xcrun', '--sdk', args.sdk, 'clang++', '-std=c++20', '-fobjc-arc',
           '-target', targets[args.sdk], '-isysroot', sdk,
           '-I' + str(args.sdl_include), '-I' + str(args.dawn_include),
           '-I' + str(args.aurora / 'lib/dawn'),
           str(root / ('tests/native/apple_webgpu_surface_probe.mm' if args.dawn_library
                       else 'tests/native/apple_metal_surface_probe.mm')),
           str(args.aurora / 'lib/dawn/MetalBinding.mm'), str(args.sdl_library),
           '-liconv', '-o', str(binary)]
    if args.dawn_library:
        cmd += [str(args.dawn_library)]
        frameworks += ['IOSurface', 'Security']
    for framework in frameworks:
        cmd += ['-framework', framework]
    subprocess.run(cmd, check=True)
    if 'simulator' in args.sdk:
        subprocess.run(['codesign', '--force', '--sign', '-', '--timestamp=none', str(app)], check=True)
    print(binary if desktop else app)


if __name__ == '__main__':
    main()
