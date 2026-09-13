#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
# shellcheck source=android-toolchain-versions.sh
source "$repo_root/scripts/android-toolchain-versions.sh"
sdk_root="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/Library/Android/sdk}}"
adb="$sdk_root/platform-tools/adb"
lane="${1:-phone}"
case "$lane" in
  phone) user_rotation=1 ;;
  tablet) user_rotation=0 ;;
  *) echo "ERROR: lane must be phone or tablet" >&2; exit 64 ;;
esac

emulator_targets="$("$adb" devices 2>/dev/null | awk '$1 ~ /^emulator-[0-9]+$/ && $2 == "device" {print $1}')"
emulator_count="$(printf '%s\n' "$emulator_targets" | awk 'NF {count++} END {print count+0}')"
[[ "$emulator_count" == 1 ]] || {
  echo "ERROR: expected exactly one authorized Android emulator; no physical device will be modified" >&2
  exit 1
}
export ANDROID_SERIAL="$emulator_targets"
[[ "$("$adb" shell getprop ro.kernel.qemu | tr -d '\r')" == 1 ]] || {
  echo "ERROR: target is not an emulator" >&2
  exit 1
}

"$repo_root/scripts/build-android-fixture.sh"
apk="$repo_root/android/app/build/outputs/apk/debug/app-debug.apk"
"$adb" install -r "$apk" >/dev/null
"$adb" shell input keyevent KEYCODE_WAKEUP >/dev/null
"$adb" shell wm dismiss-keyguard >/dev/null 2>&1 || true
"$adb" shell settings put system accelerometer_rotation 0
"$adb" shell settings put system user_rotation "$user_rotation"
"$adb" shell pm clear dev.kartpad.android >/dev/null
"$adb" logcat -c
"$adb" shell am start -W -n dev.kartpad.android/.KartPadActivity \
  --ez dev.kartpad.android.TEST_TOUCH_EDITOR_FLOW true >/dev/null

expected="A4 touch editor fixture passed selected=A dragged=A hide=shown size=1.25 back=settings reset=defaults"
for _ in {1..30}; do
  output="$("$adb" logcat -d -v brief KartPadFixture:I AndroidRuntime:E '*:S')"
  if grep -Fq "$expected" <<<"$output"; then
    printf '%s\n' "$expected"
    exit 0
  fi
  if grep -Fq "A4 touch editor fixture failed" <<<"$output"; then
    printf '%s\n' "$output" >&2
    exit 1
  fi
  sleep 1
done

echo "ERROR: touch-editor fixture did not emit its pass marker" >&2
"$adb" logcat -d -v brief KartPadFixture:V AndroidRuntime:E '*:S' >&2
exit 1
