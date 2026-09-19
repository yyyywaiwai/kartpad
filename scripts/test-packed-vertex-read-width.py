#!/usr/bin/env python3
"""Execute the prepared shader's integer loaders against checked storage words.

This maps only the WGSL integer subset used by these helpers to C++. It proves
read width/endian arithmetic, not GPU driver behavior or gameplay acceptance.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

source = (Path(sys.argv[1]) / 'aurora-main/lib/gx/shader.cpp').read_text()
names = ['load_u32_raw', 'load_u24_raw', 'load_u24', 'raw_fetch_u8_3']
functions = []
for name in names:
    start = source.index('fn ' + name + '(')
    end = source.index('\n}}', start) + 3
    code = source[start:end].replace('{{', '{').replace('}}', '}')
    code = re.sub(r'fn (\w+)\(p: ptr<storage, array<u32>>, byte_off: u32(, le: bool)?\) -> (u32|vec3u)',
                  lambda m: ('uint32_t' if m[3] == 'u32' else 'Vec3') + ' ' + m[1] +
                  '(const Words& p, uint32_t byte_off' + (', bool le' if m[2] else '') + ')', code)
    code = code.replace('let ', 'const auto ').replace('vec3u(', 'Vec3(')
    code = re.sub(r',\s*\);', ');', code)
    functions.append(code)
cpp = r'''
#include <array>
#include <cstdint>
#include <stdexcept>
#include <vector>
#include <iostream>
struct Words {
  std::vector<uint32_t> data;
  mutable std::vector<uint32_t> reads;
  uint32_t operator[](uint32_t i) const { reads.push_back(i); return data.at(i); }
};
struct Vec3 {
  uint32_t x,y,z;
  Vec3(uint32_t a,uint32_t b,uint32_t c):x(a),y(b),z(c){}
};
uint32_t extractBits(uint32_t word,uint32_t offset,uint32_t count) {
  return (word >> offset) & ((uint32_t{1} << count)-1);
}
void require(bool x) { if (!x) throw std::runtime_error("packed vertex read mismatch"); }
''' + '\n'.join(functions) + r'''
int main() {
  unsigned cases=0;
  // End every tested three-byte attribute at the final bound word, across
  // every byte alignment. Test repeated data patterns and both byte orders.
  for (uint32_t words=1;words<=16;++words) {
    for (uint32_t offset=0;offset+3<=words*4;++offset) {
      for (uint32_t seed: {0u,1u,0x80u,0xffu}) {
        Words p;
        std::vector<uint32_t> bytes(words*4);
        for (uint32_t i=0;i<bytes.size();++i) bytes[i]=(seed+i*37u)&255u;
        for (uint32_t i=0;i<words;++i) p.data.push_back(bytes[i*4] | bytes[i*4+1]<<8 | bytes[i*4+2]<<16 | bytes[i*4+3]<<24);
        const auto expected=bytes[offset]|bytes[offset+1]<<8|bytes[offset+2]<<16;
        require(load_u24(p,offset,true)==expected);
        require(load_u24(p,offset,false)==(bytes[offset]<<16|bytes[offset+1]<<8|bytes[offset+2]));
        const auto v=raw_fetch_u8_3(p,offset);
        require(v.x==bytes[offset] && v.y==bytes[offset+1] && v.z==bytes[offset+2]);
        for (auto word:p.reads) require(word>=offset/4 && word<=(offset+2)/4);
        ++cases;
      }
    }
  }
  // Original helper is retained as a negative control: at byte 1, its fourth
  // byte crosses the binding although all three requested bytes are valid.
  Words tail{{0x44332211u},{}};
  bool caught=false;
  try { (void)load_u32_raw(tail,1); } catch (const std::out_of_range&) { caught=true; }
  require(caught);
  std::cout << "Packed vertex read checks passed: " << cases << " cases; original overread caught.\n";
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-packed-read-') as temp:
    path = Path(temp)
    (path/'test.cpp').write_text(cpp)
    for opt in ['-O0', '-O2']:
        subprocess.run(['clang++', '-std=c++20', opt, '-fsanitize=undefined,address',
                        str(path/'test.cpp'), '-o', str(path/'test')], check=True)
        subprocess.run([str(path/'test')], check=True)
