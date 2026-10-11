#!/usr/bin/env python3
"""Exercise the maintained Android scheduler event-service functions on the host.

Uses stub Aurora/Fiber interfaces, not SDL, Vulkan, or an Android device.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'vendor/runtimes/android/runtime/include/aurora_events.h').read_text()
# Compile the actual final section, including its Android conditional branches.
start = source.index('#if defined(__ANDROID__)\ninline std::atomic_bool g_androidAuroraPollPending')
code = r'''
#include <atomic>
#include <cassert>
#include <initializer_list>
#define __ANDROID__ 1
#undef __APPLE__
bool scheduler = false;
bool requestDuringUpdate = false;
int polls = 0, dispatches = 0;
struct AuroraEvent {};
namespace Fiber { struct GuestFiberManager {
 static bool IsOnSchedulerFiber() { return scheduler; }
}; }
void UpdateAuroraAndProcessEvents();
const AuroraEvent* aurora_update() {
 assert(scheduler); ++polls;
 if (requestDuringUpdate) {
   requestDuringUpdate = false;
   scheduler = false;
   UpdateAuroraAndProcessEvents();
   scheduler = true;
 }
 return nullptr; // No user input or window events are available.
}
void ProcessAuroraEvents(const AuroraEvent* events) {
 assert(events == nullptr); ++dispatches;
}
'''
code += source[start:]
code += r'''
int main() {
 // Guest requests cannot enter the native poller from a guest fiber.
 UpdateAuroraAndProcessEvents();
 UpdateAuroraAndProcessEvents();
 ServicePendingAuroraEventsOnScheduler();
 assert(polls == 0 && g_androidAuroraPollPending.load());
 // Requests coalesce, then service even when there is no input.
 scheduler = true;
 ServicePendingAuroraEventsOnScheduler();
 assert(polls == 1 && dispatches == 1 && !g_androidAuroraPollPending.load());
 ServicePendingAuroraEventsOnScheduler();
 assert(polls == 1);
 // Direct scheduler polling consumes an existing guest request once.
 scheduler = false; UpdateAuroraAndProcessEvents(); scheduler = true;
 UpdateAuroraAndProcessEvents();
 ServicePendingAuroraEventsOnScheduler();
 assert(polls == 2 && !g_androidAuroraPollPending.load());
 // A new request made during either native service path survives that service.
 for (bool direct : {false, true}) {
   scheduler = false; UpdateAuroraAndProcessEvents(); scheduler = true;
   requestDuringUpdate = true;
   const int before = polls;
   if (direct) UpdateAuroraAndProcessEvents();
   else ServicePendingAuroraEventsOnScheduler();
   assert(polls == before + 1 && g_androidAuroraPollPending.load());
   ServicePendingAuroraEventsOnScheduler();
   assert(polls == before + 2 && !g_androidAuroraPollPending.load());
 }
 assert(polls == dispatches);
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-event-service-') as tmp:
    path = Path(tmp)
    (path / 'test.cpp').write_text(code)
    subprocess.run(['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(path / 'test.cpp'),
                    '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('PASS: actual Android event-service functions; guest deferral, idle polling, '
      'coalescing, and requests during service (ASan/UBSan).')
