#!/usr/bin/env python3
"""Extract source-only Aurora WGSL helpers; never read game data or captures."""
import hashlib
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text()
start = source.index('fn bswap32(')
end = source.index('fn tev_overflow_f32(', start)
helpers = source[start:end].replace('{{', '{').replace('}}', '}')
# Extracting the actual shipped functions catches upstream changes in the probe.
if '{0}' in helpers or 'fn fetch_s16_4(' not in helpers:
    raise SystemExit('Unexpected Aurora shader helper layout')
pathlib.Path(sys.argv[2]).write_text(
    'static constexpr const char* kHelperSha = "' + hashlib.sha256(helpers.encode()).hexdigest() + '";\n'
    'static constexpr const char* kHelpers = R"WGSL(' + helpers + ')WGSL";\n')
