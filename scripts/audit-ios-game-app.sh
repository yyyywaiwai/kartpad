#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 || "$1" != /* || "$1" != *.app ]]; then
  echo "usage: $0 /absolute/path/to/KartPad.app [IOSSIMULATOR|IOS]" >&2
  exit 64
fi

app="$1"
expected_platform="${2:-IOSSIMULATOR}"
region="${KARTPAD_IOS_AUDIT_REGION:-P}"
case "${region}" in
  P) bundle_identifier=dev.kartpad.app; disc_id=RMCP01; region_name=PAL ;;
  J) bundle_identifier=dev.kartpad.rmcj01.ios; disc_id=RMCJ01; region_name=Japan ;;
  *) echo "KARTPAD_IOS_AUDIT_REGION must be P or J" >&2; exit 64 ;;
esac
if [[ "${expected_platform}" != "IOSSIMULATOR" && "${expected_platform}" != "IOS" ]]; then
  echo "expected platform must be IOSSIMULATOR or IOS" >&2
  exit 64
fi

plist="${app}/Info.plist"
binary="${app}/KartPad"
test -d "${app}"
test -x "${binary}"
test -f "${plist}"
test -f "${app}/PrivacyInfo.xcprivacy"
test -f "${app}/Assets.car"
test -f "${app}/initial_pipeline_cache.db"
test -f "${app}/dsp_coef.bin"
plutil -lint "${plist}" "${app}/PrivacyInfo.xcprivacy" >/dev/null
test "$(plutil -extract CFBundleIdentifier raw "${plist}")" = "${bundle_identifier}"
test "$(plutil -extract CFBundleExecutable raw "${plist}")" = "KartPad"
test "$(plutil -extract MinimumOSVersion raw "${plist}")" = "16.0"
test "$(plutil -extract UIApplicationSceneManifest.UISceneConfigurations.UIWindowSceneSessionRoleApplication.0.UISceneDelegateClassName raw "${plist}")" = "SDLUIKitSceneDelegate"
test "$(plutil -extract CFBundleIcons.CFBundlePrimaryIcon.CFBundleIconName raw "${plist}")" = "AppIcon"
test "$(plutil -extract CFBundleIcons~ipad.CFBundlePrimaryIcon.CFBundleIconName raw "${plist}")" = "AppIcon"
test "$(plutil -extract UIFileSharingEnabled raw "${plist}")" = "true"
test "$(plutil -extract LSSupportsOpeningDocumentsInPlace raw "${plist}")" = "true"
test -n "$(plutil -extract NSLocalNetworkUsageDescription raw "${plist}")"

if [[ "$(file -b "${binary}")" != *"Mach-O 64-bit executable arm64"* ]]; then
  echo "KartPad game runtime is not arm64 Mach-O" >&2
  exit 65
fi
build_metadata="$(vtool -show-build "${binary}")"
if [[ "$(awk '/platform/{print $2; exit}' <<<"${build_metadata}")" != "${expected_platform}" ]] ||
   [[ "$(awk '/minos/{print $2; exit}' <<<"${build_metadata}")" != "16.0" ]]; then
  echo "binary is not an ${expected_platform} 16.0 artifact" >&2
  exit 65
fi

for forbidden in '*.wbfs' '*.iso' '*.rvz' '*.wia' '*.gcz' 'rksys.dat' '*.mobileprovision'; do
  forbidden_path="$(find "${app}" -name "${forbidden}" -print -quit)"
  if [[ -n "${forbidden_path}" ]]; then
    echo "game app contains forbidden private/signing data: ${forbidden}" >&2
    exit 70
  fi
done

