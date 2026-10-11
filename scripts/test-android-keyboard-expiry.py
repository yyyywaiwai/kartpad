#!/usr/bin/env python3
"""Check production keyboard expiry behavior and inactive-key clock avoidance."""
from pathlib import Path
import subprocess
import tempfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--platform', choices=['android', 'ios', 'macos', 'tvos'], default='android')
platform = parser.parse_args().platform
root = Path(__file__).resolve().parent.parent
source = (root / f'vendor/runtimes/{platform}/runtime/src/hle/input/kpad.cpp').read_text()
functions = source[source.index('bool IsKeyDown('):source.index('uint32_t ReadKeyboardButtons(')]
prelude = r'''
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
using SDL_Scancode = unsigned;
constexpr unsigned SDL_SCANCODE_COUNT = 512;
std::array<std::atomic<uint64_t>, SDL_SCANCODE_COUNT> g_syntheticExpiryNs{};
uint64_t now = 0;
unsigned clockReads = 0;
bool fullStick = false;
uint64_t SDL_GetTicksNS() { ++clockReads; return now; }
bool FullSyntheticStickEnabled() { return fullStick; }
'''
tests = r'''
int main() {
  bool keys[SDL_SCANCODE_COUNT]{};
  // Compare results with the original contract at zero, before, exactly at,
  // and after expiry. Physical input always wins; synthetic axes retain scale.
  for (unsigned code=0; code<SDL_SCANCODE_COUNT; ++code) {
    for (uint64_t expiry : {uint64_t{0}, uint64_t{1}, uint64_t{100}, UINT64_MAX}) {
      g_syntheticExpiryNs[code] = expiry;
      for (uint64_t tick : {uint64_t{0}, uint64_t{1}, uint64_t{99}, uint64_t{100}, uint64_t{101}, UINT64_MAX}) {
        now = tick;
        for (bool physical : {false, true}) {
          keys[code] = physical;
          clockReads = 0;
          assert(IsKeyDown(keys, SDL_SCANCODE_COUNT, code) == (physical || expiry > now));
          assert(clockReads == (physical || expiry == 0 ? 0u : 1u));
          for (bool full : {false, true}) {
            fullStick = full;
            clockReads = 0;
            const float expected = physical ? 1.0f : expiry > now ? (full ? 1.0f : 0.35f) : 0.0f;
            assert(ReadKeyboardAxisLevel(keys, SDL_SCANCODE_COUNT, code) == expected);
            assert(clockReads == (physical || expiry == 0 ? 0u : 1u));
          }
        }
      }
      keys[code] = false;
    }
    g_syntheticExpiryNs[code] = 0;
  }
  clockReads = 0;
  for (unsigned code=0; code<SDL_SCANCODE_COUNT; ++code)
    assert(!IsKeyDown(keys, SDL_SCANCODE_COUNT, code));
  assert(clockReads == 0);
  assert(!IsKeyDown(keys, SDL_SCANCODE_COUNT, SDL_SCANCODE_COUNT));
  assert(ReadKeyboardAxisLevel(keys, SDL_SCANCODE_COUNT, SDL_SCANCODE_COUNT) == 0.0f);
  // A key event arriving after an inactive poll remains visible on the next.
  now = 100; g_syntheticExpiryNs[7] = 101;
  assert(IsKeyDown(keys, SDL_SCANCODE_COUNT, 7));
  now = 101; assert(!IsKeyDown(keys, SDL_SCANCODE_COUNT, 7));
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-keyboard-expiry-') as temporary:
    path = Path(temporary)
    (path / 'test.cpp').write_text(prelude + functions + tests)
    subprocess.run(['clang++', '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('Passed 73,728 key/axis expiry comparisons and inactive-poll clock checks with ASan/UBSan')
