# Packed vertex attribute read width

Source review of the seven Android geometry reports found an independent, locally
reproducible out-of-range read in Aurora's generated WGSL helpers. It does not yet
explain those reports.

`raw_fetch_u8_3` and `load_u24` requested four bytes through `load_u32_raw`, then
used only three. With byte offset 1 in the last bound storage word, all three
attribute bytes are valid but the fourth byte accesses the following, unbound
word. Renderer Validation normally enables robustness, but normal release mode
explicitly disables it. The shader should not depend on robustness for a valid
three-byte attribute.

A dedicated `load_u24_raw` reads one word for offsets 0/1 and two only for offsets
2/3. Both existing helpers use it; four-byte reads and endian conversion are
unchanged. This covers packed three-component byte positions/normals, RGB8 and
RGBA6. The patch is applied by the common iOS preparation path (also used by
Android and tvOS), and by the G7/macOS preparation path.

## Verification

- `scripts/test-packed-vertex-read-width.py <prepared-runtime>` extracts the
  actual WGSL helpers, maps their integer-only syntax to C++, and runs checked
  storage accesses across 2,048 data/offset cases at both O0 and O2 under
  AddressSanitizer and UndefinedBehaviorSanitizer. Endian values and the exact
  accessed-word range pass. The original four-byte helper is a negative control:
  its byte-1 access in a one-word binding throws an out-of-range error.
- The existing renderer probe extracted all actual patched WGSL helpers, compiled
  them through pinned Dawn, and ran on Apple M3 Max / macOS 26.6.2 (25G83). All
  eight compute/indexed-draw checks passed: 4,096 comparisons per check, scalar
  and vec4 uniforms, robustness disabled/enabled. Both changed helpers are
  called by the compute entry point. Helper SHA-256:
  `6dc4597696984963cda9d8da250afe78855e4120f6bffe40ac2e6ec442d6b285`.
- The patch applies to pinned upstream with zero fuzz. Shell syntax and diff
  whitespace checks pass.

This is a read-width correction, not an Android driver fix or gameplay acceptance.
Aurora binds whole-frame vertex/storage buffers; ordinary attribute boundaries
inside those allocations do not cross the actual binding. No submitted report
establishes a draw at the final binding word. The seven graphics issues remain
open, and no APK or Apple package is changed by merging this source correction.

The inspected pinned Dawn source already includes the Qualcomm split-compute,
resolve, scalarized min/max/clamp and direct-variable-access workarounds, plus the
ARM pack/unpack workaround. Adding those toggles again or changing all Adreno
behavior is not justified by this review.
