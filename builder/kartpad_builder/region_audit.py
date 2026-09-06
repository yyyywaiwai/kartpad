"""Read-only evidence for a region port; mapping coverage is not execution proof.

Pulsar's versions.txt describes selected address intervals, not a complete
binary equivalence map. Never extrapolate across its gaps, and never use this
report as a replacement for a validated translator/runtime profile.
"""
from __future__ import annotations

import hashlib
import re
import struct
from dataclasses import dataclass
from pathlib import Path

from .errors import BuildError
from .pipeline import _validate_extraction
from .profiles import Profile, sha256_file


@dataclass(frozen=True)
class AddressRange:
    start: int
    end: int
    delta: int


def read_address_map(text: str, region: str) -> list[AddressRange]:
    ranges: list[AddressRange] = []
    selected = False
    found = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            selected = line == f"[{region}]"
            found |= selected
            continue
        if not selected:
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{8})-([0-9a-fA-F]{8}|\*):\s*([+-]0x[0-9a-fA-F]+)", line)
        if match is None:
            raise BuildError(f"unsupported address-map directive for {region}: {line}")
        start, end, delta = match.groups()
        item = AddressRange(int(start, 16), 0xFFFFFFFF if end == "*" else int(end, 16), int(delta, 16))
        if item.start > item.end or not (0 <= item.start + item.delta <= item.end + item.delta <= 0xFFFFFFFF):
            raise BuildError(f"invalid address-map range: {line}")
        ranges.append(item)
    if not found or not ranges:
        raise BuildError(f"no address-map ranges for region {region}")
    ranges.sort(key=lambda item: item.start)
    for left, right in zip(ranges, ranges[1:]):
        if left.end >= right.start:
            raise BuildError("overlapping address-map ranges")
    return ranges


def map_address(address: int, ranges: list[AddressRange]) -> int | None:
    for item in ranges:
        if item.start <= address <= item.end:
            return address + item.delta
    return None


def read_dol_layout(path: Path) -> dict:
    image = path.read_bytes()
    if len(image) < 0x100:
        raise BuildError("truncated DOL header")
    words = struct.unpack_from(">64I", image)
    sections = []
    for index in range(18):
        offset, address, size = words[index], words[18 + index], words[36 + index]
        if size == 0:
            continue
        if offset < 0x100 or offset + size > len(image) or address + size > 0x100000000:
            raise BuildError(f"invalid DOL section {index}")
        sections.append({"index": index, "kind": "text" if index < 7 else "data",
                         "offset": offset, "address": address, "size": size})
    entry = words[56]
    if not any(s["kind"] == "text" and s["address"] <= entry < s["address"] + s["size"] for s in sections):
        raise BuildError("DOL entry point is outside executable sections")

    # The retail startup initializes r2/r13 using lis+ori. Require one matching
    # pair per register in the startup neighborhood instead of guessing a delta.
    registers: dict[str, str] = {}
    for register, key in ((2, "sda2Base"), (13, "sdaBase")):
        matches: set[int] = set()
        for section in sections:
            if section["kind"] != "text":
                continue
            lower = max(section["address"], entry)
            upper = min(section["address"] + section["size"] - 4, entry + 0x400)
            for address in range(lower, upper, 4):
                offset = section["offset"] + address - section["address"]
                hi, lo = struct.unpack_from(">II", image, offset)
                if hi >> 16 == (0x3C00 | register << 5) and lo >> 16 == (0x6000 | register << 5 | register):
                    matches.add(((hi & 0xFFFF) << 16) | (lo & 0xFFFF))
        if len(matches) != 1:
            raise BuildError(f"DOL startup does not identify a unique {key}")
        registers[key] = f"0x{matches.pop():08X}"
    return {"entryPoint": f"0x{entry:08X}", **registers, "sections": sections}


