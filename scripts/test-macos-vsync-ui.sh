#!/usr/bin/env bash
# Native AppKit controls, isolated from game startup, Mii handling and user defaults.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
source="${1:?pass the prepared macOS runtime source}"
output="${2:?pass a fresh absolute test output directory}"
if [[ "${output}" != /* || -e "${output}" ]]; then
  echo 'ERROR: test output must be a fresh absolute directory' >&2
  exit 64
fi
mkdir -p "${output}"
touch "${output}/portable.txt"
clang++ -std=c++20 -fobjc-arc \
  -I "${repo_root}/apple/macos" -I "${source}/include" \
  -isystem "${source}/third_party/toml11" \
  "${repo_root}/tests/macos/vsync_settings_ui.mm" -framework Cocoa \
  -o "${output}/vsync-settings-ui"
"${output}/vsync-settings-ui" "${output}" first
"${output}/vsync-settings-ui" "${output}" reopen
