#!/usr/bin/env bash
# Build a separate Japanese development app without changing the PAL product.
set -euo pipefail
repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"
translation="${1:-$repo/private/rmcj01/verified/translation}"
data="${2:-$repo/data}"
product="${3:-base}"
case "$product" in base|retro-rewind|dual) ;; *) echo "Invalid product" >&2; exit 64 ;; esac
tag="${KARTPAD_RMCJ_BUILD_TAG:-ios-development}"
[[ "$tag" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid build tag" >&2; exit 64; }
work="$repo/private/rmcj01/$tag"
# A dedicated parent also isolates upstream's ../generated link from macOS
# builds running at the same time.
runtime="$repo/build/rmcj01-$tag/runtime"
build="$repo/build/rmcj01-$tag/xcode"
for output in "$work" "$runtime" "$build"; do
  [[ ! -e "$output" ]] || { echo "Output exists; choose a fresh build tag: $output" >&2; exit 73; }
done
export PYTHONPATH="$repo/builder${PYTHONPATH:+:$PYTHONPATH}"
export PATH="$repo/build/toolchains/python/bin:$PATH"
mkdir -p "$work"
KARTPAD_PREPARE_ONLY=1 "$repo/scripts/prepare-ios-game-runtime.sh" \
  "$translation" "$runtime" "$build" "$product" > "$work/runtime-prepare.log" 2>&1
python3 -m kartpad_builder.rmcj01 --data "$data" --output "$work" --runtime "$runtime"
python3 - "$work/host" "$runtime" "$translation" <<'PY'
import json, plistlib, sys
from pathlib import Path
host, runtime, translation = map(Path, sys.argv[1:])
# Only consume a Japanese graph emitted by the region preparation workflow.
report = json.loads((translation.parent / 'preparation.json').read_text())
if report['region'] != 'J':
    raise SystemExit('Expected a prepared Japanese translation graph')
config = (translation / 'RuntimeConfig.h').read_text()
if '8038C580' not in config.upper() or '8038E920' not in config.upper():
    raise SystemExit('Translation SDA bases are not Japanese')
path = host / 'apple/ios/RuntimeInfo.plist'
info = plistlib.loads(path.read_bytes())
info['CFBundleIdentifier'] = 'dev.kartpad.rmcj01.ios'
info['CFBundleDisplayName'] = 'KartPad Japan'
path.write_bytes(plistlib.dumps(info))
path = runtime / 'cmake/PublicProducts.cmake'
path.write_text(path.read_text().replace(
    'XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER dev.kartpad.app',
    'XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER dev.kartpad.rmcj01.ios'))
PY
KARTPAD_IOS_HOST_ROOT="$work/host" KARTPAD_IOS_AUDIT_REGION=J \
  "$repo/scripts/build-ios-device-game-app.sh" "$runtime" "$build" "$translation" "$product" \
  > "$work/build.log" 2>&1
echo "Japanese unsigned iOS app: $build/Release-iphoneos/KartPad.app"
echo "Signing, installation, and physical-device acceptance are separate steps."
