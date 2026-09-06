#!/bin/zsh
set -euo pipefail

repo=${0:A:h:h}
upstream="$repo/ref/upstream/Wiicompiled"
stage="$repo/build/wiicompiled-fpscr"
patch_file="$repo/patches/wiicompiled-fpscr-state.patch"
dual_profile_patch="$repo/patches/wiicompiled-dual-profile-translator.patch"
kamek_v2_patch="$repo/patches/wiicompiled-kamek-v2.patch"
dual_symbols_patch="$repo/patches/wiicompiled-dual-profile-symbols.patch"
dual_closure_patch="$repo/patches/wiicompiled-dual-profile-closure.patch"
dynamic_overrides_patch="$repo/patches/wiicompiled-dynamic-overrides.patch"

mkdir -p "$stage"
rsync -a --delete --exclude .git --exclude bin --exclude obj \
  "$upstream/" "$stage/"
git apply --recount --unidiff-zero --unsafe-paths --directory="$stage" "$patch_file"
git apply --recount --unsafe-paths --directory="$stage" "$dual_profile_patch"
git apply --recount --unsafe-paths --directory="$stage" "$kamek_v2_patch"
patch --batch -p1 -d "$stage" < "$dual_symbols_patch"
patch --batch -p1 -d "$stage" < "$dual_closure_patch"
patch --batch -p1 -d "$stage" < "$dynamic_overrides_patch"

dotnet_bin="${KARTPAD_DOTNET:-$(command -v dotnet || true)}"
if [[ -z "$dotnet_bin" ]]; then
  dotnet_bin="$repo/build/toolchains/dotnet/dotnet"
fi
if [[ ! -x "$dotnet_bin" ]]; then
  dotnet_bin=/opt/homebrew/opt/dotnet@8/bin/dotnet
fi
project="$stage/translator/src/Translator.Cli/Translator.Cli.csproj"
"$dotnet_bin" build "$project" -c Release
