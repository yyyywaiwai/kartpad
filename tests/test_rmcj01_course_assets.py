"""Focused tests for the local RMCJ01/RR course archive audit.

The fixtures below are tiny synthetic Yaz0/U8 archives.  They exercise the
format guards without copying any game asset out of ``data/`` or the private
Retro Rewind pack.  Two optional regression checks open the real nested U8
archives in place when the local fixture tree is present.
"""

from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/audit-rmcj01-course-assets.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_rmcj01_course_assets", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolves the module through sys.modules while constructing
    # ConfigTrack, so register the dynamically loaded module first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_audit_module()


def _align(value: int, alignment: int = 0x20) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _literal_yaz(payload: bytes, magic: bytes = b"Yaz0") -> bytes:
    """Encode a small all-literal Yaz0 stream for parser tests."""

    body = bytearray()
    for start in range(0, len(payload), 8):
        chunk = payload[start : start + 8]
        body.append(0xFF)
        body.extend(chunk)
    return magic + struct.pack(">I", len(payload)) + bytes(8) + bytes(body)


def _minimal_kmp() -> bytes:
    tags = getattr(AUDIT, "KMP_SECTION_NAMES")
    header_size = 0x4C
    payload = b"".join(tag.encode("ascii") for tag in tags)
    out = bytearray(header_size + len(payload))
    out[:4] = b"RKMD"
    struct.pack_into(">I", out, 4, len(out))
    struct.pack_into(">HH", out, 8, len(tags), header_size)
    for index in range(len(tags)):
        struct.pack_into(">I", out, 0x10 + index * 4, index * 4)
    out[header_size:] = payload
    return bytes(out)


def _minimal_kcl() -> bytes:
    # Four monotonic section offsets, each inside this tiny member.
    out = bytearray(0x4C)
    for index, offset in enumerate((0x3C, 0x40, 0x44, 0x48)):
        struct.pack_into(">I", out, index * 4, offset)
    return bytes(out)


def _minimal_u8(files: dict[str, bytes]) -> bytes:
    """Build a compact U8 archive with files directly below the root."""

    names = bytearray(b"\0")
    name_offsets: dict[str, int] = {}
    for name in files:
        name_offsets[name] = len(names)
        names.extend(name.encode("ascii"))
        names.append(0)

    node_count = 1 + len(files)
    node_offset = 0x20
    names_offset = node_offset + node_count * 12
    data_offset = _align(names_offset + len(names))
    nodes = bytearray()
    # Outer root: directory flag, empty name, and exclusive node index.
    nodes.extend(bytes((1, 0, 0, 0)))
    nodes.extend(struct.pack(">II", 0, node_count))
    data_cursor = data_offset
    file_nodes: list[tuple[int, int, int]] = []
    for name, content in files.items():
        data_cursor = _align(data_cursor)
        file_nodes.append((name_offsets[name], data_cursor, len(content)))
        data_cursor += len(content)
    for name_offset, file_offset, size in file_nodes:
        nodes.extend(bytes((0,)) + name_offset.to_bytes(3, "big"))
        nodes.extend(struct.pack(">II", file_offset, size))

    header = b"U\xAA8-" + struct.pack(">III", node_offset, data_offset - node_offset, data_offset) + bytes(0x10)
    out = bytearray(header)
    out.extend(nodes)
    out.extend(names)
    out.extend(bytes(data_offset - len(out)))
    for (_, file_offset, _), (_, content) in zip(file_nodes, files.items()):
        out.extend(bytes(file_offset - len(out)))
        out.extend(content)
    return bytes(out)


def _minimal_course_archive(*, include_model: bool = True) -> bytes:
    members = {
        "course.kmp": _minimal_kmp(),
        "course.kcl": _minimal_kcl(),
        "map_model.brres": b"bres\0map",
    }
    if include_model:
        members["course_model.brres"] = b"bres\0course"
    return _literal_yaz(_minimal_u8(members))


class Rmcj01CourseAssetTests(unittest.TestCase):
    def test_yaz_literal_round_trip(self) -> None:
        payload = b"RMCJ01 synthetic Yaz0 fixture" * 3
        self.assertEqual(AUDIT.decode_yaz(_literal_yaz(payload)), payload)
        self.assertEqual(AUDIT.decode_yaz(_literal_yaz(payload, magic=b"Yaz1")), payload)

    def test_u8_member_paths_and_metadata(self) -> None:
        expanded = _minimal_u8({"course.kmp": b"kmp", "map_model.brres": b"bres"})
        archive = AUDIT.parse_u8(expanded)
        self.assertEqual(archive.node_count, 3)
        self.assertEqual(set(archive.members), {"course.kmp", "map_model.brres"})
        self.assertGreaterEqual(archive.data_offset, 0x20)

    def test_validate_archive_core_members(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.szs"
            path.write_bytes(_minimal_course_archive())
            report = AUDIT.validate_archive(path)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(set(report["requiredMemberNames"]), set(AUDIT.REQUIRED_COURSE_MEMBERS))
        self.assertTrue(all(detail["valid"] for detail in report["requiredMembers"].values()))

    def test_retail_multiplayer_inherits_course_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_d.szs"
            path.write_bytes(_minimal_course_archive(include_model=False))
            strict = AUDIT.validate_archive(path)
            multiplayer = AUDIT.validate_archive(
                path,
                required_members=AUDIT.RETAIL_MULTIPLAYER_REQUIRED_MEMBERS,
                inherited_members=("course_model.brres",),
            )
        self.assertEqual(strict["status"], "fail")
        self.assertEqual(multiplayer["status"], "pass")
        self.assertFalse(multiplayer["inheritedMembers"]["course_model.brres"]["present"])

    def test_rr_snes_mario_circuit_runtime_proof_mapping(self) -> None:
        track = AUDIT.ConfigTrack(
            source="rr_retro",
            config_name="ConfigRT.pul",
            index=142,
            cup_index=35,
            row_index=2,
            pulsar_id=0x18E,
            slot_id=24,
            music_slot_id=24,
            variant_count=0,
            crc32=0,
            filename="rMC1",
            variant_filenames=(),
        )
        runtime = AUDIT._runtime_for_config(track)
        self.assertEqual(runtime["status"], "verified_staff_replay")
        self.assertEqual(runtime["laps"], 5)
        self.assertEqual(runtime["finishStage"], 4)

    def test_real_nested_rr_archives(self) -> None:
        paths = (
            REPO_ROOT / "private/rmcj01/retro/pack/RetroRewind6/Tracks/48.szs",
            REPO_ROOT / "private/rmcj01/retro/pack/RetroRewind6/CT/Tracks/Z84.szs",
        )
        if not all(path.is_file() for path in paths):
            self.skipTest("private Retro Rewind pack is not present")
        for path in paths:
            with self.subTest(path=path.name):
                report = AUDIT.validate_archive(path)
                self.assertEqual(report["status"], "pass")
                self.assertIn("course.kmp", report["requiredMembers"])


if __name__ == "__main__":
    unittest.main()
