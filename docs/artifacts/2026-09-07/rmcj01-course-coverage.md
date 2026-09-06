# RMCJ01 / Retro Rewind 6.12.7 course coverage

**Scope update:** The user explicitly removed course verification from the task on 2026-09-07. This ledger is retained as historical static evidence; runtime-pending rows are no longer goal blockers and must not be marked passed.

**Generated:** 2026-09-07 (local Apple Silicon host)
**Ledger:** [`private/rmcj01/coverage/rmcj01-course-coverage.json`](../../../private/rmcj01/coverage/rmcj01-course-coverage.json)
**Checker:** [`scripts/audit-rmcj01-course-assets.py`](../../../scripts/audit-rmcj01-course-assets.py)
**Focused tests:** [`tests/test_rmcj01_course_assets.py`](../../../tests/test_rmcj01_course_assets.py)

This is a reproducible **static-asset ledger**, not a claim that every course,
mode, network path, or device has been played.  The checker reads archives in
place and does not export or copy game members.  The original ISO and the
extracted `data/` tree are read-only inputs.

## Inputs and provenance pins

| Input | Value |
| --- | --- |
| Disc | RMCJ01 revision 0 |
| `sys/main.dol` SHA-256 | `1b9621ef7c5d97dada103e50e5389730e67f3c2545dda592edd4b5843655af91` |
| `rel` static R SHA-256 | `88539012d357a1420724e51dc7e351192ce696da4b0045994895518a3fad6fae` |
| Retro pack | Retro Rewind 6.12.7 (`private/rmcj01/retro/pack/RetroRewind6`) |
| `Code.pul` SHA-256 | `3a1e60f6c94e435ff672167816dbe040d0f48874bfa093ada39e468655baef72` |

The source references are read-only: `ref/upstream/rr-pulsar` (PULS/Cups,
slot expansion and course loader) and `ref/upstream/mkw-sp` (U8 cursor/
iterator and course library).  No source or archive payload was copied into a
public artifact.

## Static checks

Each configured `.szs` is checked as `Yaz0`/`Yaz1` → U8.  U8 traversal follows
the source iterator's linear node table and directory-stack pop semantics;
this matters for real RR archives whose nested `brasd/penguin_s` range crosses
its parent end index.  The checker validates, without exporting members:

* `course.kmp`: `RKMD`, declared size, 15 sections, 0x4c header and section
  tags/offsets (`KTPT` through `STGI`).
* `course.kcl`: 0x3c header and four in-bounds, monotonic section offsets.
* `course_model.brres` and `map_model.brres`: `bres` magic.
* Optional `course.bmm`, `course.btiEnv`, `course.btiMat` are recorded but are
  not required for the CourseMgr loadability check.
* Retail `*_d.szs` multiplayer archives require `course.kmp`, `course.kcl`
  and `map_model.brres`; `course_model.brres` is recorded as an inherited
  member from the base retail archive.

The static result is intentionally independent from `runtimeStatus`.
`staticPass` means only that the configured archive structure and required
members passed these checks.

## Ledger counts

The generated report contains **386 logical course rows** and **465 archive
variants**.  Every archive variant passed the static checks; runtime evidence
is much narrower.

| Source bucket | Logical rows | Archive variants | Static pass/fail | Runtime verified / pending |
| --- | ---: | ---: | ---: | ---: |
| Retail race (`retail32`) | 32 | 64 (base + `_d`) | 32 / 0 | 2 / 30 |
| Retail battle (`retail_battle10`) | 10 | 20 (base + `_d`) | 10 / 0 | 0 / 10 |
| RR RT (`rr_retro`, ConfigRT) | 172 | 209 (172 + 37 named variants) | 172 / 0 | 1 / 171 |
| RR CT-only (`rr_ct`, ConfigCT) | 132 | 132 | 132 / 0 | 0 / 132 |
| RR battle (`rr_battle`, ConfigBT) | 40 | 40 | 40 / 0 | 0 / 40 |
| **Total** | **386** | **465** | **386 / 0** | **3 / 383** |

`archiveStatus` is therefore `pass=465`, `fail=0`, `missing=0`.  The 209 RT
course-list entries visible in the native UI are accounted for as 172 base
rows plus 37 configured variant files.  ConfigRT's raw header advertises
`totalVariantCount=38`, one greater than the per-track sum (37); this remains
an explicit diagnostic (`configIssueCount=3`) rather than a static archive
failure.

## Config diagnostics and source semantics

The report keeps three non-fatal config diagnostics:

1. ConfigRT metadata variant count `38` versus track sum `37`.
2. Five ConfigRT `FILE` keys outside the configured track/variant bounds.
3. Four ConfigCT `FILE` keys outside those bounds.

