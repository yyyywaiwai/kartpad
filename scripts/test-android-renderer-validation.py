#!/usr/bin/env python3
"""Check actual prepared Dawn toggle construction for normal and diagnostic runs."""
from pathlib import Path
import subprocess
import sys
import tempfile

source = (Path(sys.argv[1]) / 'aurora-main/lib/webgpu/gpu.cpp').read_text()
start = source.index('    const char* rendererValidationFlag')
end = source.index('\n#endif', source.index('    const wgpu::DawnTogglesDescriptor togglesDescriptor', start))
code = r'''
#include <algorithm>
#include <array>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <string_view>
#include <vector>
namespace wgpu {
enum class BackendType { Vulkan };
struct DawnTogglesDescriptor {
  void* nextInChain;
  size_t enabledToggleCount; const char* const* enabledToggles;
  size_t disabledToggleCount; const char* const* disabledToggles;
};
}
struct { template<class... T> void info(T...) {} } Log;
void require(bool condition) { if (!condition) throw std::runtime_error("wrong Dawn toggle configuration"); }
int main() {
  for (const char* flag : std::array<const char*, 5>{nullptr, "", "0", "true", "1"}) {
    if (flag) setenv("KARTPAD_RENDERER_VALIDATION", flag, 1);
    else unsetenv("KARTPAD_RENDERER_VALIDATION");
    std::vector<const char*> enableToggles;
    int cacheDescriptor = 0;
    auto g_backendType = wgpu::BackendType::Vulkan;
''' + source[start:end] + r'''
    const bool expected = flag && std::string_view(flag) == "1";
    const auto& d = togglesDescriptor;
    auto enabled = [&](std::string_view name) {
      return std::any_of(d.enabledToggles, d.enabledToggles+d.enabledToggleCount,
                        [&](const char* value) { return value == name; });
    };
#ifdef NDEBUG
    require(enabled("skip_validation") == !expected);
    require(enabled("disable_robustness") == !expected);
#else
    require(!enabled("skip_validation") && !enabled("disable_robustness"));
#endif
    require(d.disabledToggleCount == (expected ? 2 : 0));
    if (expected) {
      require(std::string_view(d.disabledToggles[0]) == "skip_validation");
      require(std::string_view(d.disabledToggles[1]) == "disable_robustness");
    } else require(d.disabledToggles == nullptr);
    require(enabled("vulkan_monolithic_pipeline_cache"));
  }
}
'''
with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / 'test.cpp'
    cpp.write_text(code)
    for release in (False, True):
        exe = Path(directory) / ('release' if release else 'debug')
        command = ['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror']
        if release:
            command.append('-DNDEBUG')
        subprocess.run(command + [str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
print('PASS: normal and opt-in Dawn toggles, five environment states, debug and release')
