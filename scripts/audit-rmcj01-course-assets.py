#!/usr/bin/env python3
"""Audit RMCJ01 retail and Retro Rewind course archives without extracting them.

The checker reads the supplied ``data/`` partition and the private
Retro Rewind 6.12.7 pack in place.  It never writes an archive member.  A
course archive is inspected as ``Yaz0/Yaz1 -> U8`` and the core files used by
the Mario Kart Wii course loader are checked (``course.kmp``, ``course.kcl``,
``course_model.brres`` and ``map_model.brres``).  The resulting report is a
static asset ledger; a passing archive is not a runtime/gameplay claim.

The implementation intentionally keeps the parser self contained.  The
format details follow the read-only references in ``ref/upstream/rr-pulsar``
(``Config.hpp``, ``CupsConfig.cpp`` and ``SlotExpansion.cpp``) and
``ref/upstream/mkw-sp`` (``U8Cursor``/``U8Iterator`` and ``WU8Library.cc``).
"""

from __future__ import annotations

import argparse
import copy
import datetime as _datetime
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


YAZ_MAGICS = (b"Yaz0", b"Yaz1")
U8_MAGIC = b"U\xaa8-"
PULS_MAGIC = b"PULS"
BMG_MAGIC = b"MESGbmg1"
KMP_MAGIC = b"RKMD"
BRES_MAGIC = b"bres"

# The game source's KMPHeader contains 15 section offsets.  These names are
# useful in reports and make the expected structure explicit without copying
# any game code or assets.
KMP_SECTION_NAMES = (
    "KTPT",
    "ENPT",
    "ENPH",
    "ITPT",
    "ITPH",
    "CKPT",
    "CKPH",
    "GOBJ",
    "POTI",
    "AREA",
    "CAME",
    "JGPT",
    "CNPT",
    "MSPT",
    "STGI",
)

# These are the files loaded by the retail CourseMgr/ArchiveMgr path.  The
# reference source also lists per-course decorative files, but those are not
# required to establish a loadable course archive and differ by course.
REQUIRED_COURSE_MEMBERS = (
    "course.kmp",
    "course.kcl",
    "course_model.brres",
    "map_model.brres",
)
# ``*_d.szs`` is the retail multiplayer archive.  The multiplayer loader
# reuses the base course model and only needs the course data plus the map
# model; absent ``course_model.brres`` in these archives is therefore an
# expected inherited member rather than an asset failure.
RETAIL_MULTIPLAYER_REQUIRED_MEMBERS = (
    "course.kmp",
    "course.kcl",
    "map_model.brres",
)
OPTIONAL_COURSE_MEMBERS = ("course.bmm", "course.btiEnv", "course.btiMat")

RETAIL_COURSES: tuple[dict[str, object], ...] = (
    # The order and course ids are CupsConfig::idToCourseId / CrashExtra's
    # GetVanillaTrackSzs mapping (Mushroom, Shell, Flower, Star, Special,
    # then the remaining cups).
    {"index": 0, "courseId": 0x08, "name": "Luigi Circuit", "archive": "beginner_course"},
    {"index": 1, "courseId": 0x01, "name": "Moo Moo Meadows", "archive": "farm_course"},
    {"index": 2, "courseId": 0x02, "name": "Mushroom Gorge", "archive": "kinoko_course"},
    {"index": 3, "courseId": 0x04, "name": "Toad's Factory", "archive": "factory_course"},
    {"index": 4, "courseId": 0x00, "name": "Mario Circuit", "archive": "castle_course"},
    {"index": 5, "courseId": 0x05, "name": "Coconut Mall", "archive": "shopping_course"},
    {"index": 6, "courseId": 0x06, "name": "DK Summit", "archive": "boardcross_course"},
    {"index": 7, "courseId": 0x07, "name": "Wario's Gold Mine", "archive": "truck_course"},
    {"index": 8, "courseId": 0x09, "name": "Daisy Circuit", "archive": "senior_course"},
    {"index": 9, "courseId": 0x0F, "name": "Koopa Cape", "archive": "water_course"},
    {"index": 10, "courseId": 0x0B, "name": "Maple Treeway", "archive": "treehouse_course"},
    {"index": 11, "courseId": 0x03, "name": "Grumble Volcano", "archive": "volcano_course"},
    {"index": 12, "courseId": 0x0E, "name": "Dry Dry Ruins", "archive": "desert_course"},
    {"index": 13, "courseId": 0x0A, "name": "Moonview Highway", "archive": "ridgehighway_course"},
    {"index": 14, "courseId": 0x0C, "name": "Bowser's Castle", "archive": "koopa_course"},
    {"index": 15, "courseId": 0x0D, "name": "Rainbow Road", "archive": "rainbow_course"},
    {"index": 16, "courseId": 0x10, "name": "GCN Peach Beach", "archive": "old_peach_gc"},
    {"index": 17, "courseId": 0x14, "name": "DS Yoshi Falls", "archive": "old_falls_ds"},
    {"index": 18, "courseId": 0x19, "name": "SNES Ghost Valley 2", "archive": "old_obake_sfc"},
    {"index": 19, "courseId": 0x1A, "name": "N64 Mario Raceway", "archive": "old_mario_64"},
    {"index": 20, "courseId": 0x1B, "name": "N64 Sherbet Land", "archive": "old_sherbet_64"},
    {"index": 21, "courseId": 0x1F, "name": "GBA Shy Guy Beach", "archive": "old_heyho_gba"},
    {"index": 22, "courseId": 0x17, "name": "DS Delfino Square", "archive": "old_town_ds"},
    {"index": 23, "courseId": 0x12, "name": "GCN Waluigi Stadium", "archive": "old_waluigi_gc"},
    {"index": 24, "courseId": 0x15, "name": "DS Desert Hills", "archive": "old_desert_ds"},
    {"index": 25, "courseId": 0x1E, "name": "GBA Bowser Castle 3", "archive": "old_koopa_gba"},
    {"index": 26, "courseId": 0x1D, "name": "N64 DK's Jungle Parkway", "archive": "old_donkey_64"},
    {"index": 27, "courseId": 0x11, "name": "GCN Mario Circuit", "archive": "old_mario_gc"},
    {"index": 28, "courseId": 0x18, "name": "SNES Mario Circuit 3", "archive": "old_mario_sfc"},
    {"index": 29, "courseId": 0x16, "name": "DS Peach Gardens", "archive": "old_garden_ds"},
    {"index": 30, "courseId": 0x13, "name": "GCN DK Mountain", "archive": "old_donkey_gc"},
    {"index": 31, "courseId": 0x1C, "name": "N64 Bowser's Castle", "archive": "old_koopa_64"},
)

