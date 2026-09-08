#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
branding_dir="$repo_root/branding"
export_dir="$branding_dir/exports"

command -v rsvg-convert >/dev/null 2>&1 || {
  echo 'librsvg is required (brew install librsvg).' >&2
  exit 1
}
command -v magick >/dev/null 2>&1 || {
  echo 'ImageMagick is required for deterministic downsampling (brew install imagemagick).' >&2
  exit 1
}

mkdir -p "$export_dir/macos"
render_dir="$(mktemp -d)"
trap 'rm -rf "$render_dir"' EXIT

rsvg-convert --width 1024 --height 1024 --output "$render_dir/default.png" "$branding_dir/KartPadIcon.svg"
rsvg-convert --width 1024 --height 1024 --output "$render_dir/dark.png" "$branding_dir/KartPadIcon-Dark.svg"
rsvg-convert --width 1024 --height 1024 --output "$render_dir/tinted.png" "$branding_dir/KartPadIcon-Tinted.svg"

magick "$render_dir/default.png" -alpha off -strip -define png:color-type=2 "$export_dir/KartPadIcon-1024.png"
magick "$render_dir/dark.png" -alpha off -strip -define png:color-type=2 "$export_dir/KartPadIcon-Dark-1024.png"
magick "$render_dir/tinted.png" -alpha off -strip -define png:color-type=2 "$export_dir/KartPadIcon-Tinted-1024.png"

"$repo_root/scripts/generate-macos-icon-assets.sh"

dimensions="$(sips -g pixelWidth -g pixelHeight -g hasAlpha "$export_dir/KartPadIcon-1024.png")"
grep -q 'pixelWidth: 1024' <<<"$dimensions"
grep -q 'pixelHeight: 1024' <<<"$dimensions"
grep -q 'hasAlpha: no' <<<"$dimensions"

echo "Generated opaque icon assets in $export_dir"