while IFS= read -r dependency; do
  case "${dependency}" in
    /System/Library/*|/usr/lib/*) ;;
    *)
      echo "game app contains non-system dependency: ${dependency}" >&2
      exit 69
      ;;
  esac
done < <(otool -L "${binary}" | tail -n +2 | awk '{print $1}')

symbols="$(nm -gj "${binary}")"
for required_symbol in \
  _KartPadMobileEnsureGameDataAvailable \
  _KartPadMobileRuntimeHostInstall \
  _KartPadMobileReadClassicInput \
  _KartPadMobileReadClassicInputForPlayer \
  '_OBJC_CLASS_$_SDLUIKitSceneDelegate' \
  '_OBJC_CLASS_$_KartPadPhysicalControllers' \
  '_OBJC_CLASS_$_KartPadMotionSteering' \
  '_OBJC_CLASS_$_SunPadGameOverlay' \
  '_OBJC_CLASS_$_SunPadInputMixer' \
  '_OBJC_CLASS_$_SunPadControllerMappingStore'; do
  if ! rg -F -q "${required_symbol}" <<<"${symbols}"; then
    echo "game app is missing required mobile symbol: ${required_symbol}" >&2
    exit 69
  fi
done

for motion_contract in \
  'Motion Steering' \
  'Turn On & Recenter' \
  'KartPadMotionSteeringEnabled'; do
  if ! rg -a -F -q "${motion_contract}" "${binary}"; then
    echo "game app is missing the motion-steering contract: ${motion_contract}" >&2
    exit 69
  fi
done

for experimental_feature_contract in \
  'Player Identity' \
  'Set Player Name' \
  'dev.kartpad.manage-miis' \
  'PendingRFL_DB.dat' \
  'PendingPlayerIdentity.plist' \
  'Experimental Wii Remote + Nunchuk' \
  'Direct Wii Remote pairing is currently available only in the macOS build.'; do
  if ! rg -a -F -q "${experimental_feature_contract}" "${binary}"; then
    echo "game app is missing an experimental feature contract: ${experimental_feature_contract}" >&2
    exit 69
  fi
done

for touch_contract in \
  'Acceleration locked' \
  'Drift, hop, brake, or reverse.'; do
  if ! rg -a -F -q "${touch_contract}" "${binary}"; then
    echo "game app is missing the KartPad touch-control contract: ${touch_contract}" >&2
    exit 69
  fi
done

if ! rg -a -F -q '[KartPad] exact SunPad runtime overlay installed' "${binary}"; then
  echo "game app does not contain the exact-overlay runtime host" >&2
  exit 69
fi
for importer_contract in \
  'Game Data Required' \
  "Import from This Installation's Folder" \
  'Opening disc image' \
  'Game-file extraction was incomplete' \
  'RemoveGameDataOnNextLaunch' \
  'Game Data Removal Scheduled' \
  "KartPad currently supports ${disc_id} (${region_name}), disc 0, revision 0 only." \
  "The validated ${disc_id} data is stored privately." \
  'GameData.import-' \
  'NSFileProtectionCompleteUntilFirstUserAuthentication'; do
  if ! rg -a -F -q "${importer_contract}" "${binary}"; then
    echo "game app is missing the private game-data importer contract: ${importer_contract}" >&2
    exit 69
  fi
done
if [[ "${region}" == J ]]; then
  if ! rg -a -F -q '1b9621ef7c5d97dada103e50e5389730e67f3c2545dda592edd4b5843655af91' "${binary}"; then
    echo "Japanese app is missing the exact RMCJ01 DOL validation hash" >&2
    exit 69
  fi
  if rg -a -F -q 'KartPad currently supports RMCP01' "${binary}"; then
    echo "Japanese app retains the PAL importer contract" >&2
    exit 69
  fi
fi
if rg -a -F -q "game-data importer is not connected" "${binary}"; then
  echo "game app still contains the placeholder game-data importer" >&2
  exit 69
fi
if nm -gj "${binary}" | rg -q 'JitArm64|JitInterface|CachedInterpreter'; then
  echo "game app contains an unexpected Dolphin execution-core symbol" >&2
  exit 69
fi
if [[ "${expected_platform}" == "IOSSIMULATOR" ]]; then
  if ! rg -a -F -q 'KARTPAD_IMPORT_FORCE_SWAP_FAILURE' "${binary}"; then
    echo "Simulator app is missing the import rollback test hook" >&2
    exit 69
  fi
  if ! rg -a -F -q 'KARTPAD_TOUCH_HOLD_SELF_TEST' "${binary}"; then
    echo "Simulator app is missing the touch-hold test hook" >&2
    exit 69
  fi
  if ! rg -a -F -q 'KARTPAD_TOUCH_INPUT_SELF_TEST' "${binary}"; then
    echo "Simulator app is missing the touch-input test hook" >&2
    exit 69
  fi
  if ! rg -a -F -q 'KARTPAD_TOUCH_MODAL_SELF_TEST' "${binary}"; then
    echo "Simulator app is missing the touch-modal input-clear test hook" >&2
    exit 69
  fi
  if ! rg -a -F -q 'KARTPAD_TOUCH_EDITOR_UI_TEST' "${binary}"; then
    echo "Simulator app is missing the touch-editor UI test hook" >&2
    exit 69
  fi
else
  for simulator_only_contract in \
    'KARTPAD_IMPORT_FORCE_SWAP_FAILURE' \
    'KARTPAD_TOUCH_HOLD_SELF_TEST' \
    'KARTPAD_TOUCH_INPUT_SELF_TEST' \
    'KARTPAD_TOUCH_MODAL_SELF_TEST' \
    'KARTPAD_TOUCH_EDITOR_UI_TEST'; do
    if rg -a -F -q "${simulator_only_contract}" "${binary}"; then
      echo "device app contains Simulator-only contract: ${simulator_only_contract}" >&2
      exit 69
    fi
  done
fi

echo "iOS ${expected_platform} full-game app audit passed: ${app}"
shasum -a 256 "${binary}" "${app}/Assets.car" "${app}/PrivacyInfo.xcprivacy"