RETAIL_BATTLE_COURSES: tuple[dict[str, object], ...] = (
    {"index": 0, "courseId": 0x20, "name": "Block Plaza", "archive": "block_battle"},
    {"index": 1, "courseId": 0x21, "name": "Delfino Pier", "archive": "venice_battle"},
    {"index": 2, "courseId": 0x22, "name": "Funky Stadium", "archive": "skate_battle"},
    {"index": 3, "courseId": 0x23, "name": "Chain Chomp Wheel", "archive": "casino_battle"},
    {"index": 4, "courseId": 0x24, "name": "Thwomp Desert", "archive": "sand_battle"},
    {"index": 5, "courseId": 0x25, "name": "GCN Cookie Land", "archive": "old_CookieLand_gc"},
    {"index": 6, "courseId": 0x26, "name": "DS Twilight House", "archive": "old_House_ds"},
    {"index": 7, "courseId": 0x27, "name": "SNES Battle Course 4", "archive": "old_battle4_sfc"},
    {"index": 8, "courseId": 0x28, "name": "GBA Battle Course 3", "archive": "old_battle3_gba"},
    {"index": 9, "courseId": 0x29, "name": "N64 Skyscraper", "archive": "old_matenro_64"},
)

# The two runs called out by the user are the only runtime passes that this
# ledger carries.  Everything else intentionally remains pending.
RETAIL_REPLAY_RUNTIME: Mapping[int, dict[str, str]] = {
    0x08: {
        "status": "verified_staff_replay",
        "evidence": "macbase native retail staff replay; Luigi Circuit course_id 8",
    },
    0x01: {
        "status": "verified_staff_replay",
        "evidence": "macbase native retail staff replay; Moo Moo Meadows course_id 1",
    },
}

# Additional native macOS evidence supplied by the coordinated acceptance
# run.  ConfigRT row 142 (`rMC1`, PULS id 0x18e) is the visible "SNES Mario
# Circuit 1" entry in the Retro Rewind 209-course list.  Keep this proof
# separate from the static archive result: it covers one staff-ghost replay,
# while a normally steered TT was only started/paused/restarted/quit.
RR_REPLAY_RUNTIME: Mapping[tuple[str, int], dict[str, object]] = {
    ("rr_retro", 142): {
        "status": "verified_staff_replay",
        "evidence": "macOS native Retro Rewind SNES Mario Circuit 1 staff ghost replay; 5 laps; finish stage 4",
        "trace": "private/rmcj01/retro/rr-snes-mario-circuit-1-replay-trace.csv",
        "traceSha256": "d001e97784ae13cde7bc6235d2b559e12654dd82f293e8006c090da515e0aaa1",
        "laps": 5,
        "finishStage": 4,
        "normalTimeTrial": "started_pause_restart_quit_without_natural_finish",
    },
}


class AuditError(ValueError):
    """Malformed local archive/config input."""


@dataclass(frozen=True)
class U8Member:
    path: str
    offset: int
    size: int


@dataclass(frozen=True)
class U8Archive:
    node_count: int
    data_offset: int
    members: Mapping[str, U8Member]


@dataclass(frozen=True)
class ConfigTrack:
    source: str
    config_name: str
    index: int
    cup_index: int
    row_index: int
    pulsar_id: int
    slot_id: int
    music_slot_id: int
    variant_count: int
    crc32: int
    filename: str | None
    variant_filenames: tuple[str | None, ...]


