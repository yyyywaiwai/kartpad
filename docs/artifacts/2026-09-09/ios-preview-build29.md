# iPhone/iPad 0.4.13 build 29 release evidence

Scope: iPhone and iPad, ARM64, minimum iOS/iPadOS 16. macOS and tvOS packages unchanged. Explicit manual publication authorized by Christopher.

Changes: chooser uses KartPad app artwork; problem reports add source/runtime/version context; physical iOS runtime and translated targets use generic ARM64 with RCpc disabled. The identified M2 instruction dependency is corrected; reporter #135 attribution and older-device hardware acceptance remain pending.

Source validation: 152 Python tests passed, 2 skipped (15.045 seconds). Independent Medium review cleared both CPU baseline commits and fresh iOS/Android preparation. The actual chooser controller was extracted into a simulator UI host; logo lookup and screenshots passed on iPhone 17 Pro and iPad Pro 13-inch (M5). This was a UI harness, not full-game simulator acceptance.

Prebuilt bounded ISA scan: Dawn 1,665,366 decoded instructions, DiscIO 109,038 decoded instructions, zero RCpc-family mnemonics. This is not a comprehensive all-ISA compatibility audit.

Remaining physical tests: update in place with same signer/bundle ID; verify chooser artwork and existing saves; launch Original and installed Retro, race, return to chooser; export/share a report; test older A10-class launch. External display recovery, end-of-cup reports and Mac issues remain separately unresolved. No game-performance gain claimed.

Fresh physical iOS build passed; app version 0.4.13/build29, minimum16.0, device families1 and2. Generated Xcode settings for all eight product/runtime/translated targets use generic ARM64 with RCpc disabled; actual response files for all six targets compiled into the dual product confirm those options and no M2 override. Final linked executable scan decoded17,528,634 instructions with zero RCpc-family mnemonics.

Native SHA-256: `1b7d86af82005c425ce94d2ae02baf4fdcf392c57ed11b6685a5d57081950f3f`. Assets.car SHA-256: `1214f8da03b0fe48193a0f2cbaddd469f5cf01f3bcce6fea624a30125270ff25` (same catalog as the verified chooser UI). The build and app audit passed. The earlier M2-targeted candidate is retained locally and excluded from release.

Final merged source and package hashes are recorded in the release provenance and published SHA256SUMS. The release owner must package the clean merged revision, repeat packaging deterministically, audit the unsigned IPA and anonymously download/compare the published assets before recording publication complete.
