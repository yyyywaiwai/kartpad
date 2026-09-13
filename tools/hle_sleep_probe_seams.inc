namespace OsHleInternal {
bool ProcessSleepTimers(CpuContext*) { return false; }
bool ProcessAlarmQueue(CpuContext*, int) { return false; }
}
inline int32_t interruptState = 1;
extern "C" int32_t OS__DisableInterrupts_801a65ac() {
  const auto previous = interruptState; interruptState = 0; return previous;
}
extern "C" int32_t OS__EnableInterrupts_801a65c0() {
  const auto previous = interruptState; interruptState = 1; return previous;
}
extern "C" int32_t OS__RestoreInterrupts_801a65d4(int32_t value) {
  const auto previous = interruptState; interruptState = value; return previous;
}
extern "C" void OS__ClearContext_801a2098(uint32_t) {}
extern "C" void OS__SetCurrentContext_801a1e70(uint32_t context) {
  Memory::Write32(kOSCurrentContextAddr, context);
}
extern "C" [[noreturn]] void OS__LoadContext_801a1f58(CpuContext*) {
  throw std::runtime_error("unexpected translated context load");
}
extern "C" void func_801A1ED8(CpuContext* cpu) { cpu->gpr[3] = 0; }
