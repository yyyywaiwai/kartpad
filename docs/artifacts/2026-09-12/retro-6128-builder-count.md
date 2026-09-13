# Retro Rewind 6.12.8 personal-builder function count

The pinned 6.12.8 profile expected 4,188 mod functions, but its supported inputs
produce 4,095. This made `kartpad_builder.pipeline.translate` reject both a new
translation and reuse of its cached output with `translation failed profile
validation`. Correct only `translation.expectedRetroFunctions` to 4,095; retain
all version, artifact hash, generated-function and base-function pins.

Evidence from the fresh issue #196 translation on main
`f0fdbceb1062f18b8161b25192ec0f2eb387991f`, inspected 12 September 2026:

- Staged `Code.pul` SHA-256:
  `88cd25ff08121f7c4ddb40538703f40c270f414f2dbc55a6b4b6767e62db7253`,
  matching the checked-in 6.12.8 profile.
- 29,637 generated `func_*.cpp` files; emitted graph counts 29,065 active base
  functions and 4,095 Retro Rewind functions, with Retro Rewind shards enabled.
- The prepared translator's `TranslatedBuildShardEmitter` supplies
  `modRecords.Count` to both the CMake manifest and its reported mod-function
  count. Its completed translation log independently reports 4,095.
- Read-only invocation of the real builder's cached validation against that
  output rejects the old 4,188 profile and accepts the corrected profile. Both
  the standalone and actual compiled-shard REL report guards pass.
- The regression fixture uses the real profile's mod-count pin and real guard
  validation: 4,095 succeeds, while 4,188, 4,094 and 4,096 are rejected.
- REL report regression suite: 11 tests, one skip for unavailable pinned runtime
  in the isolated worktree. Builder suite: 25 tests, one skip for absent private
  production payload. All executed tests pass; `git diff --check` passes.

No translator regeneration, app rebuild, device installation or gameplay
acceptance is claimed by this correction. The existing strict count checks
remain unchanged. Future mod updates must remeasure this count alongside their
artifact pins.

## Independent provenance review

Commit `e617a4ea4467d33f851df3b7496909ee1a8cf6cc` updated the profile from
6.12.7 to 6.12.8, replacing the archive and Code.pul pins, while leaving the
4,188 expected count unchanged. The old Code.pul was 1,723,048 bytes with SHA-256
`3a1e60f6c94e435ff672167816dbe040d0f48874bfa093ada39e468655baef72`;
the new staged input is 1,704,868 bytes and matches the new profile hash below.

The count was also derived independently of `shards.cmake`: reading the actual
`mod/translated_sources.bin` in its `MKWSRC01` version 1 format yields 4,095
records. Each record's source bytes match its stored SHA-256, and all 4,095
sources match the exact `GeneratedMarkers.ModRegistrationPattern` used by the
prepared emitter. Their virtual paths divide into 3,382 kamek, 612 overlay and
101 continuation records, totaling 4,095. `ReadModFunctions` reads this bundle
and creates one mod record per matching source; `modRecords.Count` supplies both
the graph declaration and the emitted result. This independently checks the
actual count instead of trusting the graph's declared number.

The fresh log separately records 4,095 emitted C++ functions, zero C++
translation failures, and publication of 620 added files with zero updated,
removed or unchanged files. Files and bundled function records are different
units, so the publication total is not a second function count.

`--prefer-cached-inputs` does not reuse generated C++. In the prepared CLI's
`LoadBinaryInput`, it selects a cached download only in the HTTP(S) branch.
Local input paths are read directly with `File.ReadAllBytes`. This translation
passes local Code.pul and payload paths; the script also copies the selected
Code.pul into the base profile's input path and compares the bytes before
starting translation. The staged Code.pul and emitted payload hashes match
the profile. Thus this flag does not substitute an older cached download for
these local inputs.

Exact identities inspected read-only:

| Artifact | Git commit or SHA-256 |
| --- | --- |
| Generation checkout | `f0fdbceb1062f18b8161b25192ec0f2eb387991f` |
| Pinned WiiCompiled checkout | `1912292c804ff9b1b79938de89369ec4496f9fff` |
| Generation profile JSON, before count correction | `3e034da432364be105e96345adef646b7ee10d8416de2b40f9d2a7cbde940898` |
| Staged Code.pul | `88cd25ff08121f7c4ddb40538703f40c270f414f2dbc55a6b4b6767e62db7253` |
| Emitted Retro WFC payload | `fd8f26d6af26f1a0cfaecd1e472fe744a25d75f5136910533b7c75e3eca2f1d2` |
| Prepared `TranslatedBuildShardEmitter.cs` | `f4029b9b10204c88b2b6e2041451c3a53dbecd45a7a790f55d795584ebfcf485` |
| Built `Translator.Core.dll` beside the CLI | `318a4d81c3dd493f93b82aa56e55019ad1fe18c7fc167a34426beb4d22b3f905` |
| Actual mod `translated_sources.bin` | `b1bbe03eacd5143111f32fc9ef0092bf9b9cb3b35f215cee1ed3e2b58f7da262` |

The bundle check was the smallest check that could falsify the graph count
without rerunning translation: a different record count, invalid stored hash,
or unmatched registration would have contradicted the correction. None did.
This provenance review adds no app-build or gameplay acceptance claim.