def audit_region(repo: Path, profile: Profile, extraction: Path) -> dict:
    _validate_extraction(profile, extraction)
    config = profile.data.get("porting")
    if not config:
        raise BuildError(f"{profile.id} has no region-port audit configuration")
    inputs = {}
    for key in ("addressMap", "sourceFunctionMap"):
        path = repo / config[key]
        if not path.is_file():
            raise BuildError(f"missing pinned porting input: {path}")
        if sha256_file(path) != config[key + "SHA256"]:
            raise BuildError(f"porting input hash mismatch: {key}")
        inputs[key] = path
    ranges = read_address_map(inputs["addressMap"].read_text(), profile.data["game"]["region"])
    dol = read_dol_layout(extraction / profile.data["extraction"]["executables"]["dol"]["path"])
    translation = profile.data["translation"]
    for key in ("sdaBase", "sda2Base"):
        if int(dol[key], 16) != int(translation[key], 16):
            raise BuildError(f"DOL startup {key} does not match profile")
    if int(dol["entryPoint"], 16) not in [int(entry, 16) for entry in translation["entryPoints"]]:
        raise BuildError("DOL entry point does not match profile")

    mapped = 0
    missing = []
    destinations: dict[int, int] = {}
    collisions = []
    for raw in inputs["sourceFunctionMap"].read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        value, *name = line.split(maxsplit=1)
        address = int(value, 16)
        destination = map_address(address, ranges)
        if destination is None:
            missing.append({"sourceAddress": f"0x{address:08X}", "symbol": name[0] if name else ""})
        else:
            mapped += 1
            if destination in destinations and destinations[destination] != address:
                collisions.append({"destination": f"0x{destination:08X}",
                                   "sources": [f"0x{destinations[destination]:08X}", f"0x{address:08X}"]})
            destinations[destination] = address

    runtime = repo / "ref/upstream/Wiicompiled/runtime"
    if not (runtime / "src").is_dir():
        raise BuildError("missing pinned WiiCompiled runtime source")
    native_entries = []
    unmapped_literals: dict[int, list[str]] = {}
    pattern = re.compile(
        r"\b(?:REGISTER_(?:NATIVE|TRANSLATED)_FUNCTION(?:_AS)?\s*\(\s*0x|"
        r"PPC_NATIVE_OVERRIDE(?:_VOID)?\s*\(\s*|GX_FATAL_STUB\s*\(\s*)([0-9a-fA-F]{8})(?![0-9a-fA-F])"
    )
    source_digest = hashlib.sha256()
    paths = sorted(path for directory in (runtime / "src", runtime / "include") for path in directory.rglob("*"))
    for path in paths:
        if not path.is_file() or path.suffix not in (".cpp", ".h", ".hpp"):
            continue
        relative = str(path.relative_to(repo))
        source = path.read_text()
        source_digest.update(relative.encode() + b"\0" + path.read_bytes() + b"\0")
        for match in pattern.finditer(source):
            number = source.count("\n", 0, match.start()) + 1
            address = int(match[1], 16)
            destination = map_address(address, ranges)
            native_entries.append({"source": f"{relative}:{number}",
                                   "sourceAddress": f"0x{address:08X}",
                                   "candidateAddress": f"0x{destination:08X}" if destination is not None else None})
        for number, line in enumerate(source.splitlines(), 1):
            # Intentionally a review inventory: this also finds masks/constants
            # and comments. It must never be used for blind search-and-replace.
            for value in re.findall(r"\b0x(80[0-9a-fA-F]{6})(?![0-9a-fA-F])", line):
                address = int(value, 16)
                if map_address(address, ranges) is None:
                    unmapped_literals.setdefault(address, []).append(f"{relative}:{number}")

    summary = {"profileId": profile.id, "status": profile.status,
               "buildEnabled": profile.build_enabled, "extractedDataValidated": True,
               "sourceMapEntries": mapped + len(missing), "entriesWithCandidateMapping": mapped,
               "unmappedMapEntries": len(missing), "mappingCollisions": len(collisions),
               "nativeRegistrations": len(native_entries),
               "nativeRegistrationAddresses": len({entry["sourceAddress"] for entry in native_entries}),
               "nativeRegistrationsWithoutMapping": sum(entry["candidateAddress"] is None for entry in native_entries),
               "unmappedRuntimeLiteralValues": len(unmapped_literals),
               "runtimeExecutionVerified": False}
    return {"schemaVersion": 1, "summary": summary,
            "profileSHA256": profile.profile_sha256,
            "runtimeSourceSHA256": source_digest.hexdigest(),
            "inputs": {key: {"path": config[key], "sha256": config[key + "SHA256"]} for key in inputs},
            "dol": dol, "unmappedMapEntries": missing, "mappingCollisions": collisions,
            "nativeRegistrationCandidates": native_entries,
            "unmappedRuntimeLiteralsForReview": [{"value": f"0x{address:08X}", "locations": locations}
                                                for address, locations in sorted(unmapped_literals.items())],
            "limitations": ["Interval coverage is not proof of equivalent function bodies or ABI.",
                            "Unmapped entries are never copied from PAL or assigned an extrapolated address.",
                            "Literal inventory includes non-address constants and comments; review manually.",
                            "This audit does not enable translation, IPA packaging, Retro Rewind, or gameplay."]}
