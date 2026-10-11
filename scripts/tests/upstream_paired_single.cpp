// Exercise the maintained runtime's ARM64 paired-single implementation against
// scalar arithmetic, including lane ordering and single-NaN payload rules.
#include "isa/ppc_isa_float.h"
#include <cassert>
#include <bit>
#include <cstdio>

static void equal(double packed, float a, float b) {
    assert(PpcBitCastToU32Inline(PpcGetPs0Inline(packed)) == std::bit_cast<uint32_t>(a));
    assert(PpcBitCastToU32Inline(PpcGetPs1Inline(packed)) == std::bit_cast<uint32_t>(b));
}

int main() {
    const auto originalControl = MkwGetHostFpControl();
    MkwSetHostFpControl(originalControl & ~kMkwFpControlFlushToZeroBits);
    for (int i = -5000; i < 5000; ++i) {
        const float a = i * 0.03125f, b = (i + 7001) * 0.015625f;
        const float c = (i % 127 + 128) * 0.0625f, d = (i % 61 + 62) * 0.125f;
        const auto lhs = PpcPackPairedInline(a, b), rhs = PpcPackPairedInline(c, d);
        equal(lhs, a, b);
        equal(PPC_PsAddInline(lhs, rhs), a + c, b + d);
        equal(PPC_PsSubInline(lhs, rhs), a - c, b - d);
        equal(PPC_PsMulInline(lhs, rhs), a * c, b * d);
        equal(PPC_PsDivInline(lhs, rhs), a / c, b / d);
        equal(PPC_PsMaddInline(lhs, rhs, lhs), std::fma(a, c, a), std::fma(b, d, b));
        equal(PPC_PsMsubInline(lhs, rhs, lhs), std::fma(a, c, -a), std::fma(b, d, -b));
        equal(PPC_PsMadds0Inline(lhs, rhs, lhs), std::fma(a, c, a), std::fma(b, c, b));
        equal(PPC_PsMadds1Inline(lhs, rhs, lhs), std::fma(a, d, a), std::fma(b, d, b));
        equal(PPC_PsMerge01Inline(lhs, rhs), a, d);
        equal(PPC_PsMerge10Inline(lhs, rhs), b, c);
    }
    for (uint32_t bits : {0x7fc12345u, 0xffc54321u, 0x7f812345u}) {
        const auto nan = std::bit_cast<float>(bits);
        const auto result = PPC_PsAddInline(PpcPackPairedInline(nan, 3), PpcPackPairedInline(2, nan));
        const auto quiet = std::bit_cast<float>(bits | 0x00400000u);
        equal(result, quiet, quiet);
    }
    equal(PPC_PsNegInline(PpcPackPairedInline(0.0f, -0.0f)), -0.0f, 0.0f);
    MkwSetHostFpControl(originalControl);
    std::puts("PASS: 110,000 paired-single scalar comparisons, lane order, signed zero and single-NaN payloads");
}
