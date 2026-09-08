from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


REPO = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


class AndroidProfileIconContractTests(unittest.TestCase):
    def test_android_recognizes_the_product_as_a_game(self):
        app = ET.parse(REPO / "android/app/src/main/AndroidManifest.xml").getroot().find("application")
        self.assertEqual(app.get(ANDROID + "appCategory"), "game")

    def test_scalar_mode_optimization_only_enters_the_android_patch_stack(self):
        patch_name = "wiicompiled-android-scalar-ni-transition.patch"
        android = (REPO / "scripts/prepare-android-game-runtime.sh").read_text()
        apple = (REPO / "scripts/prepare-ios-game-runtime.sh").read_text()
        self.assertIn(patch_name, android)
        self.assertNotIn(patch_name, apple)
        patch = (REPO / "patches" / patch_name).read_text()
        self.assertEqual(patch.count("+    if (niChanged)"), 3)
        self.assertEqual(patch.count("cpu->fpscr ^ result.fpscr"), 3)
        self.assertNotIn("feclearexcept", patch)
        self.assertNotIn("fetestexcept", patch)

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
