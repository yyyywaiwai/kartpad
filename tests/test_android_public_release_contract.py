from pathlib import Path
import ast
import unittest

REPO = Path(__file__).resolve().parents[1]


class AndroidPublicReleaseTests(unittest.TestCase):
    def test_derivation_is_guarded_and_never_installs(self):
        source = (REPO / "scripts/derive-android-release-apk.sh").read_text()
        for required in ("audit-android-bundle.sh", "audit-android-package.sh",
                         "CN=Android Debug", "androiddebugkey", "apksigner",
                         "KARTPAD_ANDROID_EXPECTED_VERSION_CODE", "KARTPAD_ANDROID_REQUIRE_RELEASE",
                         '--ks-pass="file:', '--key-pass="file:', '--mode=universal'):
            self.assertIn(required, source)
        for forbidden in ("adb ", "gh release", "-genkeypair", "pass:android"):
            self.assertNotIn(forbidden, source)

    def test_public_notices_have_provenance_and_exact_signer(self):
        source = (REPO / "scripts/package-android-release-notices.py").read_text()
        for required in ("sourceCommit", "apkSHA256", "nativeLibraries", "noticesSHA256",
                         "containsTranslatedGameCode", "upstreamRightsConfirmed",
                         "certificate_sha256", "CN=Android Debug", '"--porcelain"',
                         "APPROVED_NATIVE",
                         "GPL-3.0.txt", "Dawn-BSD.txt", "SDL3-Zlib.txt", "package.testzip()"):
            self.assertIn(required, source)
        assignments = {
            target.id: node.value
            for node in ast.parse(source).body if isinstance(node, ast.Assign)
            for target in node.targets if isinstance(target, ast.Name)
        }
        native = ast.literal_eval(assignments["APPROVED_NATIVE"])
        self.assertEqual(set(native), {
            "lib/arm64-v8a/libmain.so", "lib/arm64-v8a/libkartpad_discio.so",
            "lib/arm64-v8a/libSDL3.so", "lib/arm64-v8a/libc++_shared.so",
        })
        self.assertEqual(native["lib/arm64-v8a/libmain.so"],
                         "d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be")
        for digest in native.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertIn("native != APPROVED_NATIVE", source)

    def test_update_guide_preserves_private_previews(self):
        guide = (REPO / "docs/INSTALL_ANDROID.md").read_text()
        for required in ("Do not uninstall", "does not back up Retro", "different local",
                         "60 FPS", "APK", "SHA256SUMS"):
            self.assertIn(required, guide)


if __name__ == "__main__":
    unittest.main()
