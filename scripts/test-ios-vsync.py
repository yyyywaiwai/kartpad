#!/usr/bin/env python3
"""Exercise the iOS present-mode selector with real source and fake surface capabilities."""

from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
runtime = root / "vendor/runtimes/ios"
source = (runtime / "aurora-main/lib/webgpu/gpu.cpp").read_text()
start = source.index("wgpu::PresentMode best_present_mode() {")
end = source.index("\nwgpu::TextureFormat to_linear", start)
selector = source[start:end]

program = r'''
#include <cassert>
#include <cstddef>
#include <initializer_list>
namespace wgpu {
enum class PresentMode { Fifo, Mailbox, Immediate };
enum class BackendType { Metal, Vulkan };
}
struct { bool vsync = false; } g_config;
struct { size_t presentModeCount; const wgpu::PresentMode* presentModes; } g_surfaceCapabilities;
wgpu::BackendType g_backendType = wgpu::BackendType::Metal;
unsigned targetFps = 0;
unsigned aurora_get_frame_interpolation_fps() { return targetFps; }
struct { template<class... T> void warn(T...) {} } Log;
''' + selector + r'''
int main() {
  using P = wgpu::PresentMode;
  using B = wgpu::BackendType;
  auto check = [](bool enabled, B backend, unsigned fps,
                  std::initializer_list<P> modes, P expected) {
    g_config.vsync = enabled;
    g_backendType = backend;
    targetFps = fps;
    g_surfaceCapabilities = {modes.size(), modes.begin()};
    assert(best_present_mode() == expected);
  };
  check(false, B::Metal, 0, {P::Fifo, P::Immediate}, P::Immediate);
  check(true, B::Metal, 0, {P::Fifo, P::Immediate}, P::Fifo);
  check(true, B::Metal, 120, {P::Fifo, P::Immediate}, P::Immediate);
  check(true, B::Metal, 0, {P::Immediate}, P::Immediate);
  check(true, B::Vulkan, 0, {P::Fifo, P::Mailbox}, P::Mailbox);
}
'''

with tempfile.TemporaryDirectory(prefix="kartpad-ios-vsync-") as temp:
    source_file = Path(temp) / "selector.cpp"
    binary = Path(temp) / "selector"
    source_file.write_text(program)
    subprocess.run(["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
                    str(source_file), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)

config = (runtime / "runtime/include/runtime_config.h").read_text()
main = (runtime / "runtime/src/main.cpp").read_text()
assert 'config.vsync = FindConfigValue<bool>(document, "video", "vsync")' in config
assert "auroraConfig.vsync = RuntimeConfigFile::Get().vsync.value_or(false)" in main
assert "presentModeChanged" in source
print("PASS: iOS default, FIFO opt-in, interpolation, unsupported mode and backend policies")
