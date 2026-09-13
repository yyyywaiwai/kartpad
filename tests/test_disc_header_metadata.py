import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/inspect-disc-header.py'
spec = importlib.util.spec_from_file_location('disc_header', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def header(identity=b'RMCE01', disc=0, revision=0):
    return identity + bytes([disc, revision]) + bytes(16) + bytes.fromhex('5d1c9ea3')


class DiscHeaderTests(unittest.TestCase):
    def test_identity_and_revision_are_independent_of_supported_region(self):
        self.assertEqual(module.inspect_header(header(revision=2)),
                         {'disc_id': 'RMCE01', 'disc_number': 0, 'revision': 2})
        self.assertEqual(module.inspect_header(header(b'RMCP01', disc=1))['disc_number'], 1)

    def test_rejects_containers_truncation_and_non_wii_header(self):
        for value in (b'WBFS' + bytes(24), b'RVZ\x01' + bytes(24), b'WIA\x01' + bytes(24),
                      header()[:27], header()[:24] + bytes(4), header(b'bad!??')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.inspect_header(value)

    def test_cli_reads_only_header_and_does_not_modify_or_expose_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'private-image.iso'
            original = header(revision=1) + b'private payload'
            path.write_bytes(original)
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                    check=True, capture_output=True, text=True)
            self.assertIn('"revision": 1', result.stdout)
            self.assertNotIn(temporary, result.stdout + result.stderr)
            self.assertNotIn('private payload', result.stdout)
            self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
