# Android 0.4.19 source delivery

The accompanying source archive identifies the exact compiled Android source
and public APK in `SOURCE-MANIFEST.json`. Every delivered member has its byte
length and SHA-256 recorded. The archive supplies software source and recipes;
it does not supply an SDK installation or the user's separate game inputs.

The delivery contains the current KartPad Git snapshot, pinned WiiCompiled and
Dolphin source, configured Dolphin submodules, profile-building tools, the
actual prepared Android runtime, and verified native/Maven dependency source
archives retained from the earlier release. No old Apple candidate is relabeled
as part of this Android delivery.

No translated game functions, extracted retail assets, downloaded game pack,
private generated data blobs, saves, device logs or signing identity are copied.
Public upstream snapshots retain their upstream resources and test fixtures.
A GitHub repository snapshot alone is not the full corresponding-source bundle.

Verify the published checksum before extracting. The inner Git snapshots include
`metadata/*.json` and `restore-source-git.py`; run that helper from the extracted
snapshot directory to validate files and restore their exact shallow Git
identities. Place upstream trees and Dolphin submodules at the paths recorded
in `dependencies.lock.json` and `dolphin-dependency-layout.json`.

Use the adjacent reconstruction guide and the delivered source's Android build
instructions. The maintainer's release key is not included; sign modified builds
with your own identity and preserve existing app data when certificates differ.
