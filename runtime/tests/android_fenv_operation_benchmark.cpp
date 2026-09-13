#include "android_fenv_case.h"
#include <chrono>
#include <cstdio>
#include <cfenv>
#include <utility>
__attribute__((noinline)) double Measure(AndroidFpEvaluator fn, unsigned op) {
  constexpr unsigned count = 100000;
  std::uint64_t checksum = 0;
  const auto start = std::chrono::steady_clock::now();
  for (unsigned i = 0; i < count; ++i) {
    const auto result = fn(op, 0, 1.125 + (i & 7), 0.375, 0.75);
    checksum ^= result.value ^ result.fpscr ^ result.host_flags;
  }
  const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now() - start).count();
  std::printf(" checksum=%llu", static_cast<unsigned long long>(checksum));
  return double(ns) / count;
}
int main() {
  fenv_t saved;
  std::fegetenv(&saved);
  for (unsigned round = 0; round < 4; ++round) {
    for (unsigned op = 0; op < 13; ++op) {
      double base, candidate;
      std::printf("operation round=%u op=%u", round, op);
      if (round % 2) {
        candidate = Measure(CandidateFp, op); base = Measure(ReferenceFp, op);
      } else {
        base = Measure(ReferenceFp, op); candidate = Measure(CandidateFp, op);
      }
      std::printf(" baseline_ns=%.3f candidate_ns=%.3f\n", base, candidate);
    }
  }
  std::fesetenv(&saved);
}
