// Synthetic host seams only. Actual HLE bodies are appended by the runner.
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>

struct CpuContext { uint32_t gpr[32]{}; };
namespace Memory {
inline std::unordered_map<uint32_t, uint8_t> bytes;
class AccessViolation : public std::runtime_error {
 public:
  AccessViolation() : std::runtime_error("synthetic memory violation") {}
  uint32_t address() const { return 0; }
};
inline bool Contains(uint32_t address, size_t size) {
  return address >= 0x80000000u && uint64_t(address) + size <= 0x80400000u;
}
inline uint32_t Read32(uint32_t address) {
  if (!Contains(address, 4)) throw AccessViolation();
  uint32_t value = 0;
  for (unsigned i = 0; i < 4; ++i) value = (value << 8) | bytes[address + i];
  return value;
}
inline uint16_t Read16(uint32_t address) {
  if (!Contains(address, 2)) throw AccessViolation();
  return (uint16_t(bytes[address]) << 8) | bytes[address + 1];
}
inline void Write32(uint32_t address, uint32_t value) {
  if (!Contains(address, 4)) throw AccessViolation();
  for (unsigned i = 0; i < 4; ++i) bytes[address + i] = value >> (24 - i * 8);
}
inline void Write16(uint32_t address, uint16_t value) {
  if (!Contains(address, 2)) throw AccessViolation();
  bytes[address] = value >> 8; bytes[address + 1] = value;
}
}
inline CpuContext persistent;
inline CpuContext& GetPersistentCpuContext() { return persistent; }
#define RT_TAG_OS 0
#define RT_LOG(tag) std::cerr
inline void LogMemoryError(int, const char*, const Memory::AccessViolation&) {
  throw std::runtime_error("unexpected memory violation");
}
inline uint32_t PPC_Cntlzw(uint32_t value) { return std::countl_zero(value); }
namespace TranslatedFunctionRegistry {
inline bool FindByAddressPtr(uint32_t) { return false; }
}
inline void InvokeIndirectCpu(uint32_t, CpuContext*) {
  throw std::runtime_error("unexpected translated callback");
}
namespace Fiber {
struct GuestFiberManager {
  static inline uint32_t current = 0;
  static inline unsigned switches = 0;
  static inline std::unordered_set<uint32_t> suspended;
  static inline std::function<void(uint32_t, CpuContext*)> switchHook;
  static bool IsInitialized() { return true; }
  static bool IsTerminated(uint32_t) { return false; }
  static bool HasFiber(uint32_t) { return true; }
  static uint32_t GetCurrentGuestThread() { return current; }
  static void RegisterMainThreadAsFiber(uint32_t thread, CpuContext*) { current = thread; }
  static void SuspendGuestThread(uint32_t thread) { suspended.insert(thread); }
  static void ResumeGuestThread(uint32_t thread) { suspended.erase(thread); }
  static void SwitchToThread(uint32_t thread, CpuContext* cpu) {
    ++switches; current = thread;
    if (!switchHook) throw std::runtime_error("unexpected fiber switch");
    switchHook(thread, cpu);
  }
  static void ProcessTimerEvents(CpuContext*) {}
};
}
inline unsigned idlePolls = 0;
inline std::function<void(CpuContext*)> idleHook;
struct IdleLimit : std::runtime_error { IdleLimit() : std::runtime_error("bounded idle") {} };
inline void Audio_HLE_Poll(CpuContext* cpu) {
  if (++idlePolls > 100) throw IdleLimit();
  if (idleHook) idleHook(cpu);
}
inline void VI_HLE_PollRetrace(CpuContext*) {}
inline void VI_HLE_WaitForNextRetracePoll() {}
inline bool VI_HLE_IsAdvancingRetrace() { return false; }
