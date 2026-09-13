# Apple Metal surface recovery correction

9 September 2026. Based on main `1e10db7`. This follows the
[ownership investigation](external-display-surface-ownership.md) associated with
[#100](https://github.com/chrissotraidis/kartpad/issues/100).

## Reproduced defect and correction

Aurora's Metal descriptor helper created a new SDL Metal view on every call.
WebGPU surface recreation calls this helper again. SDL UIKit replaces its root
view, leaving children of the previous root detached; on macOS, repeated calls
also allocate additional Metal views. Existing KartPad overlay reattachment on
activation/screenshots does not make ownership during surface recovery correct.

`aurora-metal-view-lifetime.patch` owns one SDL Metal view through a window
property and reuses it for subsequent descriptors. Its cleanup destroys the
view when SDL cleans up the window properties, before native-window destruction
in pinned SDL 3.4.4. Descriptor lifetime does not own the view. Creation,
property-registration and missing-layer failures return no descriptor; cleanup
also covers failed registration, as required by
[SDL's cleanup contract](https://wiki.libsdl.org/SDL3/SDL_SetPointerPropertyWithCleanup).
No retry loop, additional game window or new external-display mode is introduced.

The Mac and iOS preparation scripts apply the patch. tvOS inherits iOS
preparation. Android's shared preparation can contain the source patch, but its
renderer does not compile the Apple-only MetalBinding.mm implementation.
No Android runtime behavior or optimization is changed.

## Validation

The checked-in native probe compiles the actual prepared MetalBinding.mm against
real SDL 3.4.4 and Dawn headers. It attaches an ordinary native button below the
SDL root, requests 100 descriptors per window for three successive windows,
checks root/overlay/layer identity, clears and presents a real Metal drawable,
and verifies the layer is released after each window's teardown. UIKit release
is checked after bounded run-loop settling to allow appearance transitions.

| Target | Result |
| --- | --- |
| Native Apple Silicon macOS | 300 repeated descriptor requests, three successful Metal presentations and three layer releases pass |
| iPad Pro 13-inch (M5), iPadOS 26.5 simulator | Same native probe passes |
| iPhone 17 Pro, iOS 26.5 simulator | Same native probe passes |
| Physical M2 iPad Pro 12.9-inch (6th generation), iPadOS 26.6.1 | Same native probe passes: 300 requests, stable root/overlay/layer, three presentations and three teardowns |
| Unpatched helper, macOS and iPhone simulator | Negative controls fail at the first repeated request because the Metal layer is replaced |
| tvOS device target | Native probe compiles and links with the existing SDL library; Mach-O TVOS, minimum 17.0; not run on Apple TV |
| Injected SDL failures | Actual patched helper passes ASan/UBSan coverage for null window, property/create/register/layer failures, retry, descriptor destruction, independent windows and window-ID reuse |
| Existing Apple contracts | 23 iOS, 10 tvOS and eight macOS Python tests pass |

Fresh iOS/tvOS preparation completes. macOS preparation applies all patches and
reaches configuration; full-game configuration/build was deliberately stopped.
All three prepared Metal helpers have SHA-256
`451345117f3968eb3bf900da6baee9503226ac4032a475f8c8358171ebca1109`.
The probes contain no translated game code or game assets and use a separate
bundle identifier.

## Physical iPad candidate

The full dual-profile iPhoneOS app built from `3606741` passes the existing app
audit. Its unsigned executable SHA-256 is
`d4fda0c28172e870147c5bbab3e1d65cd10be8443a46f19d5b656afc1095b1ff`.
It retains the source version metadata, 0.4.13 / build 29; this is a private
candidate with the Metal correction, not a replacement public release.

The candidate was development-signed with an existing profile that includes the
attached iPad and installed in place over 0.4.10 / build 25. Before installation,
the stopped app's normal NAND, Retro Rewind save directory, Mii/save backups,
console identity, configuration and preferences were copied privately. All 32
files (19,871,307 bytes) have identical hashes immediately after installation
and again after the candidate reached its chooser.
The chooser launches and recognizes the existing Original and Retro Rewind
6.12.7 installations. The signed executable SHA-256 is
`2ea1c5e86ac43e04f4fcf362f447062d80100573eb4e47a9915111bd672ed402`.
The iPhone was not modified. Device identifiers, signing details, backups and
raw device logs remain outside the repository.

The separate native probe also ran successfully on this physical iPad and was
removed after its test. The user subsequently entered a Mario / Luigi Circuit
Grand Prix race: the game and touch overlay were visible. The game exited during
an attempted debugger attachment, before any graphics fault was injected. Its
exact exit cause remains unconfirmed. This is not a successful full-game recovery
test; subsequent automated checks use a separate app without a debugger.

## Real WebGPU surface recreation on the physical iPad

`apple_webgpu_surface_probe.mm` links the same pinned physical-iOS Dawn and SDL
libraries and compiles the actual Metal descriptor helper. It automatically
acquires, submits and presents 120 frames, replacing its Dawn surface after frames
30, 60 and 90. It drains submitted GPU work, unconfigures/releases the old surface,
creates/configures a replacement, and continues rendering. Every frame checks
native root and overlay attachment; every recreation checks Metal-layer identity.
Any acquisition, submission-completion, presentation or uncaptured Dawn error
fails the test.

On the same physical M2 iPad and iPadOS 26.6.1:

- Corrected helper: **PASS**, three actual Dawn surface recreations and 120
  acquired/submitted/presented frames; root, overlay and Metal layer preserved.
- Original helper: **FAIL at frame 30**, before completing its first recreation,
  because the Metal layer is replaced. The preceding 30 frames rendered normally.
- The signed passing test executable has SHA-256
  `ffb2ca0fb3089bf447c686ffe0e661e23885448801a0dc80ecb46c688fd59aed`.
  Private signing details and device logs remain outside the repository.

This is a bounded, automatic test with a separate bundle identifier,
`dev.kartpad.webgpu-recovery-probe`. It requires no game files, debugger attachment,
race setup, or user taps. Its own frame loop deliberately requests recreation;
it does not simulate an OS-generated SurfaceLost event or execute Aurora's full
presenter/worker scheduling. It also does not test physical touch delivery to
KartPad's actual game controls.

## Reproduction

Run `python3 -m unittest discover -s tests -p test_apple_metal_view_lifetime.py`.
Build the native probe using `scripts/build-apple-metal-surface-probe.py` with
`--aurora` pointing at a prepared Aurora directory, `--sdl-include`,
`--sdl-library`, `--dawn-include`, `--sdk` and a fresh `--output` directory.
Run the macOS executable directly; simulator apps use bundle identifier
`dev.kartpad.metal-recovery-probe` and can be installed/launched with `simctl`.
Pass the unpatched Aurora directory for the negative control. No game import or
installed KartPad data is necessary.

For the WebGPU variant, add `--dawn-library` pointing to the matching SDK's pinned
`libwebgpu_dawn.a`. The builder selects the automatic WebGPU probe and its separate
bundle identifier. Physical-device signing/installation is still separate from
the builder. For the negative control, use the unpatched Aurora directory with
otherwise identical SDL/Dawn inputs; the expected failure is the first recreation
at frame 30.

## Acceptance boundary

These include native helper and actual WebGPU surface-recreation tests, not a
forced Dawn surface-loss result inside a running game. They establish the
view-ownership fix, not the
cause or resolution of TV-only black video in #100. Full-game surface recovery,
touch/controller continuity, wired mirroring, AirPlay and Apple TV gameplay
remain separate acceptance gates. No public IPA or game release is produced here.
