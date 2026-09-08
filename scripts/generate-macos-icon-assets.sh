#!/usr/bin/env bash
set -euo pipefail
repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
master="${repo_root}/apple/ios/Assets.xcassets/AppIcon.appiconset/KartPadIcon-1024.png"
exports="${repo_root}/branding/exports"
temporary="$(mktemp -d)"
trap 'rm -rf "$temporary"' EXIT
iconset="${temporary}/KartPad.iconset"
mkdir -p "$iconset" "$exports/macos"
# Reuse the current shipped artwork exactly; only encode the Mac icon sizes.
for pixels in 16 32 64 128 256 512 1024; do
  if [[ "$pixels" == 1024 ]]; then
    cp "$master" "$exports/macos/KartPadIcon-${pixels}.png"
  else
    sips -z "$pixels" "$pixels" "$master" \
      --out "$exports/macos/KartPadIcon-${pixels}.png" >/dev/null
  fi
done
for points in 16 32 128 256 512; do
  cp "$exports/macos/KartPadIcon-${points}.png" "$iconset/icon_${points}x${points}.png"
  pixels=$((points * 2))
  cp "$exports/macos/KartPadIcon-${pixels}.png" "$iconset/icon_${points}x${points}@2x.png"
done
iconutil -c icns "$iconset" -o "$exports/KartPad.icns"
echo "Generated macOS ICNS from the current iPhone/iPad icon"
