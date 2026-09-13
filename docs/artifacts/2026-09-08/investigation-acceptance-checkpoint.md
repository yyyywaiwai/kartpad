# Investigation acceptance checkpoint

**Superseded device-status evidence:** the earlier `:game` process checks were
incorrect. The game runs as `dev.kartpad.android`; the chooser is `:launcher`.
The owner subsequently reported a real run with persistent slowdowns and severe
thermal throttling. Saved logs include intervening gameplay. See
[pixel-owner-slowdown-followup.md](pixel-owner-slowdown-followup.md). The old
“no game process/comparison” conclusion must not be used for publication.

This records remaining gates without narrowing the original investigation goal.
No freeze/graphics correction or complete cross-device acceptance is claimed.

| Requirement | Evidence and current limit |
| --- | --- |
| Investigate Pixel slowdown architecturally | Owner reproduced slowdown on34b3de0.23.87FPS interval after pipeline queue drained;20s CPU capture2,984samples identifies game-thread and FP/TLS costs. It does not isolate every freeze or graphics corruption. See pixel-hardware-cpu-profile.md. |
| Evidence-supported fix or bounded diagnostics | Conditional Android flag clearing a850ada passes520,000 differential cases and512 flag-state checks on Pixel,250,227 host semantics checks. Synthetic operations mostly6–9% faster, one sqrt3.7% slower. Same-scene gameplay comparison remains pending. Network in-progress registry and actual draw diagnostics validated separately in android-runtime-investigation-candidate.md. |
| Shared Android/Apple report context | Version/content/clocks/configuration and bounded source fingerprints implemented. Kotlin/Foundation tests and Android build/export pass; iOS SDK compilation passes. iOS physical share/export remains untested; no macOS/tvOS parity claim. Export-time context does not identify every historical log. |
| Retro compatibility audit | Installation/launch hashes/version gates and pinned statically translated online payload traced and tested; no blind latest-code update added. Future server compatibility and real Retro/online race acceptance remain device gates. See runtime-investigation-loop.md. |
| Local Android candidate and exact audit | Code25a850ada installed on owner Pixel;406 state files identical after update. Code26de9731a with provenance built/audited and actual emulator ZIP export passes; retained locally, not installed on Pixel. See report-build-provenance.md. |
| Preserve data/builds and coordination | Isolated worktrees, retained old APKs and state backups; emulator stopped without wiping. Coordinator owns GitHub/public integration. No publication or formal IPA. |

Next required input: Christopher's same Mario Kart Wii track/mode run on the
installed Pixel candidate and symptom timing. The request has remained pending
through multiple goal continuations. The old no-game-process inference is superseded; there is gameplay evidence,
but no temperature/scene-matched percentage comparison. The finite capture ended; later owner-run logs and CPU profiling are documented
in the follow-up above. Do not infer acceptance or restart tests by controlling his game.
Affected-Adreno corruption needs matching scene/validation evidence or a reduced
failing replay; iOS reports need physical acceptance. Additional speculative
CPU changes would not close these gates. Local integration is handed to the
coordinator; the active investigation is waiting for device evidence.
