# Renderer investigation follow-up, 8 September 2026

The 0.2.0 synthetic diagnostic passes all eight checks on the #104 reporter's
Adreno 750 / 512.762.41. The user ran it correctly without starting KartPad.
This adds affected-device indexed-draw, texture-read and queued-update evidence;
it does not reproduce the reported game failure. Adreno 840 draw results remain pending. The #104 reporter subsequently
confirmed the same corruption at 1x / 4:3, affecting drivers only; vehicles and
track environments look correct. That completes this reporter's requested
comparison. It differs from #102's additional road-texture symptoms.

A further source pass traced mapped staging-buffer rotation and copies in
Aurora common.cpp, implicit-device-synchronization feature selection and release
Dawn validation toggles in gpu.cpp, and texture conversion/upload including
CMPR expansion in texture_convert.cpp and texture.cpp. The pinned path clears
cached vertex-array ranges at batch end, waits for mapping completion before
exposing upload memory, and includes the implicit synchronization feature when
available. No additional reproducible defect was established in that pass.
The runtime disables WebGPU validation and robustness in release builds; the
synthetic diagnostic keeps validation enabled and tests both robustness modes.
A clean game log is therefore not a full draw-validation result.

The next useful local instrument is an opt-in, private game-renderer validation
capture or a reduced replay of the failing generated GX shader and resource
bindings, exercised on an affected physical GPU. That work is not implemented
or implied by the save/import release. Do not infer a Qualcomm driver bug or
ship alignment/robustness changes from these passing synthetic tests alone.

The driver-only observation makes per-vertex position/normal matrix selection
and the generated character shaders a more focused lead. The source pass also
checked PNMTXIDX byte decoding/division by three and compact versus absolute
matrix palette selection in shader.cpp and shader_info.cpp. No correction was
established from inspection alone. Capturing or reproducing a failing character
draw on an affected GPU remains the concrete evidence boundary; #104 has no
outstanding request for another log or repeat of the synthetic diagnostic.
