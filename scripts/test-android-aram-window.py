#!/usr/bin/env python3
"""Compare production AX decoding with uncached reads across cache boundaries."""
from pathlib import Path
import subprocess
import tempfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--platform', choices=['android', 'ios', 'macos', 'tvos'], default='android')
platform = parser.parse_args().platform
root = Path(__file__).resolve().parent.parent
source = (root / f'vendor/runtimes/{platform}/runtime/src/hle/audio/ax_internal.h').read_text()
windows = source[source.index('constexpr uint32_t kAramWindowShift'):source.index('enum class MailState')]
types = source[source.index('struct VolumeData'):source.index('enum class PBLayout')]
accelerator = source[source.index('class Accelerator {'):source.rindex('\n}')]
assert 'return ReadAramByte(addr, m_aramWindow);' in accelerator
reference = accelerator.replace('class Accelerator {', 'class UncachedAccelerator {').replace(
    'return ReadAramByte(addr, m_aramWindow);', 'return ReadAramByteSlow(addr);')
prelude = r'''
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <thread>
'''
backend = r'''
std::atomic<uint32_t> g_aramWindowGeneration{1};
std::array<std::array<uint8_t, 65536>, 2> ram{};
unsigned bank = 0, resolutions = 0;
uint8_t ReadAramByteSlow(uint32_t addr) { return ram[bank][addr & 65535]; }
bool ResolveAramWindow(uint32_t addr, AramWindow& window) {
  ++resolutions;
  // Exercise unmapped/partial-page fallback as well as normal contiguous pages.
  if ((addr & 0xf000) == 0xf000) { window = {}; return false; }
  window.begin = addr & ~(kAramWindowSize - 1);
  window.end = window.begin + kAramWindowSize;
  window.generation = g_aramWindowGeneration.load(std::memory_order_relaxed);
  window.host = ram[bank].data() + (window.begin & 65535);
  return true;
}
'''
tests = r'''
int main() {
  static_assert(kAxWiimoteBusCount == 8 && kAxWiimoteSamplesPerFrame == 18);
  for (unsigned b=0; b<2; ++b)
    for (unsigned i=0; i<65536; ++i) ram[b][i] = (i*37 + (i>>8)*13 + b*71) & 255;
  // Each thread keeps its own existing window; accelerators on that thread reuse it.
  auto* mainWindow = &CurrentAramWindow();
  std::thread other([&] { assert(&CurrentAramWindow() != mainWindow); }); other.join();
  unsigned comparisons = 0;
  for (unsigned format=0; format<64; ++format)
    for (unsigned looping=0; looping<2; ++looping)
      for (unsigned stream=0; stream<2; ++stream)
        for (uint32_t address : {0xff0u, 0x1ff0u, 0xeff0u, 0x1fffff0u, 0x10000ff0u, 0x3ffffff0u}) {
          AXPBWii pb{};
          pb.running = 1; pb.is_stream = stream;
          pb.audio_addr.sample_format = format; pb.audio_addr.looping = looping;
          pb.audio_addr.cur_addr_hi = address >> 16; pb.audio_addr.cur_addr_lo = address;
          const auto end = (address + 160) & 0x3fffffffu;
          const auto loop = address & 0x3fffffffu;
          pb.audio_addr.end_addr_hi = end >> 16; pb.audio_addr.end_addr_lo = end;
          pb.audio_addr.loop_addr_hi = loop >> 16; pb.audio_addr.loop_addr_lo = loop;
          pb.adpcm.gain = 64; pb.adpcm.pred_scale = 0x12;
          pb.adpcm.yn1 = 120; pb.adpcm.yn2 = -90;
          for (unsigned i=0; i<16; ++i) pb.adpcm.coefs[i] = i%2 ? -16 : 32;
          pb.adpcm_loop_info.pred_scale = 0x23;
          pb.adpcm_loop_info.yn1 = 42; pb.adpcm_loop_info.yn2 = -31;
          auto expected = pb;
          Accelerator actual; UncachedAccelerator oracle;
          actual.Setup(&pb); oracle.Setup(&expected);
          for (unsigned i=0; i<512; ++i) {
            // Mapping invalidation while the accelerator still exists must be honored.
            if (i==113 || i==277) { bank ^= 1; ++g_aramWindowGeneration; }
            assert(actual.ReadSample() == oracle.ReadSample());
            assert(std::memcmp(&pb, &expected, sizeof(pb)) == 0);
            ++comparisons;
          }
        }
  // The cache remains shared by sequential voices, rather than reset per voice.
  CurrentAramWindow() = {};
  Accelerator first, second;
  resolutions = 0;
  assert(first.ReadAram8(0x1234) == ReadAramByteSlow(0x1234));
  assert(second.ReadAram8(0x1235) == ReadAramByteSlow(0x1235));
  assert(resolutions == 1);
  assert(comparisons == 786432);
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-aram-window-') as temporary:
    path = Path(temporary)
    (path / 'test.cpp').write_text(prelude + windows + types + backend + accelerator + reference + tests)
    subprocess.run(['clang++', '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-pthread', str(path/'test.cpp'), '-o', str(path/'test')], check=True)
    subprocess.run([str(path/'test')], check=True)
print('Passed 786,432 AX sample/state comparisons, remapping, fallback, and thread-window checks with ASan/UBSan')
