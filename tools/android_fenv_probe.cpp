// Source-only Android ARM64 diagnostic. Not used by the game runtime.
// Compares Bionic's public fenv calls with equivalent FPSR register operations.
#include <cfenv>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>

#if !defined(__ANDROID__) || !defined(__aarch64__)
#error This probe requires Android ARM64.
#endif

static_assert(FE_ALL_EXCEPT == 0x9f);
static uint64_t ReadStatus() {
  uint64_t value;
  asm volatile("mrs %0, fpsr" : "=r"(value) :: "memory");
  return value;
}
static void WriteStatus(uint64_t value) {
  asm volatile("msr fpsr, %0" :: "r"(value) : "memory");
}
static uint64_t ReadControl() {
  uint64_t value;
  asm volatile("mrs %0, fpcr" : "=r"(value) :: "memory");
  return value;
}
static void InlineClear(int mask) { WriteStatus(ReadStatus() & ~(mask & FE_ALL_EXCEPT)); }
static int InlineTest(int mask) { return ReadStatus() & mask & FE_ALL_EXCEPT; }
__attribute__((noinline)) static int CaptureAndClear() {
  const auto status = ReadStatus();
  WriteStatus(status & ~uint64_t(FE_ALL_EXCEPT));
  return status & (FE_OVERFLOW | FE_UNDERFLOW | FE_INEXACT);
}
static void RequireAt(bool value, int line) {
  if (!value) { std::fprintf(stderr, "fenv_probe failed at line %d\n", line); std::exit(1); }
}
#define Require(value) RequireAt(value, __LINE__)

__attribute__((noinline)) int LibraryCycle(double a, double b) {
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double value = a / b;
  (void)value;
  const int flags = std::fetestexcept(FE_OVERFLOW | FE_UNDERFLOW | FE_INEXACT);
  std::feclearexcept(FE_ALL_EXCEPT);
  return flags;
}
__attribute__((noinline)) int RegisterCycle(double a, double b) {
  InlineClear(FE_ALL_EXCEPT);
  volatile double value = a / b;
  (void)value;
  const int flags = InlineTest(FE_OVERFLOW | FE_UNDERFLOW | FE_INEXACT);
  InlineClear(FE_ALL_EXCEPT);
  return flags;
}
__attribute__((noinline)) int CombinedCycle(double a, double b) {
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double value = a / b;
  (void)value;
  return CaptureAndClear();
}
static double Benchmark(int (*cycle)(double, double)) {
  unsigned checksum = 0;
  const auto begin = std::chrono::steady_clock::now();
  for (unsigned i = 0; i < 1000000; ++i) checksum += cycle(1.0 + (i & 15), 3.0);
  const auto elapsed = std::chrono::duration<double, std::milli>(
      std::chrono::steady_clock::now() - begin).count();
  // A memory clobber does not constrain register-only floating-point work.
  // Reject a prototype which the production compiler flags move before clear.
  if (checksum == 0) return -1.0;
  return elapsed;
}
int main() {
  fenv_t saved;
  Require(std::fegetenv(&saved) == 0);
  const auto control = ReadControl();
  unsigned cases = 0;
  for (unsigned seed = 0; seed < 128; ++seed) {
    const uint64_t status = (seed & 31) | ((seed & 32) << 2) |
                            (uint64_t(seed & 64) << 21); // Exception flags + QC.
    WriteStatus(status);
    Require(CaptureAndClear() == (status & (FE_OVERFLOW | FE_UNDERFLOW | FE_INEXACT)));
    Require(ReadStatus() == (status & ~uint64_t(FE_ALL_EXCEPT)));
    for (int mask = 0; mask < 256; ++mask) {
      WriteStatus(status);
      const int expected = std::fetestexcept(mask);
      Require(expected == InlineTest(mask));
      std::feclearexcept(mask);
      const auto after = ReadStatus();
      WriteStatus(status);
      InlineClear(mask);
      Require(after == ReadStatus() && control == ReadControl());
      ++cases;
    }
  }
  std::fesetenv(&saved);
  for (unsigned round = 0; round < 4; ++round) {
    const auto first = Benchmark(round & 1 ? CombinedCycle : LibraryCycle);
    const auto second = Benchmark(round & 1 ? LibraryCycle : CombinedCycle);
    const auto library = round & 1 ? second : first;
    const auto combined = round & 1 ? first : second;
    Require(library > 0 && combined > 0);
    std::printf("fenv_probe combined_round=%u library_ms=%.3f combined_ms=%.3f ratio=%.3f\n",
                round, library, combined, combined / library);
  }
  for (unsigned round = 0; round < 4; ++round) {
    double library, registers;
    if (round & 1) { registers = Benchmark(RegisterCycle); library = Benchmark(LibraryCycle); }
    else { library = Benchmark(LibraryCycle); registers = Benchmark(RegisterCycle); }
    Require(library > 0);
    if (registers < 0) {
      std::printf("fenv_probe status_cases=%u register_path=rejected_lost_arithmetic_flags library_ms=%.3f\n",
                  cases, library);
      break;
    }
    std::printf("fenv_probe status_cases=%u round=%u library_ms=%.3f register_ms=%.3f ratio=%.3f\n",
                cases, round, library, registers, registers / library);
  }
  std::fesetenv(&saved);
}
