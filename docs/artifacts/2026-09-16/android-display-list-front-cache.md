# Private display-list front-cache candidate113

Current build111 CPU sample addresses in GX__CallDisplayList resolve primarily
to std::unordered_map::find in ProbeDlScanCache, with a smaller layout-hash cost.
The candidate adds256 key/pointer slots ahead of the existing map (about4KiB).
It retains canonical-address/layout/content/write-generation validation. Map
rehash preserves element addresses; the only erase path clears the front before
freeing records. Record replacement remains subject to original identity checks.

Extracted actual probe/store code passed host AddressSanitizer and UBSan tests
for source mutation, alias addresses, layout changes, untracked writes, unchanged
writes, front collisions, map growth, eviction and repopulation. Synthetic Pixel
lookup tests improve small reused working sets and can regress a few percent at
4096 entries with almost no front hits. They are not gameplay FPS evidence.

Build113 includes the112 logging additions plus bounded interval counters:
probes, front_hits, validated_hits, evictions, entries and command_bytes. It was
built, APK-audited, certificate-matched and installed in place. All34 archived
NAND, identity and preference files matched byte-for-byte immediately after
installation. No data clearing, public release or scalar arithmetic experiment
was included. APK SHA256:
57f494a101811f16d9544b4623d86b6a1eabebbdfec642668c37149d7fc3fdf6

The owner reports continued drops after Retro menus and racing. Fresh logs
confirm48.08FPS at15:57:09,p95=31.85ms,p99=42.80ms,queue0,resolution2x.
That preceding300-present interval had283472 probes,55476 front hits(19.6%),
107165 validated hits(37.8%),zero evictions,3416 entries. Game-thread CPU was
15.008ms per present averaged over5.304s; render-worker encoding averaged
6.134ms wall/5.699ms CPU,present_total1.640ms. These intervals differ from the
short FPS rolling window (48 samples), so they do not identify the exact slow
frame. They also do not measure GPU execution time.

No useful FPS improvement has been established. The owner agreed to another
live CPU capture; the first armed attempt saw Next Race rather than an active
race and correctly did not record the result screen. Subsequent bounded waits also saw the results menu, so no current-build
CPU profile has yet been recorded. A new attempt was armed after the owner
agreed to resume. All24 file-backed allocated ELF sections of the saved113
debug library match the113 APK exactly (symbols113-match.json).
Phone remains build113,CPU-driver marker absent. Raw data and state archives
remain private under build/android-full-race and build/android-dl-front-cache.

## Follow-up decision: do not enlarge the front cache yet

Source inspection confirms that probes include register-only lists, which return
before StoreDlScanCache, and nested draw lists, which are deliberately excluded
from storage. Therefore a 37.8% validated hit rate is not evidence that capacity
is insufficient. The slow interval had zero evictions and3416 of8192 entries.
Increasing capacity or front slots does not address these intentional misses.
The current counters cannot distinguish unstored lists from mutated content.

The earlier full-race profile attributed2.46% of all app CPU self samples to
GX__CallDisplayList, versus53.92% to the game thread. That is approximately4.6%
of game-thread samples for the entire function, of which lookup is only a part.
These sample shares are not wall-time savings and come from build111, but they
make a large overall gain from this lookup-only candidate implausible. Do not
continue sizing this cache on the assumption that it will cure the drops.

Next discriminating hardware comparison remains the same active race at2x and
1x resolution, with opponents/items, plus a current slow-race CPU profile. The
resolution comparison changes pixel workload without rewriting guest arithmetic;
it must be owner-coordinated and cannot be replaced by a capped ghost run.
At16:19 the capture preflight again saw Next Race, and did not start simpleperf.
No recorder is left running by that attempt. Build113 and owner state unchanged.
