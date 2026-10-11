#!/usr/bin/env python3
"""Exercise production snapshot capture/restore with isolated GX state types.

Checks every CP register and combinations of VAT rows, including untouched-state
preservation. This is a state-copy contract test, not renderer/device acceptance.
"""
from pathlib import Path
import subprocess
import tempfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--platform', choices=['android', 'ios', 'macos', 'tvos'], default='android')
platform = parser.parse_args().platform
root = Path(__file__).resolve().parent.parent
source = (root / f'vendor/runtimes/{platform}/runtime/src/hle/gx/gx_dl.cpp').read_text()
functions = source[source.index('struct HleGxVertexStateSnapshot {'):source.index('struct ScanAttrStep {')]
functions += source[source.index('struct DlCpWrite {'):source.index('struct DlScanCacheEntry {')]
prelude = r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <type_traits>
#include <vector>
using GXAttrType = uint32_t;
using GXVtxFmt = uint32_t;
struct VtxAttrFmt { uint32_t cnt = 1; uint32_t type = 4; uint8_t frac = 0; };
struct HleGxState {
  GXAttrType vtxDesc[26];
  VtxAttrFmt vtxAttrFmt[8][26];
  struct VtxArray { uint32_t base = 0; uint32_t stride = 0; };
  VtxArray vtxArray[26];
  GXVtxFmt currentVtxFmt;
  uint64_t vtxLayoutHash;
  bool vtxLayoutHashDirty;
  uint32_t vtxStateGeneration;
} g_hleGxState;
static HleGxState state(uint32_t seed) {
  HleGxState s{};
  for (unsigned a=0; a<26; ++a) {
    s.vtxDesc[a] = seed+a;
    s.vtxArray[a] = {seed*16+a, seed+a*2};
    for (unsigned f=0; f<8; ++f)
      s.vtxAttrFmt[f][a] = {seed+f, seed+a, static_cast<uint8_t>(seed+f+a)};
  }
  s.currentVtxFmt=seed%8; s.vtxLayoutHash=0x1234567800000000ULL+seed;
  s.vtxLayoutHashDirty=seed%2; s.vtxStateGeneration=seed;
  return s;
}
static void equal(const HleGxState& a, const HleGxState& b) {
  for(unsigned i=0;i<26;++i) {
    assert(a.vtxDesc[i]==b.vtxDesc[i]);
    assert(a.vtxArray[i].base==b.vtxArray[i].base);
    assert(a.vtxArray[i].stride==b.vtxArray[i].stride);
    for(unsigned f=0;f<8;++f) {
      assert(a.vtxAttrFmt[f][i].cnt==b.vtxAttrFmt[f][i].cnt);
      assert(a.vtxAttrFmt[f][i].type==b.vtxAttrFmt[f][i].type);
      assert(a.vtxAttrFmt[f][i].frac==b.vtxAttrFmt[f][i].frac);
    }
  }
  assert(a.currentVtxFmt==b.currentVtxFmt);
  assert(a.vtxLayoutHash==b.vtxLayoutHash);
  assert(a.vtxLayoutHashDirty==b.vtxLayoutHashDirty);
  assert(a.vtxStateGeneration==b.vtxStateGeneration);
}
'''
tests = r'''
int main() {
  for(unsigned seed=1;seed<=32;++seed) {
    const auto original=state(seed), changed=state(seed+43);
    HleGxVertexStateSnapshot snapshot;
    std::memset(&snapshot,0xA5,sizeof(snapshot));
    g_hleGxState=original; CaptureGxVertexState(snapshot);
    g_hleGxState=changed; RestoreGxVertexState(snapshot);
    auto expected=original; expected.vtxStateGeneration=changed.vtxStateGeneration+1;
    equal(g_hleGxState,expected);
    for(unsigned reg=0;reg<256;++reg) {
      std::memset(&snapshot,0xA5,sizeof(snapshot));
      g_hleGxState=original;
      CaptureGxVertexStateForCpWrites(snapshot,DescribeDlCpWrites({{static_cast<uint8_t>(reg),0}}));
      g_hleGxState=changed; RestoreGxVertexState(snapshot);
      expected=changed;
      if(reg==0x50 || reg==0x60)
        std::memcpy(expected.vtxDesc,original.vtxDesc,sizeof(expected.vtxDesc));
      if((reg>=0x70&&reg<=0x77)||(reg>=0x80&&reg<=0x87)||(reg>=0x90&&reg<=0x97))
        std::memcpy(expected.vtxAttrFmt[reg&7],original.vtxAttrFmt[reg&7],sizeof(expected.vtxAttrFmt[0]));
      if(reg>=0xA0&&reg<=0xBF)
        std::memcpy(expected.vtxArray,original.vtxArray,sizeof(expected.vtxArray));
      expected.vtxLayoutHash=original.vtxLayoutHash;
      expected.vtxLayoutHashDirty=original.vtxLayoutHashDirty;
      ++expected.vtxStateGeneration;
      equal(g_hleGxState,expected);
    }
    for(unsigned mask=0;mask<256;++mask) {
      std::vector<DlCpWrite> writes;
      for(unsigned f=0;f<8;++f) if(mask&(1<<f)) {
        writes.push_back({static_cast<uint8_t>(0x70+f),0});
        writes.push_back({static_cast<uint8_t>(0x90+f),123});
      }
      g_hleGxState=original; CaptureGxVertexStateForCpWrites(snapshot,DescribeDlCpWrites(writes));
      g_hleGxState=changed; RestoreGxVertexState(snapshot);
      expected=changed;
      for(unsigned f=0;f<8;++f) if(mask&(1<<f))
        std::memcpy(expected.vtxAttrFmt[f],original.vtxAttrFmt[f],sizeof(expected.vtxAttrFmt[f]));
      expected.vtxLayoutHash=original.vtxLayoutHash;
      expected.vtxLayoutHashDirty=original.vtxLayoutHashDirty;
      ++expected.vtxStateGeneration;
      equal(g_hleGxState,expected);
    }
  }
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-gx-snapshot-') as temporary:
    path = Path(temporary)
    (path / 'test.cpp').write_text(prelude + functions + tests)
    subprocess.run(['clang++', '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('Passed 16,416 full/partial snapshot restoration cases with ASan/UBSan')
