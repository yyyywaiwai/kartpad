#pragma once
#include <algorithm>
#include <cstdint>

namespace kartpad::android {
// Fixed-size aggregation. No per-frame allocation or log output.
struct PhaseMetrics {
  std::uint64_t count{}, wall_ns{}, cpu_ns{}, max_wall_ns{};
  bool cpu_available = true;
  void add(std::uint64_t wall, std::uint64_t cpu, bool cpu_known = true) noexcept {
    ++count;
    wall_ns += wall;
    cpu_ns += cpu;
    cpu_available = cpu_available && cpu_known;
    max_wall_ns = std::max(max_wall_ns, wall);
  }
  double mean_wall_ms() const noexcept { return count ? double(wall_ns) / count / 1e6 : 0; }
  double mean_cpu_ms() const noexcept { return count ? double(cpu_ns) / count / 1e6 : 0; }
};
}
