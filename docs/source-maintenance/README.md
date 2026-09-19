# Maintaining WiiCompiled source

WiiCompiled is created by [patchzyy and contributors](https://github.com/patchzyy/wiicompiled).
KartPad keeps its existing product repository and attribution. Its maintained
runtime source is in the [WiiCompiled fork](https://github.com/chrissotraidis/wiicompiled),
which belongs to GitHub's upstream fork network.

## Source locations

| Consumer | Editable source | Maintained fork branch |
|---|---|---|
| Translator and native-registration baseline | `vendor/wiicompiled/translator` and `vendor/wiicompiled/runtime/src` | Git subtree in KartPad |
| macOS runtime and Aurora | `vendor/runtimes/macos` | `kartpad-macos` |
| iOS and iPadOS runtime and Aurora | `vendor/runtimes/ios` | `kartpad-ios` |
| Android runtime and Aurora | `vendor/runtimes/android` | `kartpad-android` |
| Experimental tvOS runtime and Aurora | `vendor/runtimes/tvos` | `kartpad-tvos` |

```sh
git submodule update --init --recursive
```

Git submodule commits pin each runtime exactly; branch tips never select a build
implicitly. All platform branches initially derive from WiiCompiled commit
`1912292c804ff9b1b79938de89369ec4496f9fff`. The existing platform differences are
preserved, including memory allocation, controller and renderer behavior. This
migration does not update upstream or consolidate those differences.

Edit the runtime source in the relevant submodule, on a local branch. Build
preparation copies tracked source, including local tracked edits; add new source
files in that submodule before testing. The builder fingerprints tracked edits
inside submodules, and artifact provenance fingerprints the prepared runtime.
Commit and push the reviewed source branch, then stage its gitlink in KartPad:

```sh
git add vendor/runtimes/ios
```

Preparation rejects a submodule HEAD that differs from KartPad's staged pin; it
will not reset a developer's checkout automatically. Profile headers, sse2neon
and KartPad's Android trace header remain explicit generated/copied inputs.
Preparation scripts retain their arguments and output layout and no longer apply
platform runtime patches. Source archives recursively include the pinned source.

The translator helper retains its historical name
`scripts/prepare-patched-translator.sh`, but copies the tracked subtree without
patch replay. **Do not replace its native-registration source with a platform
runtime:** that would change translator inputs. Translator fixes are edited and
committed in KartPad's subtree, not in the runtime fork's upstream translator copy.

Migration acceptance is tracked in [VALIDATION.md](VALIDATION.md). The 99 migrated
patch files have been retired from this candidate; Git history and the rollback
backup preserve them. Remaining patches serve separate dependencies or test inputs.

## Upstream comparison, updates and contributions

For a runtime change, use the relevant fork branch and ordinary Git comparison
against the recorded upstream base. Preserve the upstream licenses, per-file
notices, Aurora attribution and commit ancestry. The fork's `KARTPAD.md` records
how the source was materialized and links back to KartPad.

For the translator subtree:

```sh
git fetch https://github.com/patchzyy/wiicompiled.git 1912292c804ff9b1b79938de89369ec4496f9fff
git subtree split --prefix=vendor/wiicompiled -b review/wiicompiled-source
git diff 1912292c804ff9b1b79938de89369ec4496f9fff review/wiicompiled-source -- translator
```

Prepare upstream contributions as focused fixes and tests on an upstream-based
branch in the fork. Do not send the entire KartPad platform delta as a bug fix.
For upstream updates, merge the reviewed revision into an isolated platform
branch, test it, then update only the accepted KartPad gitlink. Shared fixes may
be cherry-picked between affected platform branches. Translator updates use a
reviewed subtree merge. Upstream upgrades remain separate from this migration.

See [migration and rollback gates](MIGRATION.md). No new source pin establishes
physical gameplay acceptance by itself.
