from __future__ import annotations

import re
import plistlib
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class IOSGameDataPickerContractTests(unittest.TestCase):
    def test_picker_does_not_filter_disc_images_by_dynamic_uti(self) -> None:
        source = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        match = re.search(
            r"NSArray<UTType \*> \*KartPadGameDataContentTypes\(\) \{(.*?)\n\}",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        body = match.group(1)

        self.assertIn(
            "return @[UTTypeItem, UTTypeData, UTTypeDiskImage, UTTypeFolder];",
            body,
        )
        self.assertNotIn("typeWithFilenameExtension", body)
        self.assertEqual(
            source.count(
                "initForOpeningContentTypes:KartPadGameDataContentTypes()"
            ),
            2,
        )
        # Two game-data pickers plus the separate experimental .mii importer
        # all request private copies from potentially remote file providers.
        self.assertGreaterEqual(source.count("asCopy:YES"), 3)
        self.assertIn("choosingGameDataCopy", source)
        self.assertIn("deleteAfterwards:deleteAfterwards", source)

    def test_documents_scan_checks_disc_extension_before_directory_metadata(self) -> None:
        source = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        match = re.search(
            r"NSArray<NSURL \*> \*KartPadGameDataRootsInDocuments\(NSError \*\*error\)"
            r" \{(.*?)\n\}",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        body = match.group(1)
        self.assertLess(
            body.index("KartPadURLIsSupportedDiscImage(entry)"),
            body.index("getResourceValue:&directory"),
        )
        self.assertNotIn("!directory.boolValue", body)
        self.assertEqual(source.count("KartPadGameDataRootsInDocuments(&error)"), 2)

    def test_open_in_place_and_files_folder_contracts_are_declared(self) -> None:
        for name in ("Info.plist", "RuntimeInfo.plist"):
            with (REPO / "apple/ios" / name).open("rb") as handle:
                info = plistlib.load(handle)
            self.assertIs(info.get("UIFileSharingEnabled"), True, name)
            self.assertIs(
                info.get("LSSupportsOpeningDocumentsInPlace"), True, name
            )

        source = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        self.assertIn("KartPadDocumentsRoot(&documentsError)", source)

    def test_empty_installation_folder_scan_falls_back_directly_to_picker(self) -> None:
        source = (REPO / "apple/ios/KartPadRuntimeOverlayHost.mm").read_text()
        self.assertIn("KartPadDocumentsFolderScanDetail", source)
        self.assertIn("NSBundle.mainBundle.bundleIdentifier", source)
        self.assertIn("If a signer changes the bundle identifier", source)
        self.assertEqual(
            source.count('actionWithTitle:@"Import from This Installation\'s Folder..."'),
            2,
        )
        self.assertIn("[self presentGameDataPicker];", source)
        self.assertIn("[self presentGameDataFolderPicker];", source)
        self.assertEqual(
            source.count('NSLog(@"[KartPad] %@", KartPadDocumentsFolderScanDetail(error));'),
            2,
        )
        self.assertEqual(source.count("KartPadGameDataRootsInDocuments(&error)"), 2)

    def test_local_peer_network_usage_is_declared_and_audited(self) -> None:
        for name in ("Info.plist", "RuntimeInfo.plist"):
            path = REPO / "apple/ios" / name
            with path.open("rb") as handle:
                info = plistlib.load(handle)
            description = info.get("NSLocalNetworkUsageDescription", "")
            self.assertIn("local network", description, name)
            self.assertIn("multiplayer", description, name)
            self.assertEqual(
                path.read_text().count("<key>NSLocalNetworkUsageDescription</key>"),
                1,
                name,
            )
        audit = (REPO / "scripts/audit-ios-game-app.sh").read_text()
        self.assertIn("plutil -extract NSLocalNetworkUsageDescription raw", audit)
        package = (REPO / "scripts/package-macos-runtime.sh").read_text()
        self.assertIn("plutil -insert NSLocalNetworkUsageDescription -string", package)
        self.assertEqual(
            package.count("plutil -insert NSLocalNetworkUsageDescription -string"),
            1,
        )
        mac_audit = (REPO / "scripts/audit-macos-package.sh").read_text()
        self.assertIn("plutil -extract NSLocalNetworkUsageDescription raw", mac_audit)


if __name__ == "__main__":
    unittest.main()
