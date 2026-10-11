#include "ppc_runtime.h"
#include <array>
#include <bit>
#include <chrono>
#include <thread>

extern "C" bool baseline(unsigned, double&, double, double, double);
extern "C" bool candidate(unsigned, double&, double, double, double);
void ShowRuntimeFatalPopup(std::string_view title, std::string_view message) noexcept {
    std::fprintf(stderr, "runtime fatal: %.*s %.*s\n",
                 int(title.size()), title.data(), int(message.size()), message.data());
    std::abort();
}

struct Result {
    uint64_t value;
    uint32_t fpscr;
    int flags;
    bool write;
    uint64_t raw;
};
using Fn = bool (*)(unsigned, double&, double, double, double);

Result run(Fn fn, unsigned op, uint32_t fpscr, double a, double b, double c) {
    CpuContext cpu{};
    cpu.gpr[1] = 0x80001000;
    cpu.fpscr = fpscr;
    CpuContextScope scope(&cpu);
    std::feclearexcept(FE_ALL_EXCEPT);
    if (fpscr & 1u) std::feraiseexcept(FE_INEXACT | FE_UNDERFLOW);
    uint64_t before;
    asm volatile("mrs %0, fpsr" : "=r"(before) :: "memory");
    before = (before & ~(uint64_t{1} << 27)) | ((fpscr & 2u) ? (uint64_t{1} << 27) : 0u);
    asm volatile("msr fpsr, %0" :: "r"(before) : "memory");
    double d = std::bit_cast<double>(uint64_t{0x402a000000000000});
    bool write = fn(op, d, a, b, c);
    uint64_t raw;
    asm volatile("mrs %0, fpsr" : "=r"(raw) :: "memory");
    if ((raw & (uint64_t{1} << 27)) != (before & (uint64_t{1} << 27))) {
        std::fprintf(stderr, "QC changed op=%u before=%llx after=%llx a=%llx b=%llx\n", op,
            (unsigned long long)before, (unsigned long long)raw,
            (unsigned long long)std::bit_cast<uint64_t>(a), (unsigned long long)std::bit_cast<uint64_t>(b));
        std::abort();
    }
    return {std::bit_cast<uint64_t>(d), cpu.fpscr, std::fetestexcept(FE_ALL_EXCEPT), write, raw};
}

uint64_t rng(uint64_t& x) {
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return x;
}

void check(uint64_t seed) {
    const std::array<uint64_t, 12> edges = {
        0, 0x8000000000000000ULL, 0x3ff0000000000000ULL, 0xbff0000000000000ULL,
        0x7ff0000000000000ULL, 0xfff0000000000000ULL, 0x7ff8000000000001ULL,
        0x7ff0000000000001ULL, 1, 0x0010000000000000ULL, 0x7fefffffffffffffULL,
        0x3810000000000000ULL};
    unsigned checks = 0;
    CpuContext outer{};
    outer.gpr[1] = 0x80002000;
    CpuContextScope outerScope(&outer);
    for (int mode : {FE_TONEAREST, FE_DOWNWARD, FE_UPWARD, FE_TOWARDZERO}) {
        std::fesetround(mode);
        for (unsigned i = 0; i < 20000; ++i) {
            double a = std::bit_cast<double>(i < edges.size() ? edges[i] : rng(seed));
            double b = std::bit_cast<double>(i < edges.size() ? edges[(i + 3) % edges.size()] : rng(seed));
            double c = std::bit_cast<double>(i < edges.size() ? edges[(i + 7) % edges.size()] : rng(seed));
            if (i >= 4000 && i < 12000) {
                a = static_cast<double>(std::bit_cast<float>(uint32_t(rng(seed))));
                b = static_cast<double>(std::bit_cast<float>(uint32_t(rng(seed))));
            } else if (i >= 12000) {
                // Exercise exactness boundary gaps 27/28/29/30 and both range ends.
                unsigned ae = 897u + unsigned(rng(seed) % 254u);
                unsigned be = ae + unsigned(i % 31u);
                if (be > 1150u) be = 1150u;
                const uint64_t mask = 0x800fffffe0000000ULL;
                a = std::bit_cast<double>((rng(seed) & mask) | (uint64_t(ae) << 52));
                b = std::bit_cast<double>((rng(seed) & mask) | (uint64_t(be) << 52));
            }
            if (i % 11u == 0) a = std::bit_cast<double>(rng(seed) & 0x8000000000000000ULL);
            if (i % 13u == 0) b = std::bit_cast<double>(rng(seed) & 0x8000000000000000ULL);
            uint32_t fpscr = uint32_t(rng(seed));
            for (unsigned op = 0; op < 14; ++op) {
                auto x = run(baseline, op, fpscr, a, b, c);
                auto y = run(candidate, op, fpscr, a, b, c);
                if (x.value != y.value || x.fpscr != y.fpscr || x.flags != y.flags ||
                    x.write != y.write || x.raw != y.raw || g_currentCpuContext != &outer || std::fegetround() != mode) {
                    std::fprintf(stderr,
                        "mismatch op=%u case=%u mode=%d a=%016llx b=%016llx fpscr_in=%08x "
                        "x=%016llx/%08x/%x/%d/raw%llx y=%016llx/%08x/%x/%d/raw%llx\n",
                        op, i, mode, (unsigned long long)std::bit_cast<uint64_t>(a),
                        (unsigned long long)std::bit_cast<uint64_t>(b), fpscr,
                        (unsigned long long)x.value, x.fpscr, x.flags, x.write,
                        (unsigned long long)x.raw, (unsigned long long)y.value,
                        y.fpscr, y.flags, y.write, (unsigned long long)y.raw);
                    std::abort();
                }
                ++checks;
            }
        }
    }
    std::printf("PASS %u adapter differential cases; nested context and rounding preserved\n", checks);
}

int main() {
    std::thread t([] { check(0xabcdef01); });
    check(0x12345678);
    t.join();

    CpuContext cpu{};
    cpu.gpr[1] = 0x80001000;
    CpuContextScope scope(&cpu);
    std::fesetround(FE_TONEAREST);
    // Alternate order to expose drift. Microbenchmark nanoseconds are not game FPS.
    struct Bench {
        unsigned op;
        double a, b;
        const char* label;
    };
    for (auto test : {Bench{0, 1.25, 2.5, "add-fast"},
                      Bench{2, 1.25, 2.5, "mul-fast"},
                      Bench{0, 1.0 / 3.0, 2.5, "add-f64-fallback"},
                      Bench{0, 0x1p100, 0x1p-100, "add-gap-fallback"},
                      Bench{3, 1.25, 2.5, "divide-unchanged"}}) {
        for (int round = 0; round < 6; ++round) {
            for (int j = 0; j < 2; ++j) {
                int variant = (j + round) % 2;
                auto fn = variant ? candidate : baseline;
                double d = 0;
                auto start = std::chrono::steady_clock::now();
                for (int i = 0; i < 10000000; ++i)
                    fn(test.op, d, test.a, test.b, 0);
                auto ns = std::chrono::duration<double, std::nano>(
                    std::chrono::steady_clock::now() - start).count() / 10000000;
                std::printf("bench case=%s round=%d variant=%s ns=%.3f result=%.2f\n",
                            test.label, round, variant ? "candidate" : "baseline", ns, d);
            }
        }
    }
}
