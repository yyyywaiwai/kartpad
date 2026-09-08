#include "kartpad/android/phase_metrics.h"
#include <cassert>
#include <cstdio>
int main() {
  kartpad::android::PhaseMetrics metrics;
  assert(metrics.mean_wall_ms() == 0 && metrics.mean_cpu_ms() == 0);
  for (unsigned i = 0; i < 300; ++i) metrics.add(2000000, 1000000);
  assert(metrics.count == 300 && metrics.mean_wall_ms() == 2);
  assert(metrics.mean_cpu_ms() == 1 && metrics.max_wall_ns == 2000000);
  metrics.add(8000000, 0);
  assert(metrics.max_wall_ns == 8000000 && metrics.wall_ns == 608000000);
  metrics.add(1, 0, false);
  metrics.add(1, 1);
  assert(!metrics.cpu_available);
  metrics = {};
  assert(metrics.count == 0 && metrics.max_wall_ns == 0);
  assert(metrics.cpu_available);
  std::puts("PASS: phase aggregation, units, maxima and reset");
}
