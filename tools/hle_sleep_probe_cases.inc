namespace {
constexpr uint32_t caller = 0x80010000, peer = 0x80011000, waitQueue = 0x80020000;
unsigned completed = 0;
void require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}
void thread(uint32_t address, unsigned priority, unsigned state) {
  Memory::Write32(address + kThreadPriorityOffset, priority);
  Memory::Write16(address + kThreadStateOffset, state);
}
void reset(bool withPeer = true) {
  Memory::bytes.clear(); persistent = {}; interruptState = 1;
  idlePolls = completed = 0; idleHook = {};
  Fiber::GuestFiberManager::current = caller;
  Fiber::GuestFiberManager::switches = 0;
  Fiber::GuestFiberManager::suspended.clear();
  Fiber::GuestFiberManager::switchHook = {};
  thread(caller, 5, kThreadStateRunning);
  thread(peer, 10, kThreadStateReady);
  Memory::Write32(kOSRunningContextAddr, caller);
  Memory::Write32(kOSCurrentContextAddr, caller);
  if (withPeer) {
    InsertThreadIntoQueueByPriority(kThreadQueueArrayAddr + 10 * 8, peer, 10);
  }
}
void sleep() {
  persistent.gpr[3] = waitQueue;
  OSSleepThread_HLE_801aa9b8(&persistent);
}
void intact() {
  require(Memory::Read16(caller + kThreadStateOffset) == kThreadStateRunning,
          "caller must be running on return");
  require(Memory::Read32(caller + kThreadQueueOffset) == 0, "caller queue link leaked");
  require(Memory::Read32(caller + kThreadNextOffset) == 0, "caller next link leaked");
  require(Memory::Read32(caller + kThreadPrevOffset) == 0, "caller previous link leaked");
  require(Memory::Read32(caller + kThreadSuspendOffset) == 0, "suspension count changed");
  require(Memory::Read32(waitQueue) == 0 && Memory::Read32(waitQueue + 4) == 0,
          "wait queue not drained");
  require(!Fiber::GuestFiberManager::suspended.contains(caller), "fiber stayed suspended");
  require(interruptState == 1, "interrupt state not restored");
}
void installPeerCompletion() {
  Fiber::GuestFiberManager::switchHook = [](uint32_t next, CpuContext* cpu) {
    if (next == peer) {
      require(Memory::Read16(caller + kThreadStateOffset) == kThreadStateWaiting,
              "peer did not observe caller waiting");
      require(Memory::Read32(waitQueue) == caller, "missing queued waiter");
      ++completed;
      OS_HLE_WakeupThreadNoReschedule(cpu, waitQueue);
      cpu->gpr[3] = 0;
      SelectThread_801a9c08(cpu);
      require(Fiber::GuestFiberManager::current == caller, "caller was not selected back");
    } else {
      require(next == caller, "unexpected selected thread");
    }
  };
}
void run() {
  reset(); installPeerCompletion(); sleep(); intact();
  require(completed == 1 && Fiber::GuestFiberManager::switches == 2,
          "valid peer completion did not yield and resume");
  std::cout << "PASS enabled matching context: real queue/wakeup/select round trip\n";

  reset(); Memory::Write32(kOSCurrentContextAddr, 0x80012000);
  sleep(); intact();
  require(Fiber::GuestFiberManager::switches == 0, "mismatch switched contexts");
  require(Memory::Read32(kSchedulerPendingFlagAddr) == (1u << 21), "peer lost on rollback");
  std::cout << "PASS context mismatch: post-select rollback preserves waiter and runnable peer\n";

  reset(); Memory::Write32(kSchedulerIdleFlagAddr, 1);
  sleep(); intact();
  require(Fiber::GuestFiberManager::switches == 0, "disabled scheduler switched");
  std::cout << "PASS scheduler disabled: early refusal preserves queue and suspension\n";

  reset(false);
  idleHook = [](CpuContext* cpu) {
    if (idlePolls == 3) { ++completed; OS_HLE_WakeupThreadNoReschedule(cpu, waitQueue); }
  };
  Fiber::GuestFiberManager::switchHook = [](uint32_t next, CpuContext*) {
    require(next == caller, "idle completion chose wrong thread");
  };
  sleep(); intact();
  require(completed == 1 && idlePolls == 3, "idle path failed to process completion");
  std::cout << "PASS no runnable peer: actual idle poll accepts completion and resumes waiter\n";

  reset(false);
  bool boundedIdle = false;
  try { sleep(); } catch (const IdleLimit&) { boundedIdle = true; }
  require(boundedIdle && Memory::Read16(caller + kThreadStateOffset) == kThreadStateWaiting,
          "no completion should remain waiting in scheduler idle loop");
  require(Memory::Read32(waitQueue) == caller && Memory::Read32(waitQueue + 4) == caller,
          "idle waiter linkage invalid");
  std::cout << "PASS no peer or completion: bounded observation of intentional idle wait\n";

  reset(); Memory::Write32(kOSCurrentContextAddr, 0x80012000);
  installPeerCompletion();
  for (unsigned i = 0; i < 1000; ++i) { sleep(); intact(); }
  require(completed == 0 && idlePolls == 0 && Fiber::GuestFiberManager::switches == 0,
          "refused sleep unexpectedly executes completion");
  Memory::Write32(kOSCurrentContextAddr, caller);
  sleep(); intact();
  require(completed == 1, "valid context restoration did not unblock completion");
  std::cout << "PASS 1000 refused retries: no corruption; completion runs when context becomes switchable\n";
}
}
int main() {
  try { run(); } catch (const std::exception& error) {
    std::cerr << "FAIL " << error.what() << '\n'; return 1;
  }
}
