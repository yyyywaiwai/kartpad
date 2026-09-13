"""Exercise the actual patched helper with injected SDL failures under sanitizers."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/aurora-metal-view-lifetime.patch'


@unittest.skipUnless(shutil.which('clang++'), 'requires clang++ and sanitizers')
class MetalViewLifetimeTests(unittest.TestCase):
    def test_actual_helper_ownership_and_failures(self):
        # The patch replaces this complete small upstream file; reconstruct its
        # preimage so this regression also runs without private runtime inputs.
        before = ''.join(line[1:] + '\n' for line in PATCH.read_text().splitlines()
                         if line.startswith((' ', '-')) and not line.startswith('---'))
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            source = tmp / 'lib/dawn/MetalBinding.mm'
            source.parent.mkdir(parents=True)
            source.write_text(before)
            subprocess.run(['patch', '--batch', '-p1', '-d', d, '-i', str(PATCH)],
                           capture_output=True, text=True, check=True)
            (tmp / 'Foundation').mkdir()
            (tmp / 'Foundation/Foundation.h').write_text('')
            (tmp / 'SDL3').mkdir()
            stub = r'''
#pragma once
#include <map>
#include <memory>
#include <cassert>
#include <cstdio>
#define SDLCALL
struct SDL_Window { int id; };
using SDL_PropertiesID = int;
using SDL_MetalView = void*;
using Cleanup = void(*)(void*, void*);
struct Property { void* view; Cleanup cleanup; };
inline std::map<int, Property> props;
inline int creates = 0, destroys = 0;
inline bool failProperties = false, failCreate = false, failSet = false, failLayer = false;
inline int SDL_GetWindowProperties(SDL_Window* w) { return w && !failProperties ? w->id : 0; }
inline void* SDL_GetPointerProperty(int id, const char*, void*) {
  auto p = props.find(id); return p == props.end() ? nullptr : p->second.view;
}
inline void SDL_Metal_DestroyView(void* view) { ++destroys; delete static_cast<int*>(view); }
inline void* SDL_Metal_CreateView(SDL_Window*) { if (failCreate) return nullptr; ++creates; return new int(creates); }
inline bool SDL_SetPointerPropertyWithCleanup(int id, const char*, void* view, Cleanup cleanup, void*) {
  if (failSet) { cleanup(nullptr, view); return false; }
  assert(!props.count(id)); props[id] = {view, cleanup}; return true;
}
inline void* SDL_Metal_GetLayer(void* view) { return failLayer ? nullptr : view; }
inline bool SDL_ClearProperty(int id, const char*) {
  auto p = props.find(id);
  if (p != props.end()) { p->second.cleanup(nullptr, p->second.view); props.erase(p); }
  return true;
}
namespace wgpu {
struct ChainedStruct {};
struct SurfaceSourceMetalLayer : ChainedStruct { void* layer = nullptr; };
}
'''
            (tmp / 'stub.hpp').write_text(stub)
            for header in ['SDL_metal.h', 'SDL_video.h', 'SDL_properties.h']:
                (tmp / 'SDL3' / header).write_text('#include "stub.hpp"\n')
            (source.parent / 'BackendBinding.hpp').write_text('#include "stub.hpp"\n')
            test = tmp / 'test.cpp'
            test.write_text(r'''
#include "lib/dawn/MetalBinding.mm"
using aurora::webgpu::utils::SetupWindowAndGetSurfaceDescriptorCocoa;
auto get(SDL_Window* w) { return SetupWindowAndGetSurfaceDescriptorCocoa(w); }
void reset() { assert(props.empty()); assert(creates == destroys); creates = destroys = 0; }
int main() {
  SDL_Window a{1}, b{2};
  assert(!get(nullptr)); assert(creates == 0);
  failProperties = true; assert(!get(&a)); assert(creates == 0); failProperties = false;
  failCreate = true; assert(!get(&a)); assert(props.empty()); failCreate = false;
  failSet = true; assert(!get(&a)); assert(creates == 1 && destroys == 1); failSet = false; reset();
  failLayer = true; assert(!get(&a)); assert(creates == 1 && destroys == 1); failLayer = false; reset();
  auto layer = static_cast<wgpu::SurfaceSourceMetalLayer*>(get(&a).get())->layer;
  for (int i = 0; i < 100; ++i) {
    auto desc = get(&a);
    assert(static_cast<wgpu::SurfaceSourceMetalLayer*>(desc.get())->layer == layer);
  }
  assert(creates == 1 && destroys == 0); // descriptors do not own the view
  auto second = get(&b);
  assert(static_cast<wgpu::SurfaceSourceMetalLayer*>(second.get())->layer != layer);
  assert(creates == 2);
  SDL_ClearProperty(a.id, ""); assert(destroys == 1);
  assert(get(&b)); assert(creates == 2); // separate windows do not share ownership
  SDL_ClearProperty(b.id, ""); reset();
  assert(get(&a)); assert(creates == 1); // window ID reuse creates a fresh view
  failLayer = true; assert(!get(&a)); assert(destroys == 1); failLayer = false;
  assert(get(&a)); assert(creates == 2); // retry after failed layer
  SDL_ClearProperty(a.id, ""); reset();
  puts("PASS: null window, properties/create/set/layer failures, retry, recovery, two windows and teardown");
}
''')
            binary = tmp / 'test'
            subprocess.run(['clang++', '-std=c++20', '-fsanitize=address,undefined',
                            '-fno-omit-frame-pointer', '-I' + d, str(test), '-o', str(binary)],
                           capture_output=True, text=True, check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            self.assertIn('PASS:', result.stdout)


if __name__ == '__main__':
    unittest.main()
