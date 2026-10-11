"""Exercise the production package gate before unrelated binary audits."""
from pathlib import Path
import os
import plistlib
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DiagnosticModeGate(unittest.TestCase):
    def audit(self, value, expected=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            app = root / 'KartPad.app'
            app.mkdir()
            (app / 'Info.plist').write_bytes(plistlib.dumps({'KartPadDiagnosticsCandidate': value}))
            for name in ('KartPad', 'PrivacyInfo.xcprivacy', 'Assets.car',
                         'initial_pipeline_cache.db', 'dsp_coef.bin'):
                (app / name).touch()
            (app / 'KartPad').chmod(0o755)
            # Reaching plist lint proves the mode gate accepted the package.
            # Stop there: this fixture is intentionally not a complete iOS app.
            lint = root / 'plutil'
            lint.write_text('#!/bin/sh\nexit 93\n')
            lint.chmod(0o755)
            env = os.environ.copy()
            env.pop('KARTPAD_DIAGNOSTIC_CANDIDATE', None)
            if expected is not None:
                env['KARTPAD_DIAGNOSTIC_CANDIDATE'] = expected
            env['PATH'] = str(root) + os.pathsep + env['PATH']
            return subprocess.run(['bash', str(ROOT / 'scripts/audit-ios-game-app.sh'),
                                   str(app), 'IOS'], env=env, capture_output=True, text=True)

    def test_normal_package_reaches_remaining_audit(self):
        for value in ('NO', False):
            with self.subTest(value=value):
                self.assertEqual(self.audit(value).returncode, 93)

    def test_public_build59_configuration_is_rejected_by_default(self):
        result = self.audit('YES')
        self.assertEqual(result.returncode, 1)
        self.assertIn('stable apps must disable forced validation', result.stderr)

    def test_diagnostic_build_requires_matching_explicit_opt_in(self):
        self.assertEqual(self.audit('YES', 'YES').returncode, 93)
        self.assertEqual(self.audit('NO', 'YES').returncode, 1)

    def test_unresolved_setting_and_invalid_request_fail_closed(self):
        self.assertEqual(self.audit('$(KARTPAD_DIAGNOSTIC_CANDIDATE)').returncode, 1)
        self.assertEqual(self.audit('NO', 'maybe').returncode, 1)


if __name__ == '__main__':
    unittest.main()
