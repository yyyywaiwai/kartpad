#!/usr/bin/env python3
"""Guard one translated REL diagnostic, including the aggregate source compiled.

The emitter can read a cached source bundle instead of the standalone function.
Apply the same transformation after emission and verify the graph before builds.
Unknown/partial guards must be regenerated, never repaired by deleting control flow.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SIGNATURE = 'extern "C" void func_8000A440(CpuContext* MKW_RESTRICT ctx)\n{'
HEADER_ENTRY = "    r4 = MemoryInline::FlatRead32(r28);"
TABLE_LOAD = "    r30 = MemoryInline::FlatRead32((r28 + 16));\n"
LOOP_ENTRY = "    r29 = 0;\n    goto loc_8000A510;"
TABLE_ENTRY = TABLE_LOAD + LOOP_ENTRY
MARKER = "// KartPad: validate StaticR.rel report table before dereference"
GUARD = """    // KartPad: validate StaticR.rel report table before dereference.
    // A malformed or overwritten REL must not turn its diagnostic path into
    // a native flat-memory crash on Apple or Android. Branch through the
    // generated cleanup block; never return before restoring the prologue.
    if (!RecompMod::TryGetRelReportSectionTable(r28, r30)) {
        goto loc_8000A51C;
    }
    r4 = MemoryInline::FlatRead32(r28);"""


def report_span(source: str, path: Path) -> tuple[int, int]:
    if source.count(SIGNATURE) != 1:
        raise SystemExit(f"expected exactly one func_8000A440 definition in {path}")
    if '#include "recomp_mod_loader.h"' not in source:
        raise SystemExit(f"missing recomp_mod_loader.h in {path}")
    start = source.index(SIGNATURE)
    end = source.find("\n// RECOMP_GUEST_ABI ", start)
    if end < 0 or not source[start:end].rstrip().endswith("}"):
        raise SystemExit(f"unexpected generated report boundary in {path}; regenerate translation")
    return start, end


def verify_body(body: str, path: Path) -> None:
    if body.count(MARKER) != 1 or body.count(GUARD) != 1:
        raise SystemExit(f"missing complete REL report guard in {path}; regenerate translation")
    if TABLE_LOAD.strip() in body or body.count(HEADER_ENTRY) != 1:
        raise SystemExit(f"unchecked REL read in {path}; regenerate translation")
    # Preserve the initial count check: zero sections must never enter the table.
    required = [LOOP_ENTRY, 'loc_8000A4E4:\n{', 'loc_8000A510:\n{', 'loc_8000A51C:\n{']
    if any(body.count(item) != 1 for item in required):
        raise SystemExit(f"missing REL loop/cleanup control flow in {path}; regenerate translation")
    offsets = [body.index(GUARD)] + [body.index(item) for item in required]
    if offsets != sorted(offsets):
        raise SystemExit(f"unexpected REL loop/cleanup order in {path}; regenerate translation")
    reads = list(re.finditer(r'MemoryInline::FlatRead32\(\(?r(?:28|30)\b', body))
    if not reads or reads[0].start() != body.index(HEADER_ENTRY) + len('    r4 = '):
        raise SystemExit(f"REL read before guard in {path}; regenerate translation")
    cleanup = body[body.index('loc_8000A51C:\n{'):]
    for restore in ('ctx->lr = r0;', 'r1 = (r1 + 32);', 'ctx->gpr[1] = r1;', 'return;'):
        if restore not in cleanup:
            raise SystemExit(f"missing REL epilogue in {path}; regenerate translation")


def inject(path: Path) -> bool:
    source = path.read_text()
    start, end = report_span(source, path)
    body = source[start:end]
    if MARKER in body or 'TryGetRelReportSectionTable' in body:
        verify_body(body, path)
        return False
    if body.count(HEADER_ENTRY) != 1 or body.count(TABLE_ENTRY) != 1:
        raise SystemExit(f"unexpected REL report source in {path}; regenerate translation")
    guarded = body.replace(HEADER_ENTRY, GUARD, 1).replace(TABLE_ENTRY, LOOP_ENTRY, 1)
    verify_body(guarded, path)
    path.write_text(source[:start] + guarded + source[end:])
    return True


def verify(path: Path) -> None:
    source = path.read_text()
    start, end = report_span(source, path)
    verify_body(source[start:end], path)


def shard_definition(root: Path) -> Path:
    # Read the generated CMake source list, not arbitrary .cpp files that may
    # be leftovers or absent from the build. Never mutate paths outside root.
    root = root.resolve()
    graph = (root / 'shards.cmake').read_text()
    entries = re.findall(r'^\s*"([^"\n]+\.cpp)"\s*$', graph, re.M)
    if not entries:
        raise SystemExit(f"missing literal compiled source list in {root}/shards.cmake")
    definitions = []
    for entry in sorted(set(entries)):
        path = Path(entry).resolve()
        if SIGNATURE in path.read_text():
            if not path.is_relative_to(root):
                raise SystemExit(f"compiled report outside shard root; regenerate translation: {path}")
            definitions.append(path)
    if len(definitions) != 1:
        raise SystemExit(f"expected one compiled func_8000A440 under {root}, found {len(definitions)}")
    return definitions[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--verify', action='store_true')
    modes.add_argument('--inject-shards', type=Path)
    modes.add_argument('--verify-shards', type=Path)
    parser.add_argument('function', type=Path, nargs='?')
    args = parser.parse_args()
    shards = args.inject_shards or args.verify_shards
    if bool(shards) == bool(args.function):
        parser.error('provide either a function path or a shard mode/root')
    try:
        path = shard_definition(shards) if shards else args.function
        if args.verify or args.verify_shards:
            verify(path)
        else:
            inject(path)
    except OSError as error:
        parser.exit(1, f'REL report guard: {error}\n')
    print(f'verified REL report guard: {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
