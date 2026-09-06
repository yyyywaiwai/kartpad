"""Japanese-region development preparation (private output, no ROM mutation)."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
from pathlib import Path

from .errors import BuildError
from .pipeline import _validate_extraction
from .profiles import load_profiles, sha256_file
from .region_audit import map_address, read_address_map, read_dol_layout
from .retro_rewind import validate_rwfc_payload


REL_BASE = 0x8050FC60
JAPAN_WFC_PAYLOAD_SHA256 = "5a97dbe12aa9c41ce529d32830740d1eabb970474a3125be4bab5f4600ae29e7"


def prepare_retro(repo: Path, output: Path, retro_root: Path, payload: Path) -> Path:
    """Add a pinned Japanese mod manifest to an already prepared private port."""
    if not output.is_relative_to(repo / "private"):
        raise BuildError("Japanese Retro Rewind output must stay in private/")
    report = json.loads((output / "preparation.json").read_text())
    if report.get("region") != "J":
        raise BuildError("Retro Rewind requires a prepared Japanese base")
    profiles = load_profiles(repo / "builder/profiles")
    pal = next(p for p in profiles if p.id == "mkwii-rmcp01-rev0")
    japan = next(p for p in profiles if p.id == "mkwii-rmcj01-rev0")
    for entry in (pal.data["retroRewind"]["codePul"], pal.data["retroRewind"]["riivolutionXml"]):
        source = retro_root / entry["path"]
        if source.stat().st_size != entry["bytes"] or sha256_file(source) != entry["sha256"]:
            raise BuildError(f"Retro Rewind input does not match pinned {entry['path']}")
    image = payload.read_bytes()
    if (len(image) != 28992 or image[:12] != b"WWFC/Payload"
            or image[0x138:0x144].rstrip(b"\0") != b"RMCJD00"
            or sha256_file(payload) != JAPAN_WFC_PAYLOAD_SHA256):
        raise BuildError("Retro WFC payload is not the pinned Japanese RMCJD00 candidate")
    validate_rwfc_payload(payload, {"bytes": 28992, "sha256": JAPAN_WFC_PAYLOAD_SHA256})
    ranges = read_address_map((repo / japan.data["porting"]["addressMap"]).read_text(), "J")
    hook = map_address(0x800ED6E8, ranges)
    if hook != 0x800ED608:
        raise BuildError("Japanese bootstrap mapping changed")
    profile = (repo / "tools/mkwii-rmcp01-retro-rewind.yml").read_text().split("profiles:", 1)[1]
    profile = profile.replace("RMCP01", "RMCJ01").replace("region: P", "region: J")
    profile = profile.replace(pal.data["extraction"]["executables"]["dol"]["sha256"],
                              japan.data["extraction"]["executables"]["dol"]["sha256"])
    profile = profile.replace("private/self-build/retro-rewind/input", str(retro_root))
    profile = profile.replace("private/self-build/retro-rewind/mod", str(output / "mod"))
    profile = profile.replace("private/self-build/retro-rewind/payload.bin", str(payload))
    profile = profile.replace("0x800ED6E8", f"0x{hook:08X}")
    # The module's compatibility shadow must match the Japanese loader heap.
    # Runtime Error 429 checks the branch at 0x806013D4: its J target is
    # 0x80398D84 (link base + 0x124), not PAL's 0x80399404. Keep the actual
    # translated module at 0x81800000; only the original link view changes.
    link_base = map_address(0x803992E0, ranges)
    if link_base != 0x80398C60:
        raise BuildError("Japanese module link-base mapping changed")
    profile = profile.replace("module_link_base: 0x803992E0", "module_link_base: 0x80398C60")
    manifest = output / "retro.yml"
    manifest.write_text((output / "base.yml").read_text() + "\nprofiles:" + profile)
    return manifest


def rel_layout(image: bytes) -> tuple[list[tuple[int, int, bool]], list[dict]]:
    def word(offset):
        return struct.unpack_from(">I", image, offset)[0]
    count, table = word(0x0C), word(0x10)
    sections = []
    bss = ((len(image) + 0x3F) & ~0x1F)
    for index in range(count):
        offset, size = struct.unpack_from(">II", image, table + index * 8)
        executable = bool(offset & 1)
        offset &= ~1
        if not offset and size:
            offset = bss
            bss += size
        sections.append((offset, size, executable))
    relocations = []
    for entry in range(word(0x28), word(0x28) + word(0x2C), 8):
        module, cursor = struct.unpack_from(">II", image, entry)
        section = offset = 0
        while True:
            delta, kind, target_section, addend = struct.unpack_from(">HBBI", image, cursor)
            cursor += 8
            if kind == 203:
                break
            if kind == 202:
                section, offset = target_section, 0
                continue
            offset += delta
            if kind == 201:  # R_DOLPHIN_NOP: advances the relocation cursor only
                continue
            target = addend if module == 0 else REL_BASE + sections[target_section][0] + addend
            relocations.append({"address": REL_BASE + sections[section][0] + offset,
                                "target": target, "type": kind, "section": section})
    return sections, relocations


def prepare(repo: Path, data: Path, output: Path, runtime: Path) -> None:
    if not output.is_relative_to(repo / "private") or not runtime.is_relative_to(repo / "build"):
        raise BuildError("region development outputs must stay in private/ and build/")
    if (output / "host").exists():
        raise BuildError("region host staging output exists; choose a fresh output directory")
    profile = next(p for p in load_profiles(repo / "builder/profiles") if p.id == "mkwii-rmcj01-rev0")
    _validate_extraction(profile, data)
    config = profile.data["porting"]
    for key in ("addressMap", "sourceFunctionMap"):
        if sha256_file(repo / config[key]) != config[key + "SHA256"]:
            raise BuildError(f"pinned {key} changed")
    ranges = read_address_map((repo / config["addressMap"]).read_text(), "J")
    dol = read_dol_layout(data / "sys/main.dol")
    rel = (data / "files/rel/StaticR.rel").read_bytes()
    sections, relocations = rel_layout(rel)
    # These bounds are read from the supplied DOL/REL section tables, not a
    # extrapolation over a gap in Pulsar's code-address intervals.
    dol_ctors = next(s for s in dol["sections"] if s["index"] == 9)
    movie_table = {r["target"] for r in relocations if r["address"] in (0x80529742, 0x80529746)}
    if len(movie_table) != 1:
        raise BuildError("Japanese movie audio-system table relocation is ambiguous")
    exact = {
        0x80244DE0: dol_ctors["address"],
        0x80244EA0: dol_ctors["address"] + dol_ctors["size"],
        0x8088F400: REL_BASE + sections[2][0],
        0x8088F704: REL_BASE + sections[2][0] + sections[2][1],
        0x80399180: 0x80398B00,  # __init_registers lis/ori r1, checked below
        0x8088FDB8: movie_table.pop(),
    }
    dol_bytes = (data / "sys/main.dol").read_bytes()
    if dol_bytes[0x2384:0x238C] != bytes.fromhex("3c20803960218b00"):
        raise BuildError("Japanese startup stack/arena evidence changed")

    def port(address: int) -> int | None:
        return exact.get(address, map_address(address, ranges))

    executable_ranges = [(s["address"], s["address"] + s["size"]) for s in dol["sections"] if s["kind"] == "text"]
    executable_ranges += [(REL_BASE + offset, REL_BASE + offset + size) for offset, size, executable in sections if executable]
    def executable(address):
        return address % 4 == 0 and any(start <= address < end for start, end in executable_ranges)

    names = {}
    omitted = []
    for line in (repo / config["sourceFunctionMap"]).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        source, *name = line.split(maxsplit=1)
        source_address = int(source, 16)
        address = port(source_address)
        if address is not None and executable(address):
            names[address] = name[0] if name and not name[0].startswith("0x") else f"0x{address:08x}"
        else:
            omitted.append(line)
    seed_count = len(names)
    # Relocated function pointers (vtables, callbacks, constructors, switch
    # entries) supply Japanese-specific roots absent from the PAL map. Direct
    # calls from every seed are recursively discovered by WiiCompiled.
    for relocation in relocations:
        address = relocation["target"]
        if executable(address):
            names.setdefault(address, f"0x{address:08x}")
    for section in dol["sections"]:
        if section["kind"] == "text":
            continue
        for offset in range(section["offset"], section["offset"] + section["size"] - 3, 4):
            address = struct.unpack_from(">I", dol_bytes, offset)[0]
            if executable(address):
                names.setdefault(address, f"0x{address:08x}")

    output.mkdir(parents=True, exist_ok=True)
    marker = runtime / "kartpad-region-port.json"
    if marker.exists():
        raise BuildError("runtime source is already region-ported; prepare a fresh staged runtime")
    edits = []
    unknown = set()
    token = re.compile(r"(?<![0-9a-fA-F])(80[0-9a-fA-F]{6})(?![0-9a-fA-F])")

    def rewrite(source: str, path: str) -> str:
        def replace(match):
            value = int(match[1], 16)
            if value == 0x80808081:  # integer division multiplier, NOT a guest address
                return match[0]
            new = port(value)
            if new is None:
                unknown.add((path, match[0]))
                return match[0]
            if new != value:
                edits.append((path, match[0], f"{new:08X}"))
            return f"{new:08x}" if match[0].islower() else f"{new:08X}"
        return token.sub(replace, source).replace("524D4350", "524D434A").replace("524d4350", "524d434a").replace("RMCP", "RMCJ")

    pending = {}
    for directory in (runtime / "src", runtime / "include"):
        for path in sorted(directory.rglob("*")):
            if path.suffix in (".cpp", ".h", ".hpp", ".inc"):
                pending[path] = rewrite(path.read_text(), str(path.relative_to(runtime)))
    # Only symbols/literals in the game's fixed 0x80...... image are handled
    # above. MEM1/MEM2 bounds and MMIO constants outside that window stay intact.
    if unknown:
        raise BuildError(f"unreviewed runtime addresses: {sorted(unknown)}")
    sc = runtime / "src/hle/sc.cpp"
    pending[sc] = pending[sc].replace("constexpr uint32_t kPalProductRegion = 2;", "constexpr uint32_t kPalProductRegion = 0;")
    for path, source in pending.items():
        path.write_text(source)
    # Region-specific host sources stay private until the running port has
    # passed acceptance; the public PAL app is not loosened to accept J data.
    host = output / "host"
    shutil.copytree(repo / "apple", host / "apple")
    (host / "runtime").symlink_to(repo / "runtime", target_is_directory=True)
    (host / "cmake").symlink_to(repo / "cmake", target_is_directory=True)
    for path in (host / "apple").rglob("*"):
        if path.suffix not in (".mm", ".h", ".cpp"):
            continue
        source = rewrite(path.read_text(), str(path.relative_to(host)))
        source = source.replace("80d18895b39c63bd80f457398bfcbb91b7d16ac116a41a88967e954080155b05", profile.data["extraction"]["executables"]["dol"]["sha256"])
        source = source.replace("(PAL)", "(Japan)")
        path.write_text(source)
    for name in ("inject-g10-rkg-fixture-hook.py", "inject-online-rkg-selection-hooks.py", "inject-g10-camera-lifecycle-guard.py"):
        path = output / name
        source = rewrite((repo / "scripts" / name).read_text(), name)
        if name == "inject-online-rkg-selection-hooks.py":
            # SceneManager singleton: PAL 0x809C1E38 -> Japan 0x809C0E98.
            # The generated lis/addi expression keeps the high half in r4.
            source = source.replace("(r4 + 7736)", "(r4 + 3736)")
        path.write_text(source)
        path.chmod(0o755)
    if unknown:
        raise BuildError(f"unreviewed host/injector addresses: {sorted(unknown)}")
    (output / "MAP.txt").write_text("".join(f"{address:08x} {name}\n" for address, name in sorted(names.items())))
    # A separate development manifest never changes capabilities.build.
    manifest = (repo / "tools/mkwii-rmcp01-base.yml").read_text()
    manifest = manifest.replace("workspace_root: ..", f"workspace_root: {repo}")
    manifest = manifest.replace("rmcp01", "rmcj01").replace("RMCP01", "RMCJ01").replace("PAL", "Japan").replace("region: P", "region: J")
    manifest = manifest.replace("0x8038CC00", "0x8038C580").replace("0x8038EFA0", "0x8038E920").replace("0x805102E0", "0x8050FC60")
    pal = next(p for p in load_profiles(repo / "builder/profiles") if p.id == "mkwii-rmcp01-rev0")
    for name in ("dol", "rel"):
        manifest = manifest.replace(pal.data["extraction"]["executables"][name]["sha256"], profile.data["extraction"]["executables"][name]["sha256"])
    manifest = manifest.replace("private/self-build/disc", str(data)).replace("private/self-build/translation", str(output / "translation"))
    manifest = manifest.replace("ref/upstream/Wiicompiled/projects/mkwii/MAP.txt", str(output / "MAP.txt"))
    manifest = manifest.replace("build/wiicompiled-fpscr/runtime/src", str(runtime / "src"))
    (output / "base.yml").write_text(manifest)
    report = {"region": "J", "profileSHA256": profile.profile_sha256,
              "mappedExecutableSeeds": seed_count, "allExecutableSeeds": len(names),
              "omittedNonExecutableOrUnmappedPALSeeds": omitted,
              "sectionDerivedAddresses": {f"{key:08X}": f"{value:08X}" for key, value in exact.items()},
              "sourceEdits": edits, "runtimeVerified": False}
    marker.write_text(json.dumps(report, indent=2) + "\n")
    (output / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Prepared Japanese development translation: {len(names)} executable seeds, {len(edits)} source-token edits")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--retro-root", type=Path)
    parser.add_argument("--retro-payload", type=Path)
    args = parser.parse_args()
    if bool(args.retro_root) != bool(args.retro_payload):
        parser.error("--retro-root and --retro-payload must be supplied together")
    repo = Path(__file__).resolve().parents[2]
    prepare(repo, args.data.resolve(), args.output.resolve(), args.runtime.resolve())
    if args.retro_root:
        prepare_retro(repo, args.output.resolve(), args.retro_root.resolve(), args.retro_payload.resolve())


if __name__ == "__main__":
    main()
