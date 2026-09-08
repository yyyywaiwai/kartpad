#include "android_fenv_case.h"
#include <array>
#include <bit>
#include <cfenv>
#include <cstdio>
#include <cstdint>
int main() {
  fenv_t saved;
  std::fegetenv(&saved);
  std::uint64_t seed = 0x719345631;
  auto next = [&] { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; return seed; };
  constexpr std::array<std::uint64_t, 16> special = {0, 0x8000000000000000ULL,
    1, 0x8000000000000001ULL, 0x0010000000000000ULL, 0x7fefffffffffffffULL,
    0x7ff0000000000000ULL, 0xfff0000000000000ULL, 0x7ff8000000000001ULL,
    0x7ff0000000000001ULL, 0xfff0000000000001ULL, 0x3ff0000000000000ULL,
    0xbff0000000000000ULL, 0x4008000000000000ULL, 0x380ffffffffff000ULL, 0x47effffff0000000ULL};
  unsigned cases = 0;
  for (int rounding : {FE_TONEAREST, FE_UPWARD, FE_DOWNWARD, FE_TOWARDZERO}) {
    std::fesetround(rounding);
    for (unsigned i = 0; i < 10000; ++i) {
      const double a = std::bit_cast<double>(i < 4096 ? special[i % 16] : next());
      const double b = std::bit_cast<double>(i < 4096 ? special[(i / 16) % 16] : next());
      const double c = std::bit_cast<double>(i < 4096 ? special[(i / 256) % 16] : next());
      const std::uint32_t fpscr = i % 3 == 0 ? 0 : i % 3 == 1 ? 4 : next();
      for (unsigned op = 0; op < 13; ++op) {
        std::feclearexcept(FE_ALL_EXCEPT);
        const auto expected = ReferenceFp(op, fpscr, a, b, c);
        std::feclearexcept(FE_ALL_EXCEPT);
        const auto actual = CandidateFp(op, fpscr, a, b, c);
        if (actual.value != expected.value || actual.fpscr != expected.fpscr ||
            actual.exception != expected.exception || actual.write != expected.write ||
            actual.host_flags != expected.host_flags || std::fegetround() != rounding) {
          std::printf("FAIL case=%u op=%u rounding=%d value_match=%d fpscr_match=%d flags_match=%d\n",
            i, op, rounding, actual.value == expected.value, actual.fpscr == expected.fpscr,
            actual.host_flags == expected.host_flags);
          std::fesetenv(&saved);
          return 1;
        }
        ++cases;
      }
    }
  }
  std::fesetenv(&saved);
  std::printf("PASS Android fenv differential cases=%u; values, FPSCR, exceptions, destination writes, host flags and rounding match\n", cases);
}
