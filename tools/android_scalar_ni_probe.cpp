// Source-only differential probe; contains no translated functions or game data.
#include "ppc_runtime.h"
#include <bit>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <limits>

void ShowRuntimeFatalPopup(std::string_view, std::string_view) noexcept {
    std::abort();
}

namespace {
using namespace kartpad::semantics;
using Operation = bool (*)(double&, double, double);

__attribute__((noinline)) bool BaselineMultiply(double& destination, double a, double b) {
    const auto result = EvaluatePpcScalarBinary(CurrentCpuContext()->fpscr,
        ScalarFpBinaryOperation::Multiply, a, Force25Bit(b), true);
    CpuContext* cpu = CurrentCpuContext();
    cpu->fpscr = result.fpscr;
    MkwApplyHostNiMode(cpu->fpscr);
    if (result.write_destination) destination = result.value;
    return result.write_destination;
}

__attribute__((noinline)) bool CandidateMultiply(double& destination, double a, double b) {
    return PpcFmulsStateInline(destination, a, b);
}

void Require(bool condition, const char* message) {
    if (!condition) { std::fprintf(stderr, "FAIL: %s\n", message); std::exit(1); }
}

double Benchmark(Operation operation, CpuContext& cpu) {
    CpuContextScope scope(&cpu);
    double value = 1.25;
    const auto start = std::chrono::steady_clock::now();
    for (unsigned i = 0; i < 500000; ++i)
        operation(value, 1.25 + (i & 15) * 0.125, 0.75);
    Require(std::isfinite(value), "benchmark result");
    return std::chrono::duration<double, std::milli>(
        std::chrono::steady_clock::now() - start).count();
}
}

int main() {
    CpuContext cpu{};
    cpu.gpr[1] = 0x80001000;
    unsigned checks = 0;
    const double values[] = {0.0, -0.0, 1.0, -1.25, 0x1p-149, -0x1p-149,
        0x1p-1022, 0x1p127, 0x1p1023, std::numeric_limits<double>::infinity(),
        -std::numeric_limits<double>::infinity(),
        std::bit_cast<double>(0x7ff8000000000123ULL),
        std::bit_cast<double>(0x7ff0000000000123ULL)};
    for (unsigned initial : {0u, fpscr::NI, fpscr::VE, fpscr::NI | fpscr::VE}) {
        for (double a : values) for (double b : values) {
            cpu.fpscr = initial;
            CpuContextScope scope(&cpu);
            double expected = 42.0, actual = 42.0;
            const bool expectedWrite = BaselineMultiply(expected, a, b);
            const auto expectedFpscr = cpu.fpscr;
            const auto expectedMode = _mm_getcsr() & kMkwMxcsrFlushToZeroBits;
            cpu.fpscr = initial;
            MkwApplyHostNiMode(initial);
            const bool actualWrite = CandidateMultiply(actual, a, b);
            Require(expectedWrite == actualWrite, "destination suppression");
            Require(std::bit_cast<uint64_t>(expected) == std::bit_cast<uint64_t>(actual),
                    "result bits including NaN and signed zero");
            Require(expectedFpscr == cpu.fpscr, "FPSCR exception and status bits");
            Require(expectedMode == (_mm_getcsr() & kMkwMxcsrFlushToZeroBits), "host NI mode");
            Require(g_mkwHostNiActive == ((initial & fpscr::NI) != 0), "TLS mode mirror");
            ++checks;
        }
    }
    {
        cpu.fpscr = 0;
        CpuContextScope scope(&cpu);
        double value = 0;
        PpcCommitScalarFpInline(value, {1.0, fpscr::NI, 0, true});
        Require(g_mkwHostNiActive, "explicit NI enable transition");
        PpcCommitScalarFpInline(value, {1.0, 0, 0, true});
        Require(!g_mkwHostNiActive, "explicit NI disable transition");
    }
    cpu.fpscr = 0;
    const double before = Benchmark(BaselineMultiply, cpu);
    const double after = Benchmark(CandidateMultiply, cpu);
    std::printf("scalar-ni differential=passed cases=%u baseline_ms=%.3f candidate_ms=%.3f\n",
                checks, before, after);
}
