#!/usr/bin/env bash
# Isolated Japanese Android build; supplied DATA and translations stay read-only.
set -euo pipefail
repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"
translation="${1:-$repo/private/rmcj01/verified/translation}"
data="${2:-$repo/data}"
tag="${KARTPAD_RMCJ_BUILD_TAG:-android-development}"
[[ "$tag" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid build tag" >&2; exit 64; }
work="$repo/private/rmcj01/$tag"
build="$repo/build/rmcj01-$tag"
for output in "$work" "$build"; do
  [[ ! -e "$output" ]] || { echo "Output exists; choose a fresh build tag: $output" >&2; exit 73; }
done
export PYTHONPATH="$repo/builder${PYTHONPATH:+:$PYTHONPATH}"
export PATH="$repo/build/toolchains/python/bin:$PATH"
python3 -m kartpad_builder.rmcj01_android --translation "$translation"
"$repo/scripts/check-android-host.sh"
product=base
if grep -Eq '^set\(MKW_HAVE_RETRO_REWIND_SHARDS ON\)' "$translation/build_shards/shards.cmake"; then
  product=dual
fi
mkdir -p "$work"
"$repo/scripts/prepare-android-game-runtime.sh" \
  "$translation" "$build/runtime" "$build/native" "$product" > "$work/prepare.log" 2>&1
python3 -m kartpad_builder.rmcj01 --data "$data" --output "$work" --runtime "$build/runtime"
python3 -m kartpad_builder.rmcj01_android --translation "$translation" --output "$work"
# Rebuild the DiscIO importer from the Japanese host, never reuse PAL's .so.
KARTPAD_ANDROID_HOST_ROOT="$work/host" "$repo/scripts/build-android-discio-probe.sh" \
  "$repo/ref/upstream/dolphin" "$build/discio-source" "$build/discio-build" "$build/discio-jni" \
  > "$work/discio.log" 2>&1
KARTPAD_ANDROID_HOST_ROOT="$work/host" KARTPAD_DISCIO_JNI_ROOT="$build/discio-jni" \
  "$repo/scripts/build-android-game-app.sh" "$translation" "$build/runtime" "$build/native" \
  > "$work/build.log" 2>&1
if [[ "${KARTPAD_ANDROID_PACKAGE_FORMAT:-apk}" == apk ]]; then
  apk="$work/host/android/app/build/outputs/apk/debug/app-debug.apk"
  KARTPAD_ANDROID_AUDIT_REGION=J \
    KARTPAD_ANDROID_EXPECTED_VERSION_NAME="${KARTPAD_ANDROID_VERSION_NAME:-0.4.10-android.1}" \
    "$repo/scripts/audit-android-package.sh" "$apk" > "$work/audit.log" 2>&1
  echo "Japanese Android APK: $apk"
else
  echo "Japanese unsigned AAB (not APK-audited): $work/host/android/app/build/outputs/bundle/release/app-release.aab"
fi
