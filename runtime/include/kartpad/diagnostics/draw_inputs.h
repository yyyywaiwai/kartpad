#pragma once
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace kartpad::diagnostics {
struct MatrixSelection {
  bool complete = false;
  uint32_t sampled = 0;
  uint32_t outside_palette = 0;
  uint32_t non_row_multiple = 0;
  uint32_t max_raw = 0;
  uint16_t used_mask = 0;
};
// PNMTXIDX is the first byte when directly present. No input bytes leave this function.
inline MatrixSelection inspect_matrix_selection(const uint8_t* bytes, size_t size,
                                                uint32_t count, uint32_t stride) {
  MatrixSelection result;
  if (!bytes || stride == 0 || count > size / stride) return result;
  result.complete = true;
  for (uint32_t i = 0; i < count; ++i) {
    const unsigned raw = bytes[size_t(i) * stride];
    const unsigned slot = raw / 3;
    ++result.sampled;
    if (raw > result.max_raw) result.max_raw = raw;
    if (raw % 3) ++result.non_row_multiple;
    if (slot >= 10) ++result.outside_palette;
    else result.used_mask |= uint16_t(1u << slot);
  }
  return result;
}
inline unsigned count_nonfinite(const void* bytes, size_t size) {
  unsigned count = 0;
  auto* data = static_cast<const uint8_t*>(bytes);
  for (size_t offset = 0; offset + sizeof(float) <= size; offset += sizeof(float)) {
    float value;
    std::memcpy(&value, data + offset, sizeof(value));
    if (!std::isfinite(value)) ++count;
  }
  return count;
}
// Caller serializes on the renderer's existing mutex. Separate budgets keep normal
// startup samples from consuming the anomaly allowance. No dynamic allocation.
class DrawReportBudget {
 public:
  bool take(uint64_t pipeline, bool anomaly) {
    if (anomaly) {
      if (anomalies_ == 64) return false;
      ++anomalies_;
      return true;
    }
    for (unsigned i = 0; i < pipelines_; ++i) if (seen_[i] == pipeline) return false;
    if (pipelines_ == seen_.size()) return false;
    seen_[pipelines_++] = pipeline;
    return true;
  }
 private:
  std::array<uint64_t, 32> seen_{};
  unsigned pipelines_ = 0;
  unsigned anomalies_ = 0;
};
}