def _u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise AuditError(f"u16 out of range at 0x{offset:x}")
    return struct.unpack_from(">H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise AuditError(f"u32 out of range at 0x{offset:x}")
    return struct.unpack_from(">I", data, offset)[0]


def decode_yaz(data: bytes, *, max_output_size: int = 64 * 1024 * 1024) -> bytes:
    """Decode one Yaz0/Yaz1 stream with bounds checks."""

    if len(data) < 16 or data[:4] not in YAZ_MAGICS:
        raise AuditError("missing Yaz0/Yaz1 header")
    expanded_size = _u32(data, 4)
    if expanded_size <= 0:
        raise AuditError("Yaz expanded size is zero")
    if expanded_size > max_output_size:
        raise AuditError(f"Yaz expanded size exceeds {max_output_size} bytes")

    source = 16
    flags = 0
    mask = 0
    output = bytearray()
    while len(output) < expanded_size:
        if mask == 0:
            if source >= len(data):
                raise AuditError("truncated Yaz flag byte")
            flags = data[source]
            source += 1
            mask = 0x80
        if flags & mask:
            if source >= len(data):
                raise AuditError("truncated Yaz literal")
            output.append(data[source])
            source += 1
        else:
            if source + 2 > len(data):
                raise AuditError("truncated Yaz back-reference")
            value = _u16(data, source)
            source += 2
            distance = (value & 0x0FFF) + 1
            count = value >> 12
            if count:
                count += 2
            else:
                if source >= len(data):
                    raise AuditError("truncated Yaz extended run")
                count = data[source] + 18
                source += 1
            if distance > len(output):
                raise AuditError("Yaz back-reference precedes output")
            if len(output) + count > expanded_size:
                raise AuditError("Yaz run exceeds declared output size")
            # A back-reference may overlap the bytes being produced.  Copy
            # complete pattern chunks instead of appending one byte at a
            # time; this keeps a full-pack audit practical while preserving
            # Yaz0's overlapping-copy semantics.
            if count <= distance:
                start = len(output) - distance
                output.extend(output[start : start + count])
            else:
                pattern = bytes(output[-distance:])
                remaining = count
                while remaining:
                    take = min(distance, remaining)
                    output.extend(pattern[:take])
                    remaining -= take
        mask >>= 1
    return bytes(output)


def _u8_name(data: bytes, names_offset: int, name_offset: int) -> str:
    start = names_offset + name_offset
    if start < names_offset or start >= len(data):
        raise AuditError(f"U8 name offset out of range: 0x{name_offset:x}")
    end = data.find(b"\0", start)
    if end < 0:
        raise AuditError("U8 name is not NUL terminated")
    try:
        return data[start:end].decode("ascii")
    except UnicodeDecodeError as error:
        raise AuditError("U8 name is not ASCII") from error


def parse_u8(data: bytes) -> U8Archive:
    """Read U8 metadata and member ranges without exporting members."""

    if len(data) < 0x20 or data[:4] != U8_MAGIC:
        raise AuditError("missing U8 header")
    node_offset = _u32(data, 4)
    _meta_size = _u32(data, 8)  # retained for format visibility; see source refs
    data_offset = _u32(data, 0x0C)
    if node_offset < 0x20 or node_offset + 12 > len(data):
        raise AuditError("U8 node table offset is out of range")

    # The first node is an outer root.  Its size is the exclusive node index
    # of the table; this is the same convention used by mkw-sp's U8Iterator.
    root_type = data[node_offset]
    if root_type != 1:
        raise AuditError("U8 root node is not a directory")
    root_end = _u32(data, node_offset + 8)
    if root_end <= 1 or node_offset + root_end * 12 > len(data):
        raise AuditError("U8 root node count is out of range")
    names_offset = node_offset + root_end * 12
    if data_offset < names_offset or data_offset > len(data):
        raise AuditError("U8 data offset is out of range")

    members: dict[str, U8Member] = {}

    # U8 directory nodes are traversed as one linear table, not as a nested
    # tree.  The ``size``/``next_index`` field is the node index at which that
    # directory is popped from the iterator's stack.  Real Nintendo archives
    # can contain a child directory whose range extends past its parent (for
    # example RR's ``brasd/penguin_s`` subtree), so recursively parsing each
    # directory would revisit nodes and reject valid archives.  This mirrors
    # mkw-sp's U8Iterator exactly: pop directories at the current iteration,
    # then process each node once.
    dir_stack: list[tuple[str, int]] = []
    for index in range(root_end):
        while dir_stack and dir_stack[-1][1] <= index:
            dir_stack.pop()
        offset = node_offset + index * 12
        node_type = data[offset]
        name_offset = int.from_bytes(data[offset + 1 : offset + 4], "big")
        field_a = _u32(data, offset + 4)
        field_b = _u32(data, offset + 8)
        name = _u8_name(data, names_offset, name_offset)
        if node_type:
            next_index = field_b
            if next_index <= index or next_index > root_end:
                raise AuditError("U8 directory end index is out of range")
            dir_stack.append((name, next_index))
            continue

        prefix = "/".join(part for part, _ in dir_stack if part)
        member_path = "/".join(part for part in (prefix, name) if part).strip("/")
        # A number of Nintendo U8s wrap their files in a child directory
        # literally named '.'.  The runtime treats that as the archive root;
        # normalize it so both shapes expose the same member names.
        while member_path.startswith("./"):
            member_path = member_path[2:]
        if not member_path:
            raise AuditError("U8 file has an empty path")
        if field_a < data_offset or field_a + field_b > len(data):
            raise AuditError(f"U8 member {member_path} exceeds data area")
        if member_path in members:
            raise AuditError(f"duplicate U8 member: {member_path}")
        members[member_path] = U8Member(member_path, field_a, field_b)
    if not members:
        raise AuditError("U8 archive contains no files")
    return U8Archive(root_end, data_offset, members)


def _check_kmp(data: bytes) -> dict[str, object]:
    result: dict[str, object] = {
        "present": True,
        "magic": data[:4].decode("ascii", "replace") if len(data) >= 4 else None,
        "size": len(data),
        "valid": False,
        "issues": [],
    }
    issues: list[str] = result["issues"]  # type: ignore[assignment]
    if len(data) < 0x4C:
        issues.append("KMP shorter than 0x4c-byte header")
        return result
    if data[:4] != KMP_MAGIC:
        issues.append("KMP magic is not RKMD")
        return result
    declared_size = _u32(data, 4)
    section_count = _u16(data, 8)
    header_size = _u16(data, 0x0A)
    result.update(
        declaredSize=declared_size,
        sectionCount=section_count,
        headerSize=header_size,
    )
    if declared_size != len(data):
        issues.append(f"declared KMP size {declared_size} != member size {len(data)}")
    if section_count != len(KMP_SECTION_NAMES):
        issues.append(f"section count {section_count} != {len(KMP_SECTION_NAMES)}")
    if header_size < 0x4C or header_size > len(data):
        issues.append("KMP header size is out of range")
    offsets: list[int] = []
    if section_count >= len(KMP_SECTION_NAMES):
        for index in range(len(KMP_SECTION_NAMES)):
            # RKMD stores section offsets relative to the end of its 0x4c
            # byte header.  (The bytes at 0x0c are the first relative offset;
            # older declarations call this slot a version field.)
            relative = _u32(data, 0x10 + index * 4)
            value = header_size + relative
            offsets.append(value)
            if value < header_size or value >= len(data) or value % 4:
                issues.append(f"section {KMP_SECTION_NAMES[index]} offset 0x{value:x} is invalid")
            elif data[value : value + 4] != KMP_SECTION_NAMES[index].encode("ascii"):
                issues.append(f"section {KMP_SECTION_NAMES[index]} tag is missing at 0x{value:x}")
    result["sectionOffsets"] = offsets
    if not issues:
        result["valid"] = True
    return result


def _check_kcl(data: bytes) -> dict[str, object]:
    result: dict[str, object] = {
        "present": True,
        "size": len(data),
        "valid": False,
        "issues": [],
    }
    issues: list[str] = result["issues"]  # type: ignore[assignment]
    if len(data) < 0x3C:
        issues.append("KCL shorter than 0x3c-byte header")
        return result
    offsets = [_u32(data, index * 4) for index in range(4)]
    result["offsets"] = offsets
    if offsets[0] < 0x3C:
        issues.append("KCL vertex offset precedes header")
    if any(value >= len(data) for value in offsets):
        issues.append("KCL section offset exceeds member size")
    if offsets != sorted(offsets):
        issues.append("KCL section offsets are not monotonic")
    if not issues:
        result["valid"] = True
    return result


def _check_bres(data: bytes) -> dict[str, object]:
    return {
        "present": True,
        "size": len(data),
        "magic": data[:4].decode("ascii", "replace") if len(data) >= 4 else None,
        "valid": len(data) >= 4 and data[:4] == BRES_MAGIC,
        "issues": [] if len(data) >= 4 and data[:4] == BRES_MAGIC else ["BRRES magic is not bres"],
    }


def validate_archive(
    path: Path,
    *,
    display_path: str | None = None,
    required_members: Sequence[str] = REQUIRED_COURSE_MEMBERS,
    inherited_members: Sequence[str] = (),
) -> dict[str, object]:
    """Validate one SZS archive and return a JSON-ready static summary."""

    required_names = tuple(dict.fromkeys(required_members))
    inherited_names = tuple(name for name in dict.fromkeys(inherited_members) if name not in required_names)
    inspect_names = tuple(dict.fromkeys((*required_names, *inherited_names, *OPTIONAL_COURSE_MEMBERS)))

    base: dict[str, object] = {
        "path": display_path or path.as_posix(),
        "exists": path.is_file(),
        "status": "missing",
        "size": path.stat().st_size if path.is_file() else 0,
        "requiredMemberNames": list(required_names),
        "inheritedMemberNames": list(inherited_names),
    }
    # macOS volumes are commonly case-insensitive.  Preserve a case-only
    # spelling mismatch in the ledger so a configured source name (notably
    # ConfigBT's ``GCNBC``) remains distinguishable from the directory entry.
    try:
        case_matches = sorted(
            item.name
            for item in path.parent.iterdir()
            if item.is_file() and item.name.casefold() == path.name.casefold()
        )
    except OSError:
        case_matches = []
    if case_matches and path.name not in case_matches:
        base["caseInsensitiveMatches"] = case_matches
    if not path.is_file():
        # A case-folded hint is useful for the known ConfigBT GC*N* spelling
        # without silently treating a non-exact path as present.
        parent = path.parent
        base["caseInsensitiveMatches"] = case_matches
        base["issues"] = ["configured archive does not exist"]
        return base

    try:
        raw = path.read_bytes()
        base["sha256"] = hashlib.sha256(raw).hexdigest()
        base["yaz"] = {
            "magic": raw[:4].decode("ascii", "replace") if len(raw) >= 4 else None,
            "declaredExpandedSize": _u32(raw, 4) if len(raw) >= 8 else None,
            "valid": False,
        }
        expanded = decode_yaz(raw)
        base["yaz"]["valid"] = True  # type: ignore[index]
        base["yaz"]["expandedSize"] = len(expanded)  # type: ignore[index]
        u8 = parse_u8(expanded)
        base["u8"] = {
            "magic": U8_MAGIC.decode("ascii", "replace"),
            "nodeCount": u8.node_count,
            "memberCount": len(u8.members),
            "dataOffset": u8.data_offset,
        }
        # Member checks intentionally read only the requested ranges.  No
        # member is copied to an output path.
        required: dict[str, dict[str, object]] = {}
        optional: dict[str, dict[str, object]] = {}
        for member_name in inspect_names:
            member = u8.members.get(member_name)
            if member is None:
                if member_name in required_names:
                    target = required
                elif member_name in inherited_names:
                    target = base.setdefault("inheritedMembers", {})  # type: ignore[assignment]
                else:
                    target = optional
                target[member_name] = {
                    "present": False,
                    "size": 0,
                    "valid": False,
                    "issues": [
                        "member is absent from U8 archive"
                        if member_name not in inherited_names
                        else "member is inherited from the retail base archive"
                    ],
                }
                continue
            content = expanded[member.offset : member.offset + member.size]
            if member_name == "course.kmp":
                detail = _check_kmp(content)
            elif member_name == "course.kcl":
                detail = _check_kcl(content)
            elif member_name.endswith(".brres"):
                detail = _check_bres(content)
            else:
                detail = {"present": True, "size": len(content), "valid": len(content) > 0, "issues": []}
            if member_name in required_names:
                target = required
            elif member_name in inherited_names:
                target = base.setdefault("inheritedMembers", {})  # type: ignore[assignment]
            else:
                target = optional
            target[member_name] = detail
        base["requiredMembers"] = required
        base.setdefault("inheritedMembers", {})
        base["optionalMembers"] = optional
        issues = [
            f"{name}: {detail['issues']}"
            for name, detail in required.items()
            if not bool(detail.get("present")) or not bool(detail.get("valid"))
        ]
        base["issues"] = issues
        base["status"] = "pass" if not issues else "fail"
    except (OSError, AuditError, struct.error) as error:
        base["issues"] = [str(error)]
        base["status"] = "fail"
    return base


class _ArchiveCache:
    def __init__(self, display_root: Path | None = None) -> None:
        self._cache: dict[tuple[Path, tuple[str, ...], tuple[str, ...]], dict[str, object]] = {}
        self._display_root = display_root.resolve() if display_root else None

    def display(self, path: Path) -> str:
        if self._display_root:
            try:
                return path.resolve().relative_to(self._display_root).as_posix()
            except ValueError:
                pass
        return path.as_posix()

    def get(
        self,
        path: Path,
        *,
        required_members: Sequence[str] = REQUIRED_COURSE_MEMBERS,
        inherited_members: Sequence[str] = (),
    ) -> dict[str, object]:
        key = (path.resolve(), tuple(required_members), tuple(inherited_members))
        if key not in self._cache:
            self._cache[key] = validate_archive(
                path,
                display_path=self.display(path),
                required_members=required_members,
                inherited_members=inherited_members,
            )
        return self._cache[key]

    @property
    def reports(self) -> Mapping[tuple[Path, tuple[str, ...], tuple[str, ...]], dict[str, object]]:
        return self._cache


def _read_config_tracks(path: Path, source: str) -> tuple[list[ConfigTrack], dict[str, object]]:
    """Parse Config*.pul track rows and its FILE name table."""

    data = path.read_bytes()
    diagnostics: dict[str, object] = {
        "path": path.as_posix(),
        "bytes": len(data),
        "source": source,
        "issues": [],
    }
    issues: list[str] = diagnostics["issues"]  # type: ignore[assignment]
    if len(data) < 0x20 or data[:4] != PULS_MAGIC:
        raise AuditError(f"{path}: missing PULS header")
    version = _u32(data, 4)
    diagnostics["version"] = version
    if version != 3:
        issues.append(f"Config version {version} != 3")
    cups_offset = _u32(data, 0x0C)
    bmg_offset = _u32(data, 0x10)
    diagnostics["cupsOffset"] = cups_offset
    diagnostics["bmgOffset"] = bmg_offset
    if data[cups_offset : cups_offset + 4] != b"CUPS":
        raise AuditError(f"{path}: missing CUPS section")
    cup_count = _u16(data, cups_offset + 0x0C)
    track_count = cup_count * 4
    metadata_variant_count = _u32(data, cups_offset + 0x18)
    diagnostics.update(cupCount=cup_count, trackCount=track_count, metadataVariantCount=metadata_variant_count)
    track_table = cups_offset + 0x1C
    tracks_raw: list[tuple[int, int, int, int]] = []
    for index in range(track_count):
        offset = track_table + index * 8
        slot_id, music_slot_id, variant_count, crc32 = struct.unpack_from(">BBHI", data, offset)
        tracks_raw.append((slot_id, music_slot_id, variant_count, crc32))
    variant_sum = sum(row[2] for row in tracks_raw)
    diagnostics["variantCountSum"] = variant_sum
    if variant_sum != metadata_variant_count:
        issues.append(f"variant metadata {metadata_variant_count} != track sum {variant_sum}")
        # CupsConfig's combined constructor derives the runtime total from
        # CountSourceVariants(track.variantCount) rather than trusting this
        # raw metadata field.  Keep the mismatch visible, but classify it as
        # non-authoritative metadata instead of an archive failure.
        diagnostics["variantCountClassification"] = "non_authoritative_metadata_source_recomputes_track_sum"

    if data[bmg_offset : bmg_offset + 8] != BMG_MAGIC:
        raise AuditError(f"{path}: missing MESGbmg1 section")
    bmg_length = _u32(data, bmg_offset + 8)
    file_section_offset = bmg_offset + bmg_length
    diagnostics["bmgLength"] = bmg_length
    if file_section_offset > len(data):
        raise AuditError(f"{path}: BMG length exceeds file")
    tail = data[file_section_offset:]
    try:
        text = tail.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = tail.decode("latin-1")
    names: dict[tuple[int, int], str] = {}
    invalid_file_lines: list[str] = []
    file_line_count = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("FILE") or "=" not in line or "|" not in line:
            continue
        key_text, value_text = line.split("=", 1)
        try:
            key = int(key_text.strip(), 16)
        except ValueError:
            invalid_file_lines.append(line)
            continue
        file_line_count += 1
        raw_index = key & 0x0FFF
        variant_index = key >> 12
        value = value_text.split("|", 1)[0].strip()
        if raw_index >= track_count or variant_index > tracks_raw[raw_index][2]:
            invalid_file_lines.append(line)
            continue
        if not value:
            invalid_file_lines.append(line)
            continue
        names[(raw_index, variant_index)] = value
    diagnostics.update(fileLineCount=file_line_count, ignoredFileLines=invalid_file_lines)
    if invalid_file_lines:
        issues.append(f"ignored {len(invalid_file_lines)} FILE lines outside Config track/variant bounds")
        # Pulsar's FILE loader drops the same out-of-range keys; this is a
        # source-compatible diagnostic, not evidence of a missing archive.
        diagnostics["ignoredFileLinesClassification"] = "ignored_by_source_bounds_check"

    pulsar_base = 0x100
    if source == "rr_ct":
        pulsar_base += 172
    elif source == "rr_battle":
        pulsar_base += 172 + 132
    rows: list[ConfigTrack] = []
    for index, (slot_id, music_slot_id, variant_count, crc32) in enumerate(tracks_raw):
        rows.append(
            ConfigTrack(
                source=source,
                config_name=path.name,
                index=index,
                cup_index=index // 4,
                row_index=index % 4,
                pulsar_id=pulsar_base + index,
                slot_id=slot_id,
                music_slot_id=music_slot_id,
                variant_count=variant_count,
                crc32=crc32,
                filename=names.get((index, 0)),
                variant_filenames=tuple(names.get((index, variant)) for variant in range(1, variant_count + 1)),
            )
        )
    return rows, diagnostics


def _runtime_for_retail(course_id: int) -> dict[str, str]:
    return dict(RETAIL_REPLAY_RUNTIME.get(course_id, {"status": "pending", "evidence": "not exercised on macbase"}))


def _runtime_for_config(track: ConfigTrack) -> dict[str, object]:
    proof = RR_REPLAY_RUNTIME.get((track.source, track.index))
    if proof is not None:
        return copy.deepcopy(proof)
    return {"status": "pending", "evidence": "not exercised on macbase"}


def _retail_record(
    spec: Mapping[str, object], data_root: Path, cache: _ArchiveCache, *, battle: bool = False
) -> dict[str, object]:
    course_id = int(spec["courseId"])
    archive_stem = str(spec["archive"])
    base_path = data_root / "files/Race/Course" / f"{archive_stem}.szs"
    multiplayer_path = data_root / "files/Race/Course" / f"{archive_stem}_d.szs"
    base_report = cache.get(base_path)
    variants: list[dict[str, object]] = [
        {
            "variantIndex": 0,
            "kind": "retail_base",
            "filename": base_path.name,
            "staticValidation": base_report,
        }
    ]
    if multiplayer_path.is_file() or base_report.get("exists"):
        variants.append(
            {
                "variantIndex": "d",
                "kind": "retail_multiplayer_archive",
                "filename": multiplayer_path.name,
                "staticValidation": cache.get(
                    multiplayer_path,
                    required_members=RETAIL_MULTIPLAYER_REQUIRED_MEMBERS,
                    inherited_members=("course_model.brres",),
                ),
            }
        )
    static_statuses = [str(item["staticValidation"].get("status")) for item in variants]
    static_ok = all(status == "pass" for status in static_statuses)
    return {
        "source": "retail_battle10" if battle else "retail32",
        "name": spec["name"],
        "courseId": course_id,
        "retailIndex": int(spec["index"]),
        "pulsarId": course_id if battle else int(spec["index"]),
        "variants": variants,
        "staticValidation": {
            "status": "pass" if static_ok else "fail",
            "archiveCount": len(variants),
            "allRequiredMembersValid": static_ok,
        },
        "runtimeStatus": {"status": "pending", "evidence": "not exercised on macbase"}
        if battle
        else _runtime_for_retail(course_id),
    }


def _config_record(
    track: ConfigTrack,
    archive_dir: Path,
    cache: _ArchiveCache,
    diagnostics: Mapping[str, object],
) -> dict[str, object]:
    filenames = [track.filename, *track.variant_filenames]
    variants: list[dict[str, object]] = []
    for variant_index, filename in enumerate(filenames):
        if filename is None:
            variants.append(
                {
                    "variantIndex": variant_index,
                    "filename": None,
                    "staticValidation": {
                        "path": None,
                        "exists": False,
                        "status": "missing",
                        "issues": ["Config FILE section has no filename for this entry"],
                    },
                }
            )
            continue
        archive_path = archive_dir / f"{filename}.szs"
        variants.append(
            {
                "variantIndex": variant_index,
                "filename": f"{filename}.szs",
                "staticValidation": cache.get(archive_path),
            }
        )
    statuses = [str(item["staticValidation"].get("status")) for item in variants]
    static_status = "pass" if statuses and all(status == "pass" for status in statuses) else "fail"
    return {
        "source": track.source,
        "name": track.filename or f"<missing {track.index}>" ,
        "config": {
            "file": track.config_name,
            "index": track.index,
            "cupIndex": track.cup_index,
            "rowIndex": track.row_index,
            "pulsarId": track.pulsar_id,
            "slotId": track.slot_id,
            "musicSlotId": track.music_slot_id,
            "crc32": f"0x{track.crc32:08x}",
            "declaredVariantCount": track.variant_count,
        },
        "variants": variants,
        "staticValidation": {
            "status": static_status,
            "allConfiguredArchivesValid": static_status == "pass",
            "sourceDiagnostics": diagnostics["path"],
        },
        "runtimeStatus": _runtime_for_config(track),
    }


def _config_records(
    retro_root: Path, cache: _ArchiveCache
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    config_specs = (
        ("ConfigRT.pul", "rr_retro", retro_root / "Tracks"),
        ("ConfigCT.pul", "rr_ct", retro_root / "CT/Tracks"),
        ("ConfigBT.pul", "rr_battle", retro_root / "BT/Tracks"),
    )
    records: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for name, source, archive_dir in config_specs:
        config_path = retro_root / "Binaries" / name
        if not config_path.is_file():
            diagnostics.append({"path": cache.display(config_path), "source": source, "issues": ["missing Config*.pul"]})
            continue
        tracks, detail = _read_config_tracks(config_path, source)
        diagnostics.append(detail)
        for track in tracks:
            records.append(_config_record(track, archive_dir, cache, detail))
    return records, diagnostics


def _summary(records: Sequence[Mapping[str, object]], configs: Sequence[Mapping[str, object]], cache: _ArchiveCache) -> dict[str, object]:
    by_source: dict[str, dict[str, int]] = {}
    for record in records:
        source = str(record["source"])
        bucket = by_source.setdefault(source, {"courses": 0, "staticPass": 0, "staticFail": 0, "runtimePassed": 0, "runtimePending": 0})
        bucket["courses"] += 1
        if record.get("staticValidation", {}).get("status") == "pass":  # type: ignore[union-attr]
            bucket["staticPass"] += 1
        else:
            bucket["staticFail"] += 1
        runtime = record.get("runtimeStatus", {})
        if runtime.get("status") == "pending":  # type: ignore[union-attr]
            bucket["runtimePending"] += 1
        else:
            bucket["runtimePassed"] += 1
    archive_status = {"pass": 0, "fail": 0, "missing": 0}
    for report in cache.reports.values():
        status = str(report.get("status", "missing"))
        archive_status[status] = archive_status.get(status, 0) + 1
    config_issues = sum(len(detail.get("issues", [])) for detail in configs)
    return {
        "logicalCourses": len(records),
        "sourceBuckets": by_source,
        "uniqueArchives": len(cache.reports),
        "archiveStatus": archive_status,
        "configIssueCount": config_issues,
        "runtimePassed": sum(1 for record in records if record.get("runtimeStatus", {}).get("status") != "pending"),  # type: ignore[union-attr]
        "runtimePending": sum(1 for record in records if record.get("runtimeStatus", {}).get("status") == "pending"),  # type: ignore[union-attr]
        "staticIsNotRuntime": True,
    }


def audit_courses(
    data_root: Path,
    retro_root: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Build the complete retail/battle/RR static and runtime ledger."""

    display_root = repo_root or Path.cwd()
    cache = _ArchiveCache(display_root)
    records: list[dict[str, object]] = []
    for spec in RETAIL_COURSES:
        records.append(_retail_record(spec, data_root, cache))
    for spec in RETAIL_BATTLE_COURSES:
        records.append(_retail_record(spec, data_root, cache, battle=True))
    rr_records, config_diagnostics = _config_records(retro_root, cache)
    records.extend(rr_records)
    return {
        "schema": "kartpad.rmcj01.course-coverage/v1",
        "generatedAt": _datetime.date.today().isoformat(),
        "scope": {
            "dataRoot": data_root.as_posix(),
            "retroRoot": retro_root.as_posix(),
            "retailRaceCourses": 32,
            "retailBattleCourses": 10,
            "retroConfigFiles": ["ConfigRT.pul", "ConfigCT.pul", "ConfigBT.pul"],
            "runtimeBoundary": "Only macbase Luigi Circuit course_id 8 and Moo Moo Meadows course_id 1 staff replays are verified; all other runtimeStatus values remain pending.",
        },
        "inputPins": {
            "disc": "RMCJ01 revision 0",
            "sysMainDolSha256": "1b9621ef7c5d97dada103e50e5389730e67f3c2545dda592edd4b5843655af91",
            "relStaticRSha256": "88539012d357a1420724e51dc7e351192ce696da4b0045994895518a3fad6fae",
            "retroVersion": "6.12.7",
            "retroCodePulSha256": "3a1e60f6c94e435ff672167816dbe040d0f48874bfa093ada39e468655baef72",
        },
        "staticRules": {
            "outerFormat": "Yaz0/Yaz1 compressed U8",
            "requiredMembers": list(REQUIRED_COURSE_MEMBERS),
            "retailMultiplayerRequiredMembers": list(RETAIL_MULTIPLAYER_REQUIRED_MEMBERS),
            "retailMultiplayerInheritedMembers": ["course_model.brres"],
            "optionalMembers": list(OPTIONAL_COURSE_MEMBERS),
            "kmp": {"magic": "RKMD", "sectionCount": len(KMP_SECTION_NAMES), "headerSize": "0x4c"},
            "brresMagic": "bres",
            "sourceReferences": [
                "ref/upstream/rr-pulsar/PulsarEngine/Config.hpp",
                "ref/upstream/rr-pulsar/PulsarEngine/PulsarSystem.cpp",
                "ref/upstream/rr-pulsar/PulsarEngine/SlotExpansion/SlotExpansion.cpp",
                "ref/upstream/mkw-sp/payload/sp/U8Cursor.cc",
                "ref/upstream/mkw-sp/payload/sp/U8Iterator.cc",
                "ref/upstream/mkw-sp/payload/sp/WU8Library.cc",
            ],
        },
        "modeMatrix": mode_matrix(),
        "configDiagnostics": config_diagnostics,
        "summary": _summary(records, config_diagnostics, cache),
        "courses": records,
    }


def mode_matrix() -> list[dict[str, object]]:
    """Return a compact, explicit static-vs-runtime test plan."""

    return [
        {
            "scope": "original_single",
            "modes": ["Grand Prix 50/100/150cc", "Time Trial/staff replay", "VS race with CPU", "Battle with CPU"],
            "assetSet": "retail32 + retail_battle10",
            "staticValidation": "archive structure only",
            "runtimeStatus": "pending except two named retail staff replays",
        },
        {
            "scope": "original_local_multiplayer",
            "modes": ["VS race 2-4P", "Balloon Battle/Coin Runners 2-4P"],
            "assetSet": "retail32 + retail_battle10 + _d multiplayer archives",
            "staticValidation": "_d archive structure checked when present",
            "runtimeStatus": "pending",
        },
        {
            "scope": "retro_rewind_offline_single",
            "modes": ["RT/CT/BT cups", "150/200cc", "Feather/Item Rain variants where configured"],
            "assetSet": "ConfigRT + ConfigCT + ConfigBT and configured variants",
            "staticValidation": "Config IDs, FILE names, Yaz0/U8 and core members",
            "runtimeStatus": "pending",
        },
        {
            "scope": "retro_rewind_local_multiplayer",
            "modes": ["VS 2-4P", "Battle 2-4P", "variant selection"],
            "assetSet": "same RR configs; battle rows retain repeated IDs",
            "staticValidation": "same as offline; no run implied",
            "runtimeStatus": "pending",
        },
        {
            "scope": "online",
            "modes": [
                "public/private VS and Battle",
                "RR regional 0x0A retros",
                "0x0B OTT",
                "0x0C 200cc",
                "0x0D Item Rain",
                "0x0E RR Battle",
                "0x0F elimination",
                "0x14 CT",
                "0x15 RT",
            ],
            "assetSet": "RR config IDs and battle10/BT rows",
            "staticValidation": "asset/config checks do not exercise network",
            "runtimeStatus": "pending",
        },
    ]


def write_report(report: Mapping[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"), help="extracted RMCJ01 DATA root")
    parser.add_argument(
        "--retro-root",
        type=Path,
        default=Path("private/rmcj01/retro/pack/RetroRewind6"),
        help="private Retro Rewind 6.12.7 root",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("private/rmcj01/coverage/rmcj01-course-coverage.json"),
        help="new JSON ledger path (existing files are never overwritten)",
    )
    parser.add_argument("--print-summary", action="store_true", help="print compact counts after writing JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        report = audit_courses(args.data, args.retro_root, repo_root=Path.cwd())
        write_report(report, args.output)
        summary = report["summary"]
        print(f"wrote {report['schema']} to {args.output}")
        if args.print_summary:
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, AuditError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
