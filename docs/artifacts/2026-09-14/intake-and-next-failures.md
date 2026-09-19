# September 14 intake and next failure investigations

Refreshed after the owner’s reporting changes (main b662377). Stable Android remains code85; reporting preview 90 has identical native libraries. iOS reporting 42 is a fresh build, not a confirmed correction for #196.

## Response and duplicate pass

Eleven threads received targeted replies: #102, #104, #166, #193, #196, #206, #250, #273, #275, #277 and #278. The same reporter’s code 80 cellular/Wi-Fi update in #277 was copied into #206 and #277 was closed as a duplicate. Different-device performance and graphics reports were not collapsed merely for sharing symptoms. All 49 open tickets at intake were assigned to the owner; closing #277 left 48. No extra acknowledgement was posted for the old #198 handoff acceptance.

#102/#104/#166/#193 confirm graphics failures on85. No code 90 graphics retest was requested because its renderer is unchanged. #104 still affects pilots alone while scenery is intact; #102’s possibly improved icons are separate from unchanged model/road corruption. #250 supplies 60 Hz and interpolation off. #273 needs device/build and motion behavior because its body is empty. #275’s model name is ambiguous; #278 lacks profile scope. The reporting preview is offered to those performance reporters only to obtain a single session log, not as a speed fix.

## Android: recovered exact reported shader recipes

Both #193 pipeline IDs exist in the public 85 seed database (SHA256 `9ec9bf3617558f6608a1ef5ed34a6a87f916ce32d6400126b07f2480e3e7725c`), schema 19, 2768-byte configuration, first frame 231. An executable host harness used public 85 shader.cpp/shader_info.cpp to generate their WGSL before device module creation. The only renderer stub rounds uniform allocation size to 256; it does not change generated WGSL.

| Pipeline | Generated WGSL SHA256 |
| --- | --- |
| 58866e32bada1f83 | bad017e6a53cb06304af0aa9ee0285d8d2b9107c26e5c5fabc3155f1d2e554b2 |
| 33c5ff18d5c180e0 | 0c682289bfd23b08c9badea9109595f08e17728e9db3730cedf697dada560737 |

Both use a seven-byte vertex stride, PNMTX at offset 0 divided by 3, indexed F32x3 positions (array stride 12) and S16x3 normals (stride 6, fraction 14). Position/normal matrix arrays contain 20/10 elements and use dynamic indexing. Configuration validation and CPU shader generation pass; GPU/Tint validation is not yet performed. Local recipe blobs, WGSL and reproducible harness are retained in the private issue193 recipe-review directory.

**Next:** generate and validate a selected-draw literal-index variant of these exact shaders, retaining other texture matrices and state. The private diagnostic also needs draw-merge protection and bound shader/pipeline identity. It is absent from public 85; no ready diagnostic APK is claimed. A finite CPU input record does not establish GPU buffer content, lifetime or driver causality.

## iPhone: new #196 report symbolized

The submitted microstackshot UUID exactly matches retained public build 39. Symbolized app frames include `func_8000A3F8 → InvokeIndirectCpu → FatalMissingGuestTarget → WriteCrashArtifacts → WriteGuestMemorySnapshot`. The guest indirect target comes from object + 52, with caller LR 0x8000A42C; the numeric target is absent. The reporter was asked for the existing fatal text containing the missing target and caller LR, not another general analytics report or repeated crashes.

The report’s 4,336.72 MB file-backed dirtiness says **Action taken: none**. Thirteen of 16 samples reach guest zero-fill/dcbz (`InvokeDirectCpu<0x801A16E4>`); iOS guest RAM currently uses temporary files with MAP_SHARED. File-backed guest RAM is therefore a concrete storage-write hypothesis to investigate. The once-per-process fatal snapshot is at most 152 MiB and cannot alone be blamed for 4.3 GB.

**Next independent local work:** evaluate anonymous Mach VM aliases for iOS guest-memory backing with complete alias coherence, access/permission and cleanup tests before replacement. No measured speedup, supported iOS behavior or causal connection to the fatal dispatch is established yet.

Build 42 has a different executable UUID and fresh native compilation, but its CMake cache reuses an older Apple translation/shard directory. Source ancestry through continuation fixes does not establish regenerated translation. Do not claim build 42 fixes this missing target without the actual address and corresponding generated graph.
