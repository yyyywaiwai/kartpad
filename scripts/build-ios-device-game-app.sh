#!/usr/bin/env bash
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
absolute_from_repo() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "${repo_root}" "$1" ;;
  esac
}

runtime_source="$(absolute_from_repo "${1:-build/g14-ios-game-runtime-source}")"
xcode_build="$(absolute_from_repo "${2:-build/g14-ios-device-game-app-xcode}")"
translation_root="$(absolute_from_repo "${3:-private/g8-full-translation}")"
product="${4:-dual}"
host_root="$(absolute_from_repo "${KARTPAD_IOS_HOST_ROOT:-${repo_root}}")"
dawn_archive="${repo_root}/build/dependency-cache/dawn-ios-arm64-v20260603.191052.tar.gz"
dawn_sha256="a361fcca75929fa5c766cfcde979c010a6da7d805e5db8e15c75e73fd8260e78"
discio_source="${KARTPAD_DISCIO_SOURCE_DIR:-${repo_root}/build/dolphin-ios-discio-iphoneos-source}"
discio_build="${KARTPAD_DISCIO_BUILD_DIR:-${repo_root}/build/dolphin-ios-discio-iphoneos-build}"
app="${xcode_build}/Release-iphoneos/KartPad.app"
path_map_flags="-ffile-prefix-map=${repo_root}=KartPad -fmacro-prefix-map=${repo_root}=KartPad"

case "${product}" in
  base) product_target="WiiCompiled" ;;
  retro-rewind) product_target="RetroRewind" ;;
  dual) product_target="KartPadDual" ;;
  *) echo "ERROR: product must be base, retro-rewind, or dual" >&2; exit 64 ;;
esac

region_verification=()
if [[ "${KARTPAD_IOS_AUDIT_REGION:-P}" == J ]]; then
  PYTHONPATH="${repo_root}/builder${PYTHONPATH:+:${PYTHONPATH}}" python3 - "${repo_root}" "${translation_root}" <<'PYCODE'
import sys
from pathlib import Path
from kartpad_builder.rmcj01 import validate_retro_version
validate_retro_version(Path(sys.argv[1]), Path(sys.argv[2]))
PYCODE
  region_verification=(--japan-data "${KARTPAD_RMCJ_DATA:?Japanese build requires its validated data path}")
fi
python3 "${repo_root}/scripts/stage-maintained-runtime.py" --verify ios "${runtime_source}" \
  ${region_verification[@]+"${region_verification[@]}"}

if [[ ! -f "${runtime_source}/CMakeLists.txt" ]] ||
   ! rg -q 'MKW_KARTPAD_REPO_ROOT' "${runtime_source}/cmake/PublicProducts.cmake"; then
  echo "ERROR: prepare the integrated source first with scripts/prepare-ios-game-runtime.sh" >&2
  exit 66
fi
# Reject older prepared trees that still target the runtime at Apple M2.
if ! rg -F -q 'CMAKE_OSX_SYSROOT MATCHES "iphoneos|iPhoneOS"' \
    "${runtime_source}/cmake/PublicProducts.cmake"; then
  echo "ERROR: stale iOS CPU baseline; prepare a fresh runtime source before building" >&2
  exit 66
fi
if [[ ! -f "${translation_root}/build_shards/shards.cmake" ]]; then
  echo "ERROR: missing real-title translation: ${translation_root}" >&2
  exit 66
fi
if [[ "${KARTPAD_SKIP_REL_REPORT_GUARD:-0}" == "1" ]]; then
  echo "skipping PAL REL report guard verify (region-specific translation)"
else
  python3 "${repo_root}/scripts/inject-retro-rel-report-guard.py" --verify \
    "${translation_root}/functions/func_8000A440.cpp"
  python3 "${repo_root}/scripts/inject-retro-rel-report-guard.py" --verify-shards \
    "${translation_root}/build_shards"
fi
if [[ ! -f "${dawn_archive}" ]] ||
   [[ "$(shasum -a 256 "${dawn_archive}" | awk '{print $1}')" != "${dawn_sha256}" ]]; then
  echo "ERROR: missing or mismatched pinned physical-iOS Dawn archive" >&2
  exit 66
