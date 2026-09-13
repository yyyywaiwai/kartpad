#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "kartpad/android/gamepad_contract.h"

namespace kartpad::android {

using ControllerButtonMapping = std::array<uint8_t, 7>;

inline constexpr ControllerButtonMapping kDefaultControllerButtonMapping{
    0, 1, 2, 3, 4, 5, 6,
};

inline constexpr std::array<uint32_t, 7> kMappablePhysicalButtons{
    kGamepadSouth, kGamepadEast, kGamepadWest, kGamepadNorth,
    kGamepadLeftShoulder, kGamepadRightShoulder, kGamepadDpadUp,
};

inline bool IsValidControllerButtonMapping(
    const ControllerButtonMapping& mapping) noexcept {
  uint32_t seen = 0;
  for (const uint8_t physical : mapping) {
    if (physical >= kMappablePhysicalButtons.size()) return false;
    const uint32_t bit = 1u << physical;
    if ((seen & bit) != 0) return false;
    seen |= bit;
  }
  return seen == ((1u << mapping.size()) - 1u);
}

inline uint32_t ApplyControllerButtonMapping(
    const uint32_t buttons, ControllerButtonMapping mapping) noexcept {
  if (!IsValidControllerButtonMapping(mapping)) {
    mapping = kDefaultControllerButtonMapping;
  }
  constexpr uint32_t mappedMask = kGamepadSouth | kGamepadEast |
      kGamepadWest | kGamepadNorth | kGamepadLeftShoulder |
      kGamepadRightShoulder | kGamepadDpadUp;
  uint32_t result = buttons & ~mappedMask;
  for (std::size_t game = 0; game < mapping.size(); ++game) {
    if ((buttons & kMappablePhysicalButtons[mapping[game]]) != 0) {
      result |= kMappablePhysicalButtons[game];
    }
  }
  return result;
}

void PublishControllerButtonMapping(
    const ControllerButtonMapping& mapping) noexcept;
ControllerButtonMapping ReadControllerButtonMapping() noexcept;

}  // namespace kartpad::android
