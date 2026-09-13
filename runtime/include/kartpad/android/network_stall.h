#pragma once
#if defined(__ANDROID__)
#include <atomic>
#include <chrono>
#include <cstring>
#include "kartpad/diagnostics/active_calls.h"

extern "C" void KartPadAndroidLogMetric(const char*, const char*, ...);
extern "C" long long KartPadAndroidThreadCpuNanos();

namespace kartpad::android {
inline diagnostics::ActiveCalls activeNetworkCalls;
inline int64_t NetworkClockNanos() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline diagnostics::NetworkOperation NetworkOperation(const char* operation) {
  if (std::strcmp(operation, "socket_ioctl") == 0) return diagnostics::NetworkOperation::SocketScalar;
  if (std::strcmp(operation, "socket_ioctlv") == 0) return diagnostics::NetworkOperation::SocketVector;
  return diagnostics::NetworkOperation::SslVector;
}
inline void SampleNetworkWaits() {
  const auto now = NetworkClockNanos();
  const auto sample = activeNetworkCalls.sample(now);
  for (size_t i = 0; i < sample.count; ++i) {
    const auto& call = sample.overdue[i];
    KartPadAndroidLogMetric("KartPadNetWait",
        "state=in_progress operation=%u command=%u age_ms=%.3f remaining=%u untracked=%llu call=%llu",
        static_cast<unsigned>(call.operation), call.command,
        double(now - call.started_ns) / 1e6, sample.remaining,
        static_cast<unsigned long long>(sample.untracked),
        static_cast<unsigned long long>(call.token));
  }
}
// Completed host calls only: guest scheduler waits are intentionally excluded.
// A process-wide cap prevents repeated stalls from flooding the private log.
class NetworkCallTimer {
 public:
  NetworkCallTimer(const char* operation, unsigned command)
      : operation_(operation), command_(command), start_(Clock::now()),
        cpu_start_(KartPadAndroidThreadCpuNanos()),
        token_(activeNetworkCalls.begin(NetworkOperation(operation), command, NetworkClockNanos())) {}
  ~NetworkCallTimer() {
    activeNetworkCalls.end(token_);
    const double wall_ms = std::chrono::duration<double, std::milli>(Clock::now() - start_).count();
    if (wall_ms < 100.0) return;
    unsigned remaining = budget_.load(std::memory_order_relaxed);
    do {
      if (remaining == 0) return;
    } while (!budget_.compare_exchange_weak(remaining, remaining - 1,
                                          std::memory_order_relaxed));
    const long long cpu_end = KartPadAndroidThreadCpuNanos();
    const double cpu_ms = cpu_start_ >= 0 && cpu_end >= cpu_start_
        ? double(cpu_end - cpu_start_) / 1e6 : -1.0;
    KartPadAndroidLogMetric("KartPadNetStall",
        "operation=%s command=%u wall_ms=%.3f cpu_ms=%.3f remaining=%u call=%llu",
        operation_, command_, wall_ms, cpu_ms, remaining - 1,
        static_cast<unsigned long long>(token_));
  }
  NetworkCallTimer(const NetworkCallTimer&) = delete;
  NetworkCallTimer& operator=(const NetworkCallTimer&) = delete;
 private:
  using Clock = std::chrono::steady_clock;
  inline static std::atomic<unsigned> budget_{32};
  const char* operation_;
  unsigned command_;
  Clock::time_point start_;
  long long cpu_start_;
  uint64_t token_;
};
}
#endif
