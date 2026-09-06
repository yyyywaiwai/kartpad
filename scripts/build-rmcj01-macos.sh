#!/usr/bin/env bash
# Private Japanese base-game development build. Does not enable public IPA builds.
set -euo pipefail
repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"
data="${1:-$repo/data}"
tag="${KARTPAD_RMCJ_BUILD_TAG:-development}"
[[ "$tag" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid build tag" >&2; exit 64; }
work="$repo/private/rmcj01/$tag"
runtime="$repo/build/rmcj01-$tag-runtime"
build="$repo/build/rmcj01-$tag-macos"
export PYTHONPATH="$repo/builder${PYTHONPATH:+:$PYTHONPATH}"
export PATH="$repo/build/toolchains/python/bin:$PATH"
dotnet="${KARTPAD_DOTNET:-$repo/build/toolchains/dotnet/dotnet}"
[[ -x "$dotnet" ]] || dotnet="$(command -v dotnet)"
export KARTPAD_DOTNET="$dotnet"
command -v ninja >/dev/null
for output in "$work" "$runtime" "$build"; do
  [[ ! -e "$output" ]] || { echo "Output exists; choose a fresh KARTPAD_RMCJ_BUILD_TAG: $output" >&2; exit 73; }
done
mkdir -p "$work"
python3 - "$data" <<'PY'
import sys
from pathlib import Path
from kartpad_builder.pipeline import _validate_extraction
from kartpad_builder.profiles import load_profiles
profile = next(p for p in load_profiles(Path('builder/profiles')) if p.id == 'mkwii-rmcj01-rev0')
_validate_extraction(profile, Path(sys.argv[1]).resolve())
PY
./scripts/prepare-patched-translator.sh > "$work/translator-build.log" 2>&1
KARTPAD_PREPARE_ONLY=1 ./scripts/prepare-g7-game-runtime.sh \
  "$work/translation" "$runtime" "$build" base > "$work/runtime-prepare.log" 2>&1
patch --batch -p1 -d "$runtime" < "$repo/patches/wiicompiled-rkg-primary-controller.patch"
python3 -m kartpad_builder.rmcj01 --data "$data" --output "$work" --runtime "$runtime"
translator="$repo/build/wiicompiled-fpscr/translator/src/Translator.Cli/bin/Release/net8.0/Translator.Cli.dll"
"$dotnet" "$translator" translate-recursive 0x800060A4 --project "$work/base.yml" \
  --threads 4 --prune-stale --output-metadata "$work/translation/base_translation_output.json" \
  > "$work/translation.log" 2>&1
"$work/inject-g10-rkg-fixture-hook.py" "$work/translation/functions/func_8051F604.cpp"
"$work/inject-g10-camera-lifecycle-guard.py" "$work/translation/functions/func_805A140C.cpp"
for function in 8083D614 80846288 8084D9F4 806435B4; do
  "$work/inject-online-rkg-selection-hooks.py" "$work/translation/functions/func_${function}.cpp"
done
"$dotnet" "$translator" generate-data-init --project "$work/base.yml"
python3 - "$work/translation/data_sections_init_blobs.S" <<'PY'
import re, sys
from pathlib import Path
path = Path(sys.argv[1])
path.write_text(re.sub(r'^\.globl (kData_[^\n]+)\n\1:',
                      r'.globl \1\n.globl _\1\n\1:\n_\1:', path.read_text(), flags=re.M))
PY
"$dotnet" "$translator" emit-build-shards --project "$work/base.yml" \
  --base-metadata "$work/translation/base_translation_output.json" \
  --base-functions-dir "$work/translation/functions" --native-source-dir "$runtime/src" \
  --out "$work/translation/build_shards"
# The upstream product uses ../generated for data blobs. Preserve other builds'
# link and restore it even if configure/build fails.
generated="$repo/build/generated"
[[ ! -e "$generated" || -L "$generated" ]] || { echo "generated is not a symlink" >&2; exit 73; }
previous=""
[[ ! -L "$generated" ]] || previous="$(readlink "$generated")"
restore_link() {
  if [[ -n "$previous" ]]; then ln -sfn "$previous" "$generated"; else rm -f "$generated"; fi
}
trap restore_link EXIT
ln -sfn "$work/translation" "$generated"
cmake -S "$runtime" -B "$build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 \
  -DMKW_AURORA_DIR="$runtime/aurora-main" \
  -DAURORA_DAWN_PACKAGE_URL="file://$repo/build/dependency-cache/dawn-darwin-arm64-v20260603.191052.tar.gz" \
  -DMKW_TRANSLATED_SHARD_MANIFEST="$work/translation/build_shards/shards.cmake" \
  -DMKW_KARTPAD_RUNTIME_INCLUDE="$repo/runtime/include" \
  -DMKW_KARTPAD_REPO_ROOT="$work/host" -DMKW_TRANSLATED_COMPILE_JOBS=3 > "$work/configure.log" 2>&1
cmake --build "$build" --target WiiCompiled --parallel 6 > "$work/build.log" 2>&1
./scripts/package-macos-runtime.sh "$build" "$work/run/KartPad-Japan.app" WiiCompiled
# Isolate all test saves/settings/caches from an installed PAL application's state.
touch "$work/run/portable.txt"
python3 - "$work/run/UserData" "$data" <<'PY'
import json, sys
from pathlib import Path
state = Path(sys.argv[1])
state.mkdir()
# JSON basic strings are also valid TOML strings for these filesystem paths.
(state / 'Config.toml').write_text(
    '[video]\nwidescreen = true\nresolution_multiplier = 1.0\n'
    'window_width = 960\nwindow_height = 540\ndisplay_mode = "windowed"\n'
    '[network]\nenabled = true\n[paths]\ndvd_root = '
    + json.dumps(str(Path(sys.argv[2]).resolve()), ensure_ascii=False)
    + '\nnand_root = "NAND"\n')
PY
plutil -replace CFBundleIdentifier -string dev.kartpad.rmcj01.development "$work/run/KartPad-Japan.app/Contents/Info.plist"
codesign --force --deep --sign - --entitlements "$repo/apple/macos/KartPad.entitlements" "$work/run/KartPad-Japan.app"
codesign --verify --deep --strict "$work/run/KartPad-Japan.app"
echo "Built private Japanese development app: $work/run/KartPad-Japan.app"
echo "Runtime acceptance remains a separate step; no test result is implied by compilation."
