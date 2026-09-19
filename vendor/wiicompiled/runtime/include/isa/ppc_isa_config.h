#pragma once

#include <atomic>
#include <cstdint>

#define MKW_RESTRICT __restrict
#include <immintrin.h>

inline constexpr bool MkwStateFreeAbiEnabled(uint32_t) noexcept
{
    return true;
}

#define MKW_PPC_FORCE_INLINE __forceinline
#define MKW_PPC_NO_INLINE __declspec(noinline)
#define MKW_PPC_ALWAYS_INLINE_BODY __attribute__((always_inline))
#define MKW_PPC_COLD __attribute__((cold))
#define MKW_PPC_INTERNAL_CALL __regcall


using MkwStateFreeResult2 = uint64_t __attribute__((ext_vector_type(2)));