fi
if [[ ! -f "${discio_source}/Source/Core/DiscIO/DiscExtractor.h" ||
      ! -f "${discio_build}/Source/Core/DiscIO/libdiscio.a" ]]; then
  echo "ERROR: missing physical-iOS DiscIO dependency" >&2
  exit 66
fi

generated_link="$(dirname "${runtime_source}")/generated"
if [[ -e "${generated_link}" && ! -L "${generated_link}" ]]; then
  echo "ERROR: generated path exists and is not a symlink: ${generated_link}" >&2
  exit 73
fi
previous_generated_target=""
if [[ -L "${generated_link}" ]]; then
  previous_generated_target="$(readlink "${generated_link}")"
fi
restore_generated_link() {
  if [[ -n "${previous_generated_target}" ]]; then
    ln -sfn "${previous_generated_target}" "${generated_link}"
  elif [[ -L "${generated_link}" ]]; then
    rm "${generated_link}"
  fi
}
trap restore_generated_link EXIT
ln -sfn "${translation_root}" "${generated_link}"

"${repo_root}/scripts/verify-sunpad-overlay-snapshot.sh"
plutil -lint "${host_root}/apple/ios/RuntimeInfo.plist" \
  "${host_root}/apple/ios/PrivacyInfo.xcprivacy" >/dev/null

# A prior device deployment may have signed this reusable build product in
# place. Remove only that generated signing residue before the unsigned build
# so the privacy audit cannot inspect a stale profile from an older install.
rm -f "${app}/embedded.mobileprovision"
if [[ -d "${app}/_CodeSignature" ]]; then
  rm -r "${app}/_CodeSignature"
fi

cmake -S "${runtime_source}" -B "${xcode_build}" -G Xcode \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CONFIGURATION_TYPES=Release \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DCMAKE_SYSTEM_PROCESSOR=arm64 \
  -DCMAKE_OSX_SYSROOT=iphoneos \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0 \
  -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG ${path_map_flags}" \
  -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG ${path_map_flags}" \
  -DCMAKE_OBJC_FLAGS_RELEASE="-O3 -DNDEBUG ${path_map_flags}" \
  -DCMAKE_OBJCXX_FLAGS_RELEASE="-O3 -DNDEBUG ${path_map_flags}" \
  -DMKW_AURORA_DIR="${runtime_source}/aurora-main" \
  -DAURORA_DAWN_PACKAGE_URL="file://${dawn_archive}" \
  -DAURORA_DAWN_PACKAGE_URL_HASH="SHA256=${dawn_sha256}" \
  -DMKW_TRANSLATED_SHARD_MANIFEST="${translation_root}/build_shards/shards.cmake" \
  -DMKW_KARTPAD_RUNTIME_INCLUDE="${repo_root}/runtime/include" \
  -DMKW_KARTPAD_REPO_ROOT="${host_root}" \
  -DMKW_KARTPAD_DISCIO_SOURCE_DIR="${discio_source}" \
  -DMKW_KARTPAD_DISCIO_BUILD_DIR="${discio_build}" \
  -DMKW_TRANSLATED_COMPILE_JOBS=2
python3 "${repo_root}/scripts/write-build-provenance.py" --repo "${repo_root}" \
  --runtime "${runtime_source}" --translation "${translation_root}" \
  --output "${xcode_build}/kartpad-build.json"
cmake --build "${xcode_build}" --config Release --target "${product_target}" -- \
  -sdk iphoneos CODE_SIGNING_ALLOWED=NO

cp "${xcode_build}/kartpad-build.json" "${app}/kartpad-build.json"
"${repo_root}/scripts/audit-ios-game-app.sh" "${app}" IOS
if rg -a -F -q "${repo_root}" "${app}/KartPad"; then
  echo "ERROR: physical-iOS app exposes its private KartPad build path" >&2
  exit 65
fi
echo "Built full translated physical-iOS game app: ${app}"
