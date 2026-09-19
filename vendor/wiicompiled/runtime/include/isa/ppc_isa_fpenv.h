#pragma once
// FPSCR[NI] (non-IEEE flush-to-zero) modeled on the host FP environment, plus
// the thread-local mirror of that state the hot paths read instead of MXCSR.

#include "ppc_isa_config.h"

#include <cstdint>

// Software-flushing Gekko's single-precision denormals per op roughly doubled the THP IDCT
// kernel's cycle count, so instead the runtime mirrors guest FPSCR[NI] into host MXCSR FTZ+DAZ
// wherever FPSCR can change (PPC_Mtfs*, fiber context switches, CpuContextScope), making per-op
// flushes free. Accepted deviations (same trade Dolphin makes): FTZ also flushes double
// denormals unlike real NI, and a pre-round-flush edge near FLT_MIN rounds via cvtsd2ss instead.
inline constexpr uint32_t kMkwMxcsrFlushToZeroBits = (1u << 15) | (1u << 6); // FTZ | DAZ


inline thread_local bool g_mkwHostNiActive = false;

// Same state in the form PpcForceSingleValueInline consumes: the pre-round subnormal threshold
// while NI is active, 0.0 (identity, `|value| < 0.0` is always false) otherwise, so that path
// needs no branch. Every writer of g_mkwHostNiActive must write this beside it in agreement.
inline constexpr double kMkwNiFlushThreshold = 0x1p-126;  // 0x3810000000000000
inline thread_local double g_mkwNiFlushThreshold = 0.0;

inline void MkwApplyHostNiMode(uint32_t fpscr) noexcept
{
    const uint32_t csr = _mm_getcsr();
    const bool wantNi = (fpscr & 0x4u) != 0;
    const uint32_t want = wantNi
        ? (csr | kMkwMxcsrFlushToZeroBits)
        : (csr & ~kMkwMxcsrFlushToZeroBits);
    if (want != csr)
        _mm_setcsr(want);
    // `want` has both bits set or both clear, so this is exactly
    // `(_mm_getcsr() & kMkwMxcsrFlushToZeroBits) != 0` after the write - the
    // mirror cannot disagree with the register even if the incoming CSR held
    // only one of the two bits.
    g_mkwHostNiActive = wantNi;
    g_mkwNiFlushThreshold = wantNi ? kMkwNiFlushThreshold : 0.0;
}

/// <summary>
/// Restores a previously captured MXCSR value and re-derives the mirror from
/// it. Every raw restore has to go through here; a bare _mm_setcsr would leave
/// the mirror describing the FP environment that was just replaced.
/// </summary>
inline void MkwRestoreHostMxcsr(uint32_t csr) noexcept
{
    _mm_setcsr(csr);
    const bool niActive = (csr & kMkwMxcsrFlushToZeroBits) != 0;
    g_mkwHostNiActive = niActive;
    g_mkwNiFlushThreshold = niActive ? kMkwNiFlushThreshold : 0.0;
}
