#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

failures=0

for required_ignore in \
  'ref/Mario Kart Wii.wbfs' \
  'ref/sunpad' \
  'ref/upstream/Wiicompiled' \
  'private/example' \
  'generated/example' \
  'build-macos-local/example'; do
  if ! git check-ignore -q "$required_ignore"; then
    echo "ERROR: expected ignored path is not ignored: $required_ignore" >&2
    failures=$((failures + 1))
  fi
done

forbidden_pattern='\.(iso|gcm|gcz|ciso|wbfs|wia|rvz|sav|gci|dtm|pcap|pcapng|mobileprovision|p12|key|pem|jks|keystore|apk|aab|apks)$'
if git ls-files | grep -Eiq "$forbidden_pattern"; then
  echo 'ERROR: tracked files include private game, save, capture, or signing data:' >&2
  git ls-files | grep -Ei "$forbidden_pattern" >&2
  failures=$((failures + 1))
fi

while IFS= read -r tracked_file; do
  [[ -f "$tracked_file" ]] || continue
  file_size="$(stat -f '%z' "$tracked_file")"
  if (( file_size > 10485760 )); then
    echo "ERROR: tracked file exceeds the 10 MiB review threshold: $tracked_file ($file_size bytes)" >&2
    failures=$((failures + 1))
  fi
done < <(git ls-files)

secret_pattern='BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}'
if git grep -IEn "$secret_pattern" -- . ':!scripts/check-repo-safety.sh'; then
  echo 'ERROR: possible secret material found in tracked content.' >&2
  failures=$((failures + 1))
fi

if (( failures != 0 )); then
  echo "Repository safety audit failed with $failures finding(s)." >&2
  exit 1
fi

echo 'Repository safety audit passed.'
