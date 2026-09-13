#!/usr/bin/env python3
"""Fail-closed manifest coverage for the private CPU-profiler handoff."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit-android-profiler.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ManifestTests(unittest.TestCase):
    badging = "package: name='dev.kartpad.android' versionCode='84' versionName='0.4.18-profile.1'"
    tree = '  E: application\n    E: profileable (line=51)\n      A: http://schemas.android.com/apk/res/android:shell(0x01010594)=true\n    E: activity\n'

    def test_release_profiler(self):
        self.assertEqual(audit.check_manifest(self.badging, self.tree, 84)['version_code'], 84)

    def test_debug_build_rejected(self):
        with self.assertRaisesRegex(ValueError, 'non-debuggable'):
            audit.check_manifest(self.badging + '\napplication-debuggable', self.tree, 84)

    def test_public_non_profileable_rejected(self):
        with self.assertRaisesRegex(ValueError, 'profileability'):
            audit.check_manifest(self.badging, self.tree.replace('=true', '=false'), 84)

    def test_shell_attribute_in_other_element_does_not_pass(self):
        tree = self.tree.replace('      A:', '    E: unrelated\n      A:')
        with self.assertRaisesRegex(ValueError, 'profileability'):
            audit.check_manifest(self.badging, tree, 84)

    def test_old_build_and_wrong_package_rejected(self):
        for badging in (self.badging.replace("'84'", "'73'"), self.badging.replace('dev.kartpad.android', 'example.other')):
            with self.subTest(badging=badging), self.assertRaisesRegex(ValueError, 'package|version'):
                audit.check_manifest(badging, self.tree, 84)


if __name__ == '__main__':
    unittest.main()
