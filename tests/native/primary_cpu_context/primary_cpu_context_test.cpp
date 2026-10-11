// Runs on an arm64 Android device/emulator. Verifies that the primary-thread
// context slot always equals the thread_local value it mirrors.
#include "isa/ppc_isa_context.h"
#include <cstdio>
#include <thread>
#include <vector>

void ShowRuntimeFatalPopup(std::string_view, std::string_view) noexcept {}

static int failures = 0;
#define CHECK(c) do { if (!(c)) { std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #c); ++failures; } } while (0)

static void Nest(CpuContext* ctxs, int depth) {
    if (depth == 0) return;
    CpuContextScope scope(&ctxs[depth]);
    CHECK(TryGetCpuContext() == &ctxs[depth]);
    CHECK(TryGetCpuContext() == g_currentCpuContext);
    Nest(ctxs, depth - 1);
    CHECK(TryGetCpuContext() == &ctxs[depth]);
}

int main() {
    static CpuContext ctxs[8]{};
    CHECK(TryGetCpuContext() == nullptr);
    CHECK(!OnPrimaryCpuContextThread());
    {
        // A scope opened before registration is mirrored at the claim.
        CpuContextScope outer(&ctxs[0]);
        ClaimPrimaryCpuContextThread();
        CHECK(OnPrimaryCpuContextThread());
        CHECK(TryGetCpuContext() == &ctxs[0]);
        Nest(ctxs, 6);
        CHECK(TryGetCpuContext() == &ctxs[0]);
        // Another thread keeps its own context and cannot claim the slot.
        std::thread other([&] {
            CHECK(!OnPrimaryCpuContextThread());
            CHECK(TryGetCpuContext() == nullptr);
            ClaimPrimaryCpuContextThread();
            CHECK(!OnPrimaryCpuContextThread());
            Nest(ctxs, 5);
            CHECK(TryGetCpuContext() == nullptr);
        });
        other.join();
        CHECK(TryGetCpuContext() == &ctxs[0]);
    }
    CHECK(TryGetCpuContext() == nullptr);

    // A claimed thread that exits releases the slot for reuse.
    std::thread owner2([&] {});
    owner2.join();
    std::thread claimer([&] {
        CHECK(!OnPrimaryCpuContextThread());
    });
    claimer.join();

    // Ownership release: a worker that claims before the main owner exits
    // cannot take the slot; after the owner's thread exits the slot is free.
    uintptr_t ownerTp = g_primaryCpuContext.owner.load();
    CHECK(ownerTp == HostThreadPointer());

    std::thread t1([&] {
        // Not owner.
        CpuContextScope s(&ctxs[3]);
        CHECK(TryGetCpuContext() == &ctxs[3]);
    });
    t1.join();

    // Simulate owner exit on a dedicated thread.
    g_primaryCpuContext.owner.store(0);
    std::thread t2([&] {
        CpuContextScope s(&ctxs[4]);
        ClaimPrimaryCpuContextThread();
        CHECK(OnPrimaryCpuContextThread());
        CHECK(TryGetCpuContext() == &ctxs[4]);
    });
    t2.join();
    CHECK(g_primaryCpuContext.owner.load() == 0);
    CHECK(g_primaryCpuContext.context == nullptr);

    std::printf("%s (%d failures)\n", failures ? "FAILED" : "PASSED", failures);
    return failures ? 1 : 0;
}
