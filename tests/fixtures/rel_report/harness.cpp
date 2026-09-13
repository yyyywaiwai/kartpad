#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
#define MKW_RESTRICT
#define RT_LOG(tag) std::cerr
struct CpuContext { uint32_t gpr[32]{}; uint32_t lr = 0; };
std::vector<uint32_t> observed;
struct Memory {
    static inline std::map<uint32_t, uint32_t> words;
    static inline bool failRead = false;
    static bool Contains(uint32_t address, size_t length) {
        const uint64_t end = uint64_t(address) + length;
        return (address >= 0x80000000 && end <= 0x80001000) ||
               (address >= 0xFFFFFFE0 && end <= (uint64_t{1} << 32));
    }
    static bool TryRead32(uint32_t address, uint32_t& value) noexcept {
        if (failRead || !Contains(address, 4)) return false;
        value = words[address];
        return true;
    }
};
namespace MemoryInline {
uint32_t FlatRead32(uint32_t address) {
    if (!Memory::Contains(address, 4)) throw std::runtime_error("unchecked REL read");
    return Memory::words[address];
}
}
namespace RecompMod {
@HELPER@
}
@FUNCTION@
void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
int main(int argc, char** argv) {
    try {
        require(argc == 2, "case argument required");
        const std::string mode = argv[1];
        uint32_t header = 0x80000080, table = 0x80000100, count = 2;
        bool valid = false;
        if (mode == "valid") valid = true;
        else if (mode == "empty") { count = 0; table = 0xBAD00001; valid = true; }
        else if (mode == "header-null") header = 0;
        else if (mode == "header-unmapped") header = 0xBAD00000;
        else if (mode == "header-unaligned") header += 1;
        else if (mode == "header-end") header = 0x80000FE4;
        else if (mode == "header-wrap") header = 0xFFFFFFE4;
        else if (mode == "read-failure") Memory::failRead = true;
        else if (mode == "table-null") table = 0;
        else if (mode == "table-unaligned") table += 1;
        else if (mode == "table-end") table = 0x80000FFC;
        else if (mode == "table-wrap") { table = 0xFFFFFFF8; count = 2; }
        else if (mode == "count-overflow") count = 0x20000000;
        else if (mode == "last-entry") { table = 0x80000FF8; count = 1; valid = true; }
        else throw std::runtime_error("unknown case");
        Memory::words[header + 12] = count;
        Memory::words[header + 16] = table;
        for (uint32_t i = 0; i < 4; ++i) Memory::words[table + 4 * i] = 10 + i;
        uint32_t output = 0xDEADBEEF;
        require(RecompMod::TryGetRelReportSectionTable(header, output) == valid, "helper validity");
        require(output == (valid ? table : 0), "helper output");
        CpuContext ctx;
        ctx.gpr[1] = 0x80000800;
        ctx.gpr[3] = header;
        for (int i = 28; i <= 31; ++i) ctx.gpr[i] = 90 + i;
        ctx.lr = 0x81234560;
        const auto saved = ctx;
        func_8000A440(&ctx);
        require(ctx.gpr[1] == saved.gpr[1] && ctx.lr == saved.lr, "stack/link restoration");
        for (int i = 28; i <= 31; ++i) require(ctx.gpr[i] == saved.gpr[i], "callee-saved restoration");
        const size_t expected = valid ? 2 * count : 0;
        require(observed.size() == expected, "section iteration count");
        for (size_t i = 0; i < expected; ++i) require(observed[i] == 10 + i, "section data");
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
