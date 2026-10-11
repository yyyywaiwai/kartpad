#include <bit>
#include <cfenv>
#include <cstdint>
#include <cstdio>
#include <random>
// Host stand-ins for the Android helpers; same flag set and clearing contract.
extern "C" int KartPadAndroidCaptureScalarFlags() noexcept {
  const int f = std::fetestexcept(FE_OVERFLOW | FE_UNDERFLOW | FE_INEXACT);
  std::feclearexcept(FE_ALL_EXCEPT);
  return f;
}
extern "C" void KartPadAndroidClearScalarFlags() noexcept { std::feclearexcept(FE_ALL_EXCEPT); }
using Fn = void (*)(int, std::uint32_t, double, double, double, bool, double*, std::uint32_t*, std::uint32_t*, bool*);
extern "C" void baseline_eval(int, std::uint32_t, double, double, double, bool, double*, std::uint32_t*, std::uint32_t*, bool*);
extern "C" void candidate_eval(int, std::uint32_t, double, double, double, bool, double*, std::uint32_t*, std::uint32_t*, bool*);
constexpr std::uint32_t kStatus = 0x80000000u | 0x10000000u | 0x08000000u | 0x02000000u;  // FX OX UX XX
constexpr std::uint32_t kEnables = 0x40u | 0x20u | 0x08u;                                  // OE UE XE
std::mt19937_64 rng(0x4b617274u);
double operand() {
  switch (rng() % 8) {
  case 0: return std::bit_cast<double>(rng());
  case 1: return static_cast<double>(std::bit_cast<float>(static_cast<std::uint32_t>(rng())));
  case 2: { const std::uint64_t e = 1 + rng() % 60; return std::bit_cast<double>((rng() & 0x800fffffffffffffULL) | (e << 52)); }
  case 3: { const std::uint64_t e = 2040 + rng() % 7; return std::bit_cast<double>((rng() & 0x800fffffffffffffULL) | (e << 52)); }
  case 4: { const double s[] = {0.0, -0.0, 1.0, -1.0, 0x1p-149, 0x1p-126, 0x1p127, 3.4028234663852886e38, 1e308, 4.9e-324, __builtin_inf(), -__builtin_inf(), std::bit_cast<double>(0x7ff4000000000000ULL), std::bit_cast<double>(0x7ff8000000000001ULL)}; return s[rng() % 14]; }
  case 5: return static_cast<double>(static_cast<std::int32_t>(rng() % 2001) - 1000) / 8.0;
  default: return static_cast<double>(std::bit_cast<float>(static_cast<std::uint32_t>((rng() & 0x807fffffu) | ((96 + rng() % 64) << 23))));
  }
}
int main(int argc, char** argv) {
  const unsigned long cases = argc > 1 ? std::strtoul(argv[1], nullptr, 10) : 2000000;
  const int modes[] = {FE_TONEAREST, FE_TOWARDZERO, FE_UPWARD, FE_DOWNWARD};
  unsigned long mismatches = 0, masked = 0, tracked = 0;
  for (unsigned long i = 0; i < cases; ++i) {
    const int op = static_cast<int>(rng() % 7);
    const bool single = (rng() & 1) != 0;
    std::uint32_t fpscr = static_cast<std::uint32_t>(rng()) & ~0x00000004u;  // NI clear or set via bit 2 below
    if (rng() % 4 != 0) fpscr &= ~kEnables;                  // mostly the game's configuration
    if (rng() % 8 == 0) fpscr |= 0x4u;                       // NI
    // Architecturally consistent summaries: VX = OR of VX*; FEX = OR of enabled exceptions.
    {
      const std::uint32_t vxAny = 0x01f80700u;
      fpscr &= ~0x60000000u;
      if (fpscr & vxAny) fpscr |= 0x20000000u;
      const bool fex = ((fpscr & vxAny) && (fpscr & 0x80u)) || ((fpscr & 0x10000000u) && (fpscr & 0x40u)) ||
                       ((fpscr & 0x08000000u) && (fpscr & 0x20u)) || ((fpscr & 0x04000000u) && (fpscr & 0x10u)) ||
                       ((fpscr & 0x02000000u) && (fpscr & 0x08u));
      if (fex) fpscr |= 0x40000000u;
    }
    const double a = operand(), b = operand(), c = operand();
    const int mode = modes[rng() % 4];
    // Leave arbitrary host flags set before each call to prove neither variant depends on them.
    std::feclearexcept(FE_ALL_EXCEPT);
    if (rng() & 1) std::feraiseexcept(FE_INEXACT | FE_OVERFLOW);
    std::fesetround(mode);
    double vb, vc; std::uint32_t fb, fc, eb, ec; bool wb, wc;
    baseline_eval(op, fpscr, a, b, c, single, &vb, &fb, &eb, &wb);
    std::feclearexcept(FE_ALL_EXCEPT);
    if (rng() & 1) std::feraiseexcept(FE_INEXACT | FE_UNDERFLOW);
    candidate_eval(op, fpscr, a, b, c, single, &vc, &fc, &ec, &wc);
    std::fesetround(FE_TONEAREST);
    const bool enables = (fpscr & kEnables) != 0;
    const bool strict = argc > 2;  // control: demand exact status bits everywhere
    const std::uint32_t mask = (enables || strict) ? 0xffffffffu : ~kStatus;
    (enables ? tracked : masked) += 1;
    const bool same = std::bit_cast<std::uint64_t>(vb) == std::bit_cast<std::uint64_t>(vc) && wb == wc &&
                      (fb & mask) == (fc & mask) && (eb & mask) == (ec & mask);
    if (!same && ++mismatches <= 10)
      std::printf("MISMATCH op=%d single=%d fpscr=%08x mode=%d a=%a b=%a c=%a value %a/%a fpscr %08x/%08x exc %08x/%08x write %d/%d\n",
                  op, single, fpscr, mode, a, b, c, vb, vc, fb, fc, eb, ec, wb, wc);
  }
  std::printf("cases=%lu enabled_exact=%lu enables_clear_masked=%lu mismatches=%lu\n", cases, tracked, masked, mismatches);
  return mismatches == 0 ? 0 : 1;
}
