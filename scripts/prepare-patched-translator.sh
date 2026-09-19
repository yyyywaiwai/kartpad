#!/bin/zsh
set -euo pipefail

repo=${0:A:h:h}
source="$repo/vendor/wiicompiled"
stage="$repo/build/wiicompiled-fpscr"

# Keep the established output path for translator and native-registration callers.
# Maintained source lives in Git; this command never replays translator patches.
[[ -f "$source/translator/src/Translator.Cli/Translator.Cli.csproj" ]] || {
  print -u2 'ERROR: missing tracked WiiCompiled translator source'
  exit 1
}
python3 "$repo/scripts/stage-maintained-translator.py" "$stage"

dotnet_bin="${KARTPAD_DOTNET:-$(command -v dotnet || true)}"
if [[ -z "$dotnet_bin" ]]; then
  dotnet_bin="$repo/build/toolchains/dotnet/dotnet"
fi
if [[ ! -x "$dotnet_bin" ]]; then
  dotnet_bin=/opt/homebrew/opt/dotnet@8/bin/dotnet
fi
project="$stage/translator/src/Translator.Cli/Translator.Cli.csproj"
"$dotnet_bin" build "$project" -c Release
