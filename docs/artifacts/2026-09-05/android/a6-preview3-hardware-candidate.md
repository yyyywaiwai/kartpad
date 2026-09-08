# Android A6 preview 3 hardware candidate

Date: 2026-09-05

Classification: **Pass for a reproducible, guarded, unpublished physical-phone
test candidate.** No physical Android device was attached, so this is not
hardware, vendor-Vulkan, performance, audio, touch, haptic, controller,
lifecycle, thermal, or online acceptance.

## Falsifiable subgoal

Promote the retained-data runtime-root correction to a forward-versioned local
preview, prove clean package reproducibility and release-derived execution, and
make the guarded phone installer accept only those exact bytes while still
rejecting the connected emulator before mutation.

## Identity and reproducibility

The current default is `0.4.0-android-preview.3`, version code 8. Two independent
scoped `:app:clean` plus release-bundle builds produced byte-identical unsigned
AABs:

```text
clean_to_clean_preview3_aab_match=yes
aab_sha256=85a7e12d8ebccbaa313dc2740e86137a26c24d02ac47c7835d6019a60f1335d7
```

Pinned bundletool derived a non-debuggable, locally test-signed universal APK:

```text
apk_sha256=b709d5e42b08be0e276c2fc07ed25b1f34a58c31282c049d6505a390ee647707
apk_bytes=90502311
```

The APK is retained outside Git at
`.android-bootstrap/hardware-preview/KartPad-0.4.0-android-preview.3-v8-arm64.apk`.
It contains no game data or save and uses only the local Android debug identity.
It was not uploaded, hosted, or published.

## Runtime and state result

The complete API 36 ARM64 bundle-derived gate passed:

```text
version_code=8
release_non_debuggable=yes
universal_selector_visible=yes
universal_runtime_stable=yes
universal_frame_diverse=yes
device_splits=4
split_signer_consistent=yes
split_native_bytes_exact=yes
split_selector_visible=yes
split_runtime_stable=yes
split_frame_diverse=yes
debug_apk_restored=yes
durable_state_preserved=yes
```

The guarded installer is pinned to the preview-3 name, code, path, and exact
APK digest. With the emulator as the sole ADB target, it failed in the physical
preflight before installation, suppressed the serial, and preserved the exact
installed package/version:

```text
serial_redacted=yes
package_unchanged=yes
installed_version=7
```

Physical execution remains the next authority. A later release-key package
cannot update this debug-signed preview in place; preserve/export any test save
before a signing-identity transition.
