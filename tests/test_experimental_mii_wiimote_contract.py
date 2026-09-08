import pathlib
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


class ExperimentalMiiWiimoteContractTests(unittest.TestCase):
    def test_ios_menu_exposes_features_in_expected_submenus(self) -> None:
        source = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        self.assertIn('actionWithTitle:@"Player Identity…"', source)
        self.assertIn('actionWithTitle:@"Rename or Delete Licenses…"', source)
        self.assertIn('actionWithTitle:@"Rename License…"', source)
        self.assertIn('actionWithTitle:@"Delete License…"', source)
        self.assertIn('actionWithTitle:@"Remove Mii Appearance…"', source)
        self.assertIn('actionWithTitle:@"Edit Mii Name…"', source)
        self.assertIn('menuWithTitle:@"Controls"', source)
        self.assertIn('actionWithTitle:@"Experimental Wii Remote + Nunchuk…"', source)
        self.assertLess(source.index('actionWithTitle:@"Player Identity…"'),
                        source.index('gameData = [UIMenu menuWithTitle:dataMenu.title'))

    def test_mii_changes_are_staged_and_applied_before_runtime(self) -> None:
        manager = (REPO / "apple/shared/KartPadMiiManager.mm").read_text()
        runtime = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        mac = (REPO / "apple/macos/KartPadMacShell.mm").read_text()
        self.assertIn('@"PendingRFL_DB.dat"', manager)
        self.assertIn('@"PendingPlayerIdentity.plist"', manager)
        self.assertIn('@"PendingLicenseChange.plist"', manager)
        self.assertIn('RetroRewind/riivolution/save/RetroWFC/RMCP/rksys.dat', manager)
        self.assertIn('RetroRewind/riivolution/save/RetroWFC2/RMCP/rksys.dat', manager)
        self.assertIn('NSDataWritingAtomic', manager)
        self.assertIn('@"MiiBackups"', manager)
        self.assertIn('@"SaveBackups"', manager)
        self.assertIn('KartPadStagePlayerName', manager)
        self.assertIn('KartPadStageLicenseRename', manager)
        self.assertIn('KartPadStageLicenseDeletion', manager)
        self.assertIn('KartPadApplyPendingMiiDatabase(&miiError)', runtime)
        self.assertIn('KartPadApplyPendingMiiDatabase(&miiError)', mac)

    def test_wiimote_driver_is_opt_in_and_packaged_with_bluetooth_permission(self) -> None:
        pairing = (REPO / "apple/macos/KartPadWiimotePairing.mm").read_text()
        package = (REPO / "scripts/package-macos-runtime.sh").read_text()
        entitlements = (REPO / "apple/macos/KartPad.entitlements").read_text()
        self.assertIn('SDL_HINT_JOYSTICK_HIDAPI_WII, "0"', pairing)
        self.assertIn('SDL_HINT_JOYSTICK_HIDAPI_WII, "1"', pairing)
        self.assertIn('Nintendo RVL-CNT-01', pairing)
        self.assertIn('NSBluetoothAlwaysUsageDescription', package)
        self.assertIn('com.apple.security.device.bluetooth', entitlements)

    def test_runtime_preparation_applies_explicit_nunchuk_preset(self) -> None:
        preset = REPO / "patches/wiicompiled-experimental-wiimote-preset.patch"
        self.assertTrue(preset.exists())
        text = preset.read_text()
        self.assertIn('kWiimoteNunchukPreset', text)
        self.assertIn('"unmapped",      // L: Nunchuk Z', text)
        for script in ("prepare-g7-game-runtime.sh", "prepare-ios-game-runtime.sh"):
            self.assertIn(preset.name, (REPO / "scripts" / script).read_text())


if __name__ == "__main__":
    unittest.main()
