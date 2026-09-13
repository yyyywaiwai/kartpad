#include <cfenv>
#include <chrono>
#include <cstdint>
#include <cstdio>

extern "C" void KartPadAndroidClearScalarFlags() noexcept;
__attribute__((noinline)) void BaselineClear() noexcept {
  std::feclearexcept(FE_ALL_EXCEPT);
}
// Both paths use an opaque function boundary. This is a microbenchmark only;
// FPSR semantics are covered separately and game performance needs a scene A/B.
__attribute__((noinline)) double Measure(void (*clear)() noexcept, bool dirty) {
  constexpr unsigned count = 1000000;
  const std::uint64_t bits = FE_ALL_EXCEPT | (1ULL << 27);
  std::feclearexcept(FE_ALL_EXCEPT);
  const auto start = std::chrono::steady_clock::now();
  for (unsigned i = 0; i < count; ++i) {
    if (dirty) asm volatile("msr fpsr, %0" :: "r"(bits) : "memory");
    clear();
  }
  return double(std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now() - start).count()) / count;
}
int main() {
  fenv_t saved;
  std::fegetenv(&saved);
  // Alternate order to expose warmup/drift instead of always favoring one path.
  for (bool dirty : {false, true}) {
    for (unsigned round = 0; round < 6; ++round) {
      double baseline, candidate;
      if (round % 2) {
        candidate = Measure(KartPadAndroidClearScalarFlags, dirty);
        baseline = Measure(BaselineClear, dirty);
      } else {
        baseline = Measure(BaselineClear, dirty);
        candidate = Measure(KartPadAndroidClearScalarFlags, dirty);
      }
      std::printf("clear-benchmark dirty=%d round=%u baseline_ns=%.3f candidate_ns=%.3f\n",
                  dirty, round, baseline, candidate);
    }
  }
  std::fesetenv(&saved);
}
