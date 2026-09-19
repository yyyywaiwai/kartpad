from pathlib import Path
from runtime_sources import runtime_source, assert_runtime_staging
import unittest
import xml.etree.ElementTree as ET


REPO = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


class AndroidProfileIconContractTests(unittest.TestCase):
    def test_android_recognizes_the_product_as_a_game(self):
        app = ET.parse(REPO / "android/app/src/main/AndroidManifest.xml").getroot().find("application")
        self.assertEqual(app.get(ANDROID + "appCategory"), "game")

    def test_scalar_mode_optimization_is_android_only(self):
        assert_runtime_staging(self, "android")
        android = runtime_source("android", "runtime/include/ppc_runtime.h")
        self.assertEqual(android.count("    if (niChanged)"), 3)
        self.assertEqual(android.count("cpu->fpscr ^ result.fpscr"), 3)
        for platform in ("ios", "macos", "tvos"):
            with self.subTest(platform=platform):
                self.assertNotIn("niChanged", runtime_source(platform, "runtime/include/ppc_runtime.h"))

    def test_launcher_uses_shared_apple_artwork_with_mask_safe_inset(self):
        gradle = (REPO / "android/app/build.gradle.kts").read_text()
        self.assertIn("../apple/ios/Assets.xcassets/AppIcon.appiconset/KartPadIcon-1024.png", gradle)
        self.assertIn("dependsOn(prepareKartpadIcon)", gradle)
        manifest = ET.parse(REPO / "android/app/src/main/AndroidManifest.xml")
        app = manifest.getroot().find("application")
        self.assertEqual(app.get(ANDROID + "icon"), "@mipmap/ic_launcher")
        self.assertEqual(app.get(ANDROID + "roundIcon"), "@mipmap/ic_launcher")
        icon = ET.parse(REPO / "android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml")
        inset = icon.getroot().find("foreground/inset")
        self.assertEqual(inset.get(ANDROID + "drawable"), "@drawable/kartpad_app_icon")
        self.assertEqual(inset.get(ANDROID + "inset"), "16.6667%")

    def test_profiling_is_explicitly_opt_in_and_does_not_enable_debugging(self):
        gradle = (REPO / "android/app/build.gradle.kts").read_text()
        self.assertIn('providers.gradleProperty("kartpadProfileable")\n    .map { it.toBooleanStrict() }\n    .getOrElse(false)', gradle)
        self.assertNotIn("isDebuggable = true", gradle)
        manifest = ET.parse(REPO / "android/app/src/main/AndroidManifest.xml")
        profile = manifest.getroot().find("application/profileable")
        self.assertEqual(profile.get(ANDROID + "shell"), "${kartpadProfileable}")
        script = (REPO / "scripts/build-android-game-app.sh").read_text()
        self.assertIn('${KARTPAD_ANDROID_PROFILEABLE:-0}', script)
        self.assertIn('if [[ "$profileable" == 1 ]]', script)


if __name__ == "__main__":
    unittest.main()
