from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kartpad_builder.cli import main
from kartpad_builder.errors import BuildError
from kartpad_builder.pipeline import _validate_extraction, build, extract, translate, write_translator_manifest
from kartpad_builder.profiles import Profile, ProfileError, load_profiles, select_profile, validate_profile
from kartpad_builder.region_audit import AddressRange, audit_region, map_address, read_address_map, read_dol_layout
from kartpad_builder.rmcj01 import JAPAN_WFC_PAYLOAD_SHA256, REL_BASE, rel_layout, prepare_retro
from kartpad_builder.retro_rewind import validate_rwfc_payload


REPO = Path(__file__).resolve().parents[1]
PROFILES = REPO / "builder/profiles"


def japan_profile() -> Profile:
    return next(profile for profile in load_profiles(PROFILES) if profile.id == "mkwii-rmcj01-rev0")


def fixture(root: Path) -> tuple[Profile, Path, Path]:
    data = copy.deepcopy(japan_profile().data)
    extraction = root / "DATA with spaces"
    for name in data["extraction"]["requiredFiles"]:
        path = extraction / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fixture " + name.encode())
    boot = bytearray(0x440)
    boot[:8] = b"RMCJ01\0\0"
    boot[24:28] = bytes.fromhex("5d1c9ea3")
    (extraction / "sys/boot.bin").write_bytes(boot)
    for exe in data["extraction"]["executables"].values():
        exe["sha256"] = hashlib.sha256((extraction / exe["path"]).read_bytes()).hexdigest()
    image = root / "MarioKartWii [RMCJ01].iso"
    image.write_bytes(boot + b"fixture image")
    data["containers"]["acceptedImages"] = [{"format": "iso", "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}]
    profiles = root / "profiles"
    profiles.mkdir()
    path = profiles / "japan.json"
    path.write_text(json.dumps(data))
    return Profile(path, data), image, extraction


class JapaneseProfileTests(unittest.TestCase):
    def test_japanese_production_payload_signature_and_tamper_detection(self):
        payload = REPO / "private/rmcj01/retro/RMCJD00-payload.bin"
        if not payload.is_file():
            self.skipTest("private Japanese production payload is not cached")
        config = {"bytes": 28992, "sha256": JAPAN_WFC_PAYLOAD_SHA256}
        validate_rwfc_payload(payload, config)
        with tempfile.TemporaryDirectory() as temp:
            tampered = Path(temp) / "payload.bin"
            image = bytearray(payload.read_bytes())
            image[-1] ^= 1
            tampered.write_bytes(image)
            changed = dict(config, sha256=hashlib.sha256(image).hexdigest())
            with self.assertRaisesRegex(BuildError, "signature"):
                validate_rwfc_payload(tampered, changed)

    def test_retro_preparation_rejects_outputs_outside_private(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            with self.assertRaisesRegex(BuildError, "stay in private"):
                prepare_retro(repo, repo / "public", repo / "pack", repo / "payload")

    def test_retro_preparation_rejects_a_pal_base_before_reading_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            output = repo / "private/port"
            output.mkdir(parents=True)
            (output / "preparation.json").write_text('{"region":"P"}')
            with self.assertRaisesRegex(BuildError, "prepared Japanese base"):
                prepare_retro(repo, output, repo / "missing-pack", repo / "missing-payload")
            self.assertFalse((output / "retro.yml").exists())

    def test_ios_build_isolated_from_public_pal_and_other_generated_links(self):
        script = (REPO / "scripts/build-rmcj01-ios.sh").read_text()
        self.assertIn('runtime="$repo/build/rmcj01-$tag/runtime"', script)
        self.assertIn("dev.kartpad.rmcj01.ios", script)
        self.assertIn('KARTPAD_IOS_AUDIT_REGION=J', script)
        self.assertIn("Translation SDA bases are not Japanese", script)
        public_plist = (REPO / "apple/ios/RuntimeInfo.plist").read_text()
        self.assertIn("$(PRODUCT_BUNDLE_IDENTIFIER)", public_plist)
        integration = (REPO / "patches/wiicompiled-ios-app-integration.patch").read_text()
        self.assertIn("XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER dev.kartpad.app", integration)
        self.assertNotIn("dev.kartpad.rmcj01.ios", public_plist)

    def test_ios_audit_keeps_pal_default_and_checks_exact_japanese_dol(self):
        script = (REPO / "scripts/audit-ios-game-app.sh").read_text()
        self.assertIn('${KARTPAD_IOS_AUDIT_REGION:-P}', script)
        self.assertIn(japan_profile().data["extraction"]["executables"]["dol"]["sha256"], script)
        self.assertIn("Japanese app retains the PAL importer contract", script)

    def test_japanese_retro_link_view_matches_the_observed_branch_contract(self):
        # J Code.pul checks this actual branch before entering its title scene.
        # Keeping PAL's shadow base produced Error 429 at runtime.
        callsite, module_offset = 0x806013D4, 0x124
        branch = lambda base: 0x48000000 | ((base + module_offset - callsite) & 0x03FFFFFC)
        self.assertEqual(branch(0x80398C60), 0x4BD979B0)
        self.assertEqual(branch(0x803992E0), 0x4BD98030)
        preparer = (REPO / "builder/kartpad_builder/rmcj01.py").read_text()
        self.assertIn('module_link_base: 0x80398C60', preparer)

    def test_exact_japanese_iso_selects_its_own_profile(self):
        profile = japan_profile()
        selected = select_profile(load_profiles(PROFILES), "78cb026411171d531bfbfa60e5e2d8ee94d73e855551de1c23d7231f34b8733a")
        self.assertEqual(selected.id, profile.id)
        self.assertEqual(profile.data["game"]["region"], "J")
        self.assertEqual(profile.status, "macos-development")
        self.assertFalse(profile.build_enabled)
        self.assertIsNone(profile.data["translation"]["functionMap"])
        self.assertNotIn("retroRewind", profile.data)

    def test_pal_stays_build_enabled_and_separate(self):
        profile = next(p for p in load_profiles(PROFILES) if p.id == "mkwii-rmcp01-rev0")
        self.assertTrue(profile.build_enabled)
        with self.assertRaisesRegex(ProfileError, "does not match"):
            select_profile(load_profiles(PROFILES), japan_profile().accepted_images[0]["sha256"], profile.id)

    def test_incomplete_port_cannot_be_enabled_with_unknown_translation_counts(self):
        data = copy.deepcopy(japan_profile().data)
        data["capabilities"]["build"] = True
        with self.assertRaisesRegex(ProfileError, "function map"):
            validate_profile(data)
        data["translation"]["functionMap"] = "candidate.map"
        with self.assertRaisesRegex(ProfileError, "non-negative integer"):
            validate_profile(data)

    def test_capabilities_cannot_use_truthy_strings(self):
        data = copy.deepcopy(japan_profile().data)
        data["capabilities"]["build"] = "false"
        with self.assertRaisesRegex(ProfileError, "must be bool"):
            validate_profile(data)

    def test_region_must_match_disc_identity(self):
        data = copy.deepcopy(japan_profile().data)
        data["game"]["region"] = "P"
        with self.assertRaisesRegex(ProfileError, "region"):
            validate_profile(data)

    def test_direct_build_and_translation_entrypoints_are_gated_before_side_effects(self):
        profile = japan_profile()
        with tempfile.TemporaryDirectory() as temp, patch("kartpad_builder.pipeline.run") as run:
            root = Path(temp)
            calls = [
                lambda: build(root, profile, root / "image", "0" * 64, root / "out.ipa", root / "work", app_override=root / "existing.app"),
                lambda: translate(profile, root, root / "data", root / "translation", 2, None),
                lambda: write_translator_manifest(profile, root, root / "data", root / "translation", root / "out.yml", None, root / "mod"),
            ]
            for call in calls:
                with self.assertRaisesRegex(ProfileError, "not build-enabled"):
                    call()
            run.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])

    def test_reuse_needs_no_extractor_and_does_not_change_data(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, image, data = fixture(Path(temp))
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in data.rglob("*") if p.is_file()}
            with patch("kartpad_builder.pipeline.run") as run, contextlib.redirect_stdout(io.StringIO()):
                extract(profile, image, data)
                run.assert_not_called()
            after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in data.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_wrong_disc_revision_and_magic_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, _, data = fixture(Path(temp))
            boot = data / "sys/boot.bin"
            original = boot.read_bytes()
            for offset, value in ((3, ord("P")), (6, 1), (7, 1), (24, 0)):
                changed = bytearray(original)
                changed[offset] = value
                boot.write_bytes(changed)
                with self.assertRaisesRegex(BuildError, "identity"):
                    _validate_extraction(profile, data)

    def test_both_executable_hashes_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, _, data = fixture(Path(temp))
            for name, exe in profile.data["extraction"]["executables"].items():
                path = data / exe["path"]
                original = path.read_bytes()
                path.write_bytes(original + b"tamper")
                with self.assertRaisesRegex(BuildError, f"extracted {name}"):
                    _validate_extraction(profile, data)
                path.write_bytes(original)

    def test_missing_required_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, _, data = fixture(Path(temp))
            (data / "sys/fst.bin").unlink()
            with self.assertRaisesRegex(BuildError, "missing sys/fst.bin"):
                _validate_extraction(profile, data)

    def test_cli_inspect_and_prepare_accept_existing_partition(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, image, data = fixture(Path(temp))
            for command in ("inspect", "prepare"):
                output = io.StringIO()
                with contextlib.redirect_stdout(output), patch("kartpad_builder.cli.prepare_dependencies") as deps:
                    code = main(["--profiles-dir", str(profile.path.parent), command, str(image), "--extracted-data", str(data)])
                self.assertEqual(code, 0)
                self.assertFalse(json.loads(output.getvalue())["buildEnabled"])
                deps.assert_not_called()

    def test_cli_build_fails_before_dependency_download(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, image, data = fixture(Path(temp))
            error = io.StringIO()
            with contextlib.redirect_stderr(error), patch("kartpad_builder.cli.prepare_dependencies") as deps:
                code = main(["--profiles-dir", str(profile.path.parent), "build", str(image), "--extracted-data", str(data)])
            self.assertEqual(code, 1)
            self.assertIn("not build-enabled", error.getvalue())
            deps.assert_not_called()

    def test_prepare_rejects_conflicting_output(self):
        with tempfile.TemporaryDirectory() as temp:
            profile, image, data = fixture(Path(temp))
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["--profiles-dir", str(profile.path.parent), "prepare", str(image), "--extracted-data", str(data), "--output", str(Path(temp) / "new")])
            self.assertEqual(code, 1)
            self.assertFalse((Path(temp) / "new").exists())


class RegionMapTests(unittest.TestCase):
    def test_japanese_rel_relocation_and_constructor_evidence(self):
        path = REPO / "data/files/rel/StaticR.rel"
        if not path.is_file():
            self.skipTest("user-supplied Japanese REL is absent")
        sections, relocations = rel_layout(path.read_bytes())
        self.assertEqual(REL_BASE + sections[1][0], 0x8050FD34)
        self.assertEqual(REL_BASE + sections[2][0], 0x8088EA6C)
        self.assertEqual(REL_BASE + sections[2][0] + sections[2][1], 0x8088ED70)
        self.assertEqual(REL_BASE + sections[6][0], 0x809BC740)
        targets = {r["target"] for r in relocations}
        self.assertIn(0x805CBA28, targets)  # Japan-only EndingMovie activation body
        self.assertIn(0x8063B3E4, targets)  # Japan-only TitleMovie activation body
        movie = [r for r in relocations if r["address"] in (0x80529742, 0x80529746)]
        self.assertEqual(len(movie), 2)
        self.assertEqual(len({r["target"] for r in movie}), 1)

    def test_development_pipeline_ports_include_fragments_and_isolates_state(self):
        source = (REPO / "builder/kartpad_builder/rmcj01.py").read_text()
        self.assertIn('".inc"', source)
        self.assertIn('value == 0x80808081', source)
        script = (REPO / "scripts/build-rmcj01-macos.sh").read_text()
        self.assertIn('portable.txt', script)
        self.assertIn('dev.kartpad.rmcj01.development', script)
        self.assertIn('trap restore_link EXIT', script)
        self.assertIn('wiicompiled-rkg-primary-controller.patch', script)
        self.assertIn('state.mkdir()', script)
        self.assertLess(script.index('inject-online-rkg-selection-hooks.py'), script.index('emit-build-shards'))

    def test_audit_includes_all_native_macro_forms_and_preserves_gaps(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile, _, data = fixture(root)
            address_map = root / "versions.txt"
            address_map.write_text("[J]\n80000100-800001ff: -0x80\n")
            function_map = root / "MAP.txt"
            function_map.write_text("80000100 Known\n80000200 Missing\n")
            config = profile.data["porting"]
            config.update(addressMap="versions.txt", sourceFunctionMap="MAP.txt")
            for key in ("addressMap", "sourceFunctionMap"):
                config[key + "SHA256"] = hashlib.sha256((root / config[key]).read_bytes()).hexdigest()
            runtime = root / "ref/upstream/Wiicompiled/runtime/src"
            runtime.mkdir(parents=True)
            (runtime / "fixture.cpp").write_text(
                "REGISTER_NATIVE_FUNCTION(0x80000100, A);\n"
                "REGISTER_TRANSLATED_FUNCTION(\n0x80000104, B);\n"
                "PPC_NATIVE_OVERRIDE_VOID(80000108, C, (), {});\n"
                "GX_FATAL_STUB(80000200, D);\n"
                "constexpr auto unknown = 0x80000204u;\n"
            )
            layout = {"entryPoint": "0x800060A4", "sdaBase": "0x8038C580", "sda2Base": "0x8038E920"}
            with patch("kartpad_builder.region_audit.read_dol_layout", return_value=layout):
                report = audit_region(root, profile, data)
            self.assertEqual(report["summary"]["nativeRegistrations"], 4)
            self.assertEqual(report["summary"]["nativeRegistrationsWithoutMapping"], 1)
            self.assertEqual(report["summary"]["unmappedMapEntries"], 1)
            self.assertFalse(report["summary"]["runtimeExecutionVerified"])
            self.assertEqual(report["unmappedRuntimeLiteralsForReview"][0]["value"], "0x80000204")
            address_map.write_text(address_map.read_text() + "# modified\n")
            with self.assertRaisesRegex(BuildError, "hash mismatch"):
                audit_region(root, profile, data)

    def test_region_selection_and_inclusive_boundaries(self):
        ranges = read_address_map("[P]\n80000000-*: +0x0\n[J]\n80000100-800001ff: -0x80\n", "J")
        self.assertEqual(map_address(0x80000100, ranges), 0x80000080)
        self.assertEqual(map_address(0x800001FF, ranges), 0x8000017F)
        self.assertIsNone(map_address(0x80000200, ranges))
        self.assertIsNone(map_address(0x800000FF, ranges))

    def test_missing_ranges_are_not_extrapolated(self):
        ranges = [AddressRange(0x80000100, 0x800001FF, -0x80), AddressRange(0x80000300, 0x800003FF, -0x80)]
        self.assertIsNone(map_address(0x80000200, ranges))

    def test_missing_region_and_unsupported_directive_fail(self):
        for text in ("[P]\n80000000-*: +0x0", "[J]\nextend P"):
            with self.assertRaises(BuildError):
                read_address_map(text, "J")

    def test_overlapping_invalid_and_overflowing_ranges_fail(self):
        for text in ("80000000-80000010: +0x0\n80000010-80000020: +0x0", "80000010-80000000: +0x0", "ffffffff-ffffffff: +0x1"):
            with self.assertRaises(BuildError):
                read_address_map("[J]\n" + text, "J")

    def test_dol_rejects_truncation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "main.dol"
            path.write_bytes(b"short")
            with self.assertRaisesRegex(BuildError, "truncated"):
                read_dol_layout(path)

    def test_dol_startup_bases_are_decoded_not_assumed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "main.dol"
            dol = bytearray(0x500)
            for offset, value in ((0, 0x100), (0x48, 0x80006000), (0x90, 0x400), (0xE0, 0x80006000)):
                struct.pack_into(">I", dol, offset, value)
            struct.pack_into(">4I", dol, 0x180, 0x3C408038, 0x6042E920, 0x3DA08038, 0x61ADC580)
            path.write_bytes(dol)
            layout = read_dol_layout(path)
            self.assertEqual(layout["sdaBase"], "0x8038C580")
            self.assertEqual(layout["sda2Base"], "0x8038E920")
            struct.pack_into(">I", dol, 0x90, 0xFFFF)
            path.write_bytes(dol)
            with self.assertRaisesRegex(BuildError, "section"):
                read_dol_layout(path)

    def test_real_extraction_when_available(self):
        data = REPO / "data"
        if not (data / "sys/main.dol").is_file():
            self.skipTest("user-supplied RMCJ01 partition is not present")
        _validate_extraction(japan_profile(), data)
        layout = read_dol_layout(data / "sys/main.dol")
        self.assertEqual(layout["entryPoint"], "0x800060A4")
        self.assertEqual(layout["sdaBase"], "0x8038C580")
        self.assertEqual(layout["sda2Base"], "0x8038E920")


if __name__ == "__main__":
    unittest.main()
