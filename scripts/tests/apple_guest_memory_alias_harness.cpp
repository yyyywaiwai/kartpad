// Includes the actual implementation extracted from the Apple runtime patch.
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <cassert>
#include <cstdlib>
#include <iostream>
static int remaps = 0;
static int failRemap = 0;
static mach_vm_address_t failedReservation = 0;
static kern_return_t TestRemap(vm_map_t targetTask, vm_address_t* address,
    vm_size_t size, vm_address_t mask, int flags, vm_map_t sourceTask,
    vm_address_t source, boolean_t copy, vm_prot_t* current,
    vm_prot_t* maximum, vm_inherit_t inheritance) {
    assert(copy == FALSE);
    if (++remaps == failRemap) {
        failedReservation = *address;
        return KERN_NO_SPACE;
    }
    return vm_remap(targetTask, address, size, mask, flags, sourceTask,
                         source, copy, current, maximum, inheritance);
}
#define vm_remap TestRemap
#include "guest_flat_memory_apple.cpp"
#undef vm_remap
static bool Readable(const void* pointer) {
    uint8_t byte;
    mach_vm_size_t copied = 0;
    return mach_vm_read_overwrite(mach_task_self(), reinterpret_cast<mach_vm_address_t>(pointer),
        1, reinterpret_cast<mach_vm_address_t>(&byte), &copied) == KERN_SUCCESS && copied == 1;
}
static bool FileBacked(const void* pointer) {
    mach_vm_address_t address = reinterpret_cast<mach_vm_address_t>(pointer);
    mach_vm_size_t size = 0;
    vm_region_extended_info_data_t info{};
    mach_msg_type_number_t count = VM_REGION_EXTENDED_INFO_COUNT;
    mach_port_t object = MACH_PORT_NULL;
    assert(mach_vm_region(mach_task_self(), &address, &size, VM_REGION_EXTENDED_INFO,
                          reinterpret_cast<vm_region_info_t>(&info), &count, &object) == KERN_SUCCESS);
    if (object != MACH_PORT_NULL) mach_port_deallocate(mach_task_self(), object);
    return info.external_pager;
}
static void Reset() {
    using namespace GuestFlat;
    assert(munmap(g_base, kGuestSpaceSize + getpagesize()) == 0);
    for (auto& section : g_sections)
        assert(munmap(section.host, section.size) == 0);
    g_base = gFlatGuestBase = nullptr;
    g_initialized = false;
    g_layout.clear(); g_mappings.clear(); g_sections.clear();
}
int main() {
    using namespace GuestFlat;
    unsetenv("TMPDIR"); // Anonymous backing must not depend on a writable temp path.
    const uint64_t page = getpagesize();
    for (const auto& invalid : std::vector<std::vector<RegionRequest>>{
             {{1, page, Backing::Owned}}, {{0, 0, Backing::Owned}},
             {{0xffffc000, 0x10000, Backing::Mem1}},
             {{0, page * 2, Backing::Owned}, {static_cast<uint32_t>(page), page, Backing::Owned}}}) {
        bool rejected = false;
        try { Initialize(invalid); } catch (const std::runtime_error&) { rejected = true; }
        assert(rejected && !IsActive() && g_base == nullptr);
    }
    const std::vector<RegionRequest> layout = {
        {0, page * 2, Backing::Mem1}, {0x80000000, page * 2, Backing::Mem1},
        {0xc0000000, page * 2, Backing::Mem1},
        {0x10000000, page * 2, Backing::Mem2}, {0x90000000, page * 2, Backing::Mem2},
        {0x20000000, page, Backing::Owned}, {0x30000000, page, Backing::Owned},
        {static_cast<uint32_t>(0x80000000 + page * 2), page, Backing::Mem1}};
    failRemap = 2;
    bool failed = false;
    try { Initialize(layout); } catch (const std::runtime_error&) { failed = true; }
    assert(failed && !IsActive() && !g_base && !gFlatGuestBase);
    assert(g_sections.empty() && g_mappings.empty());
    assert(!Readable(reinterpret_cast<void*>(failedReservation)));
    failRemap = 0;
    // Positive control: the old unlinked-file mapping really is file-backed.
    char path[] = "/tmp/kartpad-old-ram-test-XXXXXX";
    int fd = mkstemp(path);
    assert(fd >= 0 && unlink(path) == 0 && ftruncate(fd, page) == 0);
    auto* old = static_cast<uint8_t*>(mmap(nullptr, page, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
    assert(old != MAP_FAILED);
    old[0] = 1;
    assert(FileBacked(old));
    assert(munmap(old, page) == 0 && close(fd) == 0);
    for (int iteration = 0; iteration < 3; ++iteration) {
        Initialize(layout);
        assert(IsActive());
        auto* flat = gFlatGuestBase;
        assert(!FileBacked(HostPointer(0)) && !FileBacked(flat + 0x80000000));
        for (uint64_t i : {uint64_t(0), page - 1, page, page * 2 - 1}) {
            assert(HostPointer(i)[0] == 0);
            HostPointer(i)[0] = 17;
            assert(flat[0x80000000ULL + i] == 17 && flat[0xc0000000ULL + i] == 17);
            flat[0xc0000000ULL + i] = 42;
            assert(flat[i] == 42 && HostPointer(0x80000000 + i)[0] == 42);
        }
        HostPointer(0x10000000)[0] = 53;
        assert(flat[0x90000000] == 53 && flat[0] == 42);
        HostPointer(0x20000000)[0] = 69;
        assert(flat[0x30000000] == 0);
        HostPointer(0x80000000 + page * 2)[0] = 81;
        assert(g_sections[0].host[page * 2] == 81); // Nonzero section offset.
        assert(HostPointer(0x40000000) == nullptr && !Readable(flat + 0x40000000));
        ProtectDeferredRange(0x80000000, page);
        assert(!Readable(flat + 0x80000000));
        HostPointer(0)[0] = 99;
        assert(flat[0] == 99 && flat[0xc0000000] == 99);
        UnprotectDeferredRange(0x80000000, page);
        assert(flat[0x80000000] == 99);
        auto* original = flat;
        Initialize(layout);
        assert(gFlatGuestBase == original && flat[0] == 0 && flat[0x90000000] == 0);
        bool rejected = false;
        try { Initialize({{0, page, Backing::Mem1}}); }
        catch (const std::runtime_error&) { rejected = true; }
        assert(rejected && IsActive() && gFlatGuestBase == original);
        Reset();
        assert(!Readable(original));
    }
    // Real runtime WiiDefaults sizes: MEM1, NDEV MEM2, overlay, locked cache.
    Initialize({{0, 0x1800000, Backing::Mem1}, {0x80000000, 0x1800000, Backing::Mem1},
                {0xc0000000, 0x1800000, Backing::Mem1}, {0x10000000, 0x8000000, Backing::Mem2},
                {0x90000000, 0x8000000, Backing::Mem2}, {0xd0000000, 0x8000000, Backing::Mem2},
                {0x81800000, 0x200000, Backing::Owned}, {0xe0000000, 0x101000, Backing::Owned}});
    for (auto& section : g_sections) {
        std::memset(section.host, 0xa5, section.size);
        assert(!FileBacked(section.host));
    }
    assert(gFlatGuestBase[0xc17fffff] == 0xa5 && gFlatGuestBase[0xd7ffffff] == 0xa5);
    Reset();
    std::cout << "Apple anonymous guest RAM: mirrors, offsets, isolation, protections, reset, invalid layouts and remap-failure cleanup passed\n";
}
