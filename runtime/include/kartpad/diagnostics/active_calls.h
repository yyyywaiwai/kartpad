#pragma once

#include <array>
#include <cstdint>
#include <mutex>

namespace kartpad::diagnostics {
// Numeric, fixed operation vocabulary: never store addresses, payloads or identities.
enum class NetworkOperation : unsigned { SocketScalar, SocketVector, SslVector };
struct ActiveCall {
  uint64_t token = 0;
  NetworkOperation operation{};
  unsigned command = 0;
  int64_t started_ns = 0;
  bool reported = false;
};

// Shared diagnostic primitive; callers supply a monotonic clock. No worker or I/O here.
class ActiveCalls {
 public:
  static constexpr size_t kCapacity = 8;
  static constexpr unsigned kReportBudget = 32;
  uint64_t begin(NetworkOperation operation, unsigned command, int64_t now_ns) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& call : calls_) {
      if (call.token == 0) {
        if (++sequence_ == 0) ++sequence_;
        call = {sequence_, operation, command, now_ns, false};
        return sequence_;
      }
    }
    ++untracked_;
    return 0;
  }
  void end(uint64_t token) {
    if (token == 0) return;
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& call : calls_) if (call.token == token) { call = {}; return; }
  }
  struct Sample {
    std::array<ActiveCall, kCapacity> overdue{};
    size_t count = 0;
    unsigned remaining = 0;
    uint64_t untracked = 0;
  };
  Sample sample(int64_t now_ns, int64_t threshold_ns = 1'000'000'000) {
    std::lock_guard<std::mutex> lock(mutex_);
    Sample result;
    for (auto& call : calls_) {
      if (remaining_ == 0) break;
      if (call.token && !call.reported && now_ns >= call.started_ns &&
          now_ns - call.started_ns >= threshold_ns) {
        call.reported = true;
        result.overdue[result.count++] = call;
        --remaining_;
      }
    }
    result.remaining = remaining_;
    result.untracked = untracked_;
    return result;
  }
 private:
  std::mutex mutex_;
  std::array<ActiveCall, kCapacity> calls_{};
  uint64_t sequence_ = 0;
  uint64_t untracked_ = 0;
  unsigned remaining_ = kReportBudget;
};
} // namespace kartpad::diagnostics
