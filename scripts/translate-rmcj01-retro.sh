#!/usr/bin/env bash
# Private Japanese Retro Rewind graph; never silently fetches an online payload.
set -euo pipefail
repo="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo"
[[ $# == 3 ]] || { echo "usage: $0 DATA RETRO_ROOT JAPANESE_PAYLOAD" >&2; exit 64; }
tag="${KARTPAD_RMCJ_BUILD_TAG:-retro-development}"
[[ "$tag" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid build tag" >&2; exit 64; }
work="$repo/private/rmcj01/$tag"
runtime="$repo/build/rmcj01-$tag-runtime"
for output in "$work" "$runtime"; do
  [[ ! -e "$output" ]] || { echo "Output exists; choose a fresh build tag: $output" >&2; exit 73; }
done
mkdir -p "$work"
export PYTHONPATH="$repo/builder${PYTHONPATH:+:$PYTHONPATH}"
export KARTPAD_DOTNET="${KARTPAD_DOTNET:-$repo/build/toolchains/dotnet/dotnet}"
"$repo/scripts/prepare-patched-translator.sh" > "$work/translator-build.log" 2>&1
KARTPAD_PREPARE_ONLY=1 "$repo/scripts/prepare-g7-game-runtime.sh" \
  "$work/translation" "$runtime" "$repo/build/rmcj01-$tag-macos" dual \
  > "$work/runtime-prepare.log" 2>&1
python3 -m kartpad_builder.rmcj01 --data "$1" --output "$work" --runtime "$runtime" \
  --retro-root "$2" --retro-payload "$3"
translator="$repo/build/wiicompiled-fpscr/translator/src/Translator.Cli/bin/Release/net8.0/Translator.Cli.dll"
manifest="$work/retro.yml"
run_translator() { "$KARTPAD_DOTNET" "$translator" "$@"; }
run_translator translate-recursive 0x800060A4 --project "$manifest" --profile retro-rewind \
  --threads 3 --prune-stale --output-metadata "$work/translation/base_translation_output.json" \
  > "$work/translation.log" 2>&1
"$work/inject-g10-rkg-fixture-hook.py" "$work/translation/functions/func_8051F604.cpp"
"$work/inject-g10-camera-lifecycle-guard.py" "$work/translation/functions/func_805A140C.cpp"
for function in 8083D614 80846288 8084D9F4 806435B4; do
  "$work/inject-online-rkg-selection-hooks.py" "$work/translation/functions/func_${function}.cpp"
done
run_translator emit-base-manifest --project "$manifest" --profile retro-rewind \
  --out "$work/translation/base" --functions-dir "$work/translation/functions" \
  --translation-output-metadata "$work/translation/base_translation_output.json" --region J \
  > "$work/base-manifest.log" 2>&1
run_translator translate-mod --project "$manifest" --profile retro-rewind \
  --base-manifest "$work/translation/base/base_manifest.json" \
  --base-translation-output-metadata "$work/translation/base_translation_output.json" \
  --code-pul "$2/Binaries/Code.pul" --mod-root "$2" --mod-name "Retro Rewind" \
  --region J --out "$work/mod" --prefer-cached-inputs --emit-cpp --threads 3 \
  --retro-wfc-payload "$3" > "$work/mod-translation.log" 2>&1
run_translator generate-data-init --project "$manifest" --profile retro-rewind
run_translator emit-build-shards --project "$manifest" --profile retro-rewind \
  --base-metadata "$work/translation/base_translation_output.json" \
  --base-functions-dir "$work/translation/functions" --native-source-dir "$runtime/src" \
  --resolved-profile "$work/mod/resolved_dispatch_profile.json" --retro-cpp-dir "$work/mod/cpp" \
  --out "$work/translation/build_shards"
python3 - "$work" <<'PY'
import re, sys
from pathlib import Path
root = Path(sys.argv[1])
for path in (root / 'translation/data_sections_init_blobs.S', root / 'mod/cpp/mod_data_patches_blobs.S'):
    text = path.read_text()
    if '.globl _k' not in text:
        path.write_text(re.sub(r'^\.globl (k[^\n]+)\n\1:',
                              r'.globl \1\n.globl _\1\n\1:\n_\1:', text, flags=re.M))
PY
echo "Prepared Japanese Retro Rewind translation: $work/translation"
echo "Compilation and runtime/online acceptance remain separate steps."