`rr-pulsar`'s `CupsConfig` combined constructor derives the runtime total by
`CountSourceVariants(track.variantCount)` instead of trusting the raw
`totalVariantCount` field.  Its `LoadFileNames` path also drops out-of-range
`FILE` keys.  The JSON marks these as
`non_authoritative_metadata_source_recomputes_track_sum` and
`ignored_by_source_bounds_check`; they are retained for auditability and are
not silently counted as missing course assets.  A case-only ConfigBT spelling
(for example `GCNBC` on a case-insensitive macOS volume) is preserved as the
configured source name; the archive still has to pass the byte/format checks.

### Case-sensitive iOS lookup review

The one known case-only spelling (`GCNBC.szs` in ConfigBT versus the extracted
`gcnBC.szs`) was checked against the generated runtime rather than inferred from
the macOS volume.  `DvdFstContract::NormalizeLookupPath` lowercases canonical
DVD paths (`build/rmcj01-ios-repro/runtime/include/hle/dvd_contract.h:91-97`).
`RegisterFileEntry` stores the actual host path while indexing the lowercased
logical path (`build/rmcj01-ios-repro/runtime/src/hle/storage/dvd.cpp:407-418`),
and both FST publication and test/open lookup use that same index (`dvd.cpp:595-612,
724-744`; `dvd_contract.h:164-191`).  As a result, the folder mapping registers
the real `gcnBC.szs` path and a guest request for `GCNBC.szs` resolves it on a
case-sensitive iPad filesystem; this conclusion is source-based and is not a
device/runtime execution result.  The lowercased fallback path in
`ResolveDvdMappedHostPath` is not relied on for this row because `DVDInit` scans
overlay folders before loading the disc FST (`dvd.cpp:810-841`).

The bounded save/identity review likewise found no functional PAL residue in
the generated iOS host: `KartPadMiiManager.mm:33-58` uses `524d434a` and `RMCJ`,
matching the Riivolution `{$__gameid}{$__region}` save redirect and the runtime's
`RMCJ01` low-memory identity.  Remaining `RMCP`/`PAL` strings in generated
runtime files are provenance or explanatory comments only; they are not counted
as runtime validation.

## Runtime boundary and accepted evidence

Only three rows carry runtime evidence, all on the macOS native local fixture:

* Retail `Luigi Circuit` (`courseId=8`) staff replay.
* Retail `Moo Moo Meadows` (`courseId=1`) staff replay.
* RR ConfigRT row `index=142`, `pulsarId=0x18e` (`rMC1`, visible as **SNES
  Mario Circuit 1**) staff-ghost replay.  The five-lap run reached finish
  stage 4.  The bounded trace is
  [`private/rmcj01/retro/rr-snes-mario-circuit-1-replay-trace.csv`](../../../private/rmcj01/retro/rr-snes-mario-circuit-1-replay-trace.csv)
  (SHA-256 `d001e97784ae13cde7bc6235d2b559e12654dd82f293e8006c090da515e0aaa1`).

For the RR `rMC1` row, a normal Solo Time Trial was started and its native
pause/resume/restart/quit path was exercised, but it was **not** naturally
completed.  The verified status is therefore specifically
`verified_staff_replay`; it must not be relabeled as a human race result.
Every other row remains `runtimeStatus.status=pending`, including Grand Prix,
VS, Battle, local multiplayer, 200cc/variant combinations, Retro WFC and
online matchmaking.

## Mode/test matrix

The JSON's `modeMatrix` keeps static and runtime obligations separate:

| Scope | Representative modes | Asset set | Runtime boundary |
| --- | --- | --- | --- |
| `original_single` | Grand Prix 50/100/150cc, CPU VS, Time Trial/staff replay, CPU Battle | Retail 32 + battle 10 | Only the two named retail staff replays verified |
| `original_local_multiplayer` | VS 2–4P, Balloon Battle/Coin Runners 2–4P | Retail base + `_d` archives | Pending; `_d` static checks do not imply a multiplayer run |
| `retro_rewind_offline_single` | RT/CT/BT cups, 150/200cc, configured Feather/Item Rain variants | ConfigRT/CT/BT rows and variants | Pending except the one RR staff replay |
| `retro_rewind_local_multiplayer` | VS/Battle 2–4P and variant selection | Same RR configs | Pending |
| `online` | public/private VS/Battle, RR modes `0x0A`–`0x0F`, CT `0x14`, RT `0x15` | RR config IDs and BT rows | Static checks never exercise network/login/matchmaking |

## Reproduction

From the repository root:

```sh
rtk python3 -m unittest -v tests/test_rmcj01_course_assets.py
rtk python3 scripts/audit-rmcj01-course-assets.py \
  --output private/rmcj01/coverage/rmcj01-course-coverage.json \
  --print-summary
```

The second command performs a read-only full-catalog pass and writes a new
private JSON ledger (existing output is never overwritten).  It does not launch
the game or claim runtime completion.  For any future runtime expansion, use a
bounded native menu/replay sequence, capture `KARTPAD_STATE_TRACE`, and require
`scripts/summarize-mkw-state-trace.py --require-complete`; retain the trace and
record the exact course/config ID.  Do not turn a static pass into a broad
catalog or device guarantee.
