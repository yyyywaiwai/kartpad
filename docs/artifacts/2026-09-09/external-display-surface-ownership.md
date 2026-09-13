# External display surface ownership investigation

Astra Medium inspected main6fd847d and pinned SDL3.4.4 with the existing prepared
iOS source. No mirroring root cause, physical acceptance or code fix is claimed.

Aurora lib/dawn/MetalBinding.mm creates a new SDL_MetalView for every surface
descriptor request and retains no handle for reuse/destruction. SDL UIKit
setSDLWindow retains the new view, removes the previous root and installs the
replacement. KartPadRuntimeOverlayHost attaches controls once beneath the old
root. Aurora surface Lost recovery requests a descriptor through gpu.cpp, so
recreation can accumulate retained views and detach the controls by this source
ownership path. Upstream and inspected prepared MetalBinding helper match
SHA-25693e234f86f2fa0464ae26ca9d7feefca5fd5539fef7222b3399d4aa44fc68832.

No evidence yet shows display attachment causes Lost or explains TV-only black
video. Ordinary mirroring differs from a dedicated external game scene; current
manifest has application role only and SDL connect/disconnect registers displays.
Chooser first-scene versus SDL foreground-scene preference is a possible multi-
scene risk, not proof of a normal-mirroring defect. Missing explicit Metal-view-
resized handling alone is inconclusive because generic resize may cover it.

Next isolate forced surface recovery: preserve/reuse/destroy the Metal view with
explicit ownership, verify root/layer and overlay identity across recreation,
then pair with wired attach/reconnect evidence. Existing Lost log and whether
handheld video also fails distinguish recovery from mirror presentation. If
handheld continues without recovery, investigate mirror presentation instead.
No generic retry loop, new window/runtime or dedicated-output feature is justified
by this audit. No build, device operation or IPA publication occurred.
