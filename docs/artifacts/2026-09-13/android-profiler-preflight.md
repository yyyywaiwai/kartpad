# Current Android CPU profiler preparation

The first performance target is sustained Android race slowdown after shader
compilation finishes. The #198 Helio G85 report already supplies settings,
three captures and willingness to profile. Do not ask for those again. A10X
performance is lower priority and is not assumed to have the same cause.

Public 0.4.18/code83 is non-debuggable but **not shell-profileable**. The retained
code73 Debug-signed profiler is stale and cannot update a Community-signed
installation. Build a private release-mode diagnostic from the current source
and verified native payload, with shell profileability enabled and a version
code greater than the recipient's installed version. Keep exact native symbols.

`scripts/build-android-game-app.sh` accepts `KARTPAD_ANDROID_PROFILEABLE=1`,
but its default APK lane runs `assembleDebug`. Use the release bundle lane
(`KARTPAD_ANDROID_PACKAGE_FORMAT=aab`) and the existing signed APK derivation
workflow, or the verified packaging-only recipe when reusing native outputs.
Do not rebuild native code merely to enable manifest profileability. Record
reused native source identity separately from diagnostic packaging identity.
Do not publish the diagnostic as a performance fix.

Before private delivery, run the offline preflight (Python 3.11+ and the pinned
Android SDK/NDK tools):

```sh
python3 scripts/audit-android-profiler.py /private/path/diagnostic.apk \
  /private/path/unstripped/libmain.so --version-code 84 \
  --signer-sha256 EXPECTED_RECIPIENT_CERTIFICATE_SHA256 > /private/path/profiler-receipt.json
```

The version above is an example allocation; verify current release and recipient
versions before building. Set `JAVA_HOME` to the verified JDK for `apksigner`.
The helper performs no ADB, installation, signing, upload or application actions.
It checks package/version, non-debuggable manifest, shell profileability and
verified signing certificate. Every allocated ARM64 ELF section (including
build-ID, native code and data, with its address/size) must match the unstripped
symbols. The JSON receipt records APK/native/symbol hashes. This complements,
and does not replace, the existing release package/content audit.

A matching expected certificate argument does not prove the installed device's
identity. Before any installation, separately verify its actual version/signer,
preserve state, and update in place. Never uninstall or clear data to force a
signer mismatch. Keep symbols, captures and device-specific evidence private.

## Bounded capture when hardware is available

Use the existing frame/health capture alongside a short (~20-second, ~99 Hz)
CPU sample during an actual warmed slow race. Record profile/course, resolution,
aspect, power state, thermal state and shader queue. No root/system tuning is
required. The operator retains control of the race; do not substitute a title
screen or automated launch. Capture exact process/thread identity locally and
symbolize using the preflight-verified library. Separate guest execution, GX CPU
preparation and waits before choosing a patch. Low `present_total` alone does
not exclude CPU work before presentation (including FIFO processing).

Compare an eventual targeted candidate against the same scene and settings,
with cold shader compilation separate and multiple warmed runs. Assess frame
percentiles/gaps, audio and correctness, not only average FPS. No new performance
claim is established by preparing a profiler.

## Preparation checks

The manifest tests cover the release-profileable success case and reject debug,
non-profileable, stale/wrong-package artifacts and an unrelated element's shell
attribute. The current public code83 APK was correctly rejected as non-profileable.
Its native library matched all 26 allocated sections of the retained unstripped
code83 symbols; using the stripped APK library as symbols was rejected. No
hardware actions or new diagnostic build occurred in this preparation step.

## Current diagnostic built after the review

Private **0.4.18-profile.1/code84** has now been packaged from code83 source (`2cea47f`) with shell profiling enabled and debugging disabled. Its four native libraries are byte-identical to public83. Package/AAB audits and the profiler preflight passed; all 26 allocated `libmain.so` sections match the retained unstripped symbols.

- APK SHA-256: `a2b13f94ca1fb1f22ce566f3d821030663af7ac928546cd05b39ccbca2cceb4c`
- Native SHA-256: `d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be`
- Symbols SHA-256: `4524a4d84e9db364b3e8ebbe8f9b54dc32a285976ae1fcaf19ed077b329a55a5`

The APK uses the existing Community Release certificate and remains private. It is suitable for an in-place update only after checking the recipient's installed version and signer. The owner's last verified Pixel installation is Debug-signed code82, so this Community-signed APK must not be installed over it; derive and audit a compatible private signing twin if that phone is used. Never uninstall to bridge this difference.

No installation, capture or performance improvement is claimed. The next step is the already accepted private tester handoff, or an owned local phone session with compatible packaging, followed by one warmed driven capture. No further native compilation is required merely to obtain that baseline.
