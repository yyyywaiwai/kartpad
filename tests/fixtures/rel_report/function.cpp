// Synthetic translated control flow; contains no game-derived source or data.
#include "recomp_mod_loader.h"
extern "C" void func_8000A440(CpuContext* MKW_RESTRICT ctx)
{
    uint32_t r0 = ctx->lr;
    uint32_t r1 = ctx->gpr[1];
    uint32_t r4 = 0;
    uint32_t r28 = ctx->gpr[3];
    uint32_t r29 = ctx->gpr[29];
    uint32_t r30 = ctx->gpr[30];
    const auto saved = *ctx;
    r1 = (r1 - 32);
    ctx->gpr[1] = r1;
    r4 = MemoryInline::FlatRead32(r28);
    (void)r4;
    r30 = MemoryInline::FlatRead32((r28 + 16));
    r29 = 0;
    goto loc_8000A510;
loc_8000A4E4:
{
    observed.push_back(MemoryInline::FlatRead32(r30));
    observed.push_back(MemoryInline::FlatRead32(r30 + 4));
    r30 += 8;
    r29 += 1;
}
loc_8000A510:
{
    if (r29 < MemoryInline::FlatRead32(r28 + 12)) goto loc_8000A4E4;
}
loc_8000A51C:
{
    ctx->lr = r0;
    r1 = (r1 + 32);
    ctx->gpr[1] = r1;
    ctx->gpr[28] = saved.gpr[28];
    ctx->gpr[29] = saved.gpr[29];
    ctx->gpr[30] = saved.gpr[30];
    ctx->gpr[31] = saved.gpr[31];
    return;
}
}
// RECOMP_GUEST_ABI synthetic fixture
