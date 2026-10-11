#!/usr/bin/env python3
"""Exercise the maintained present-mode selector with Android and desktop policies."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'vendor/runtimes/android/aurora-main/lib/webgpu/gpu.cpp').read_text()
start = source.index('wgpu::PresentMode best_present_mode() {')
end = source.index('\nwgpu::TextureFormat to_linear', start)
function = source[start:end]
prefix = '''#include <cstddef>
#include <initializer_list>
#include <cassert>
#include <iostream>
namespace wgpu {enum class PresentMode{Fifo,Mailbox,Immediate}; enum class BackendType{Vulkan,Metal,OpenGLES};}
struct {size_t presentModeCount; const wgpu::PresentMode* presentModes;} g_surfaceCapabilities;
wgpu::BackendType g_backendType;
unsigned target;
unsigned aurora_get_frame_interpolation_fps(){return target;}
struct Logger {template<class...T>void warn(T...){}} Log;
'''
main = '''
int main(){
using P=wgpu::PresentMode;using B=wgpu::BackendType;
unsigned cases=0;
auto check=[&](B backend,unsigned fps,std::initializer_list<P> modes,P expected){
g_backendType=backend;target=fps;g_surfaceCapabilities={modes.size(),modes.begin()};assert(best_present_mode()==expected);++cases;};
#ifdef __ANDROID__
check(B::Vulkan,0,{P::Fifo,P::Mailbox,P::Immediate},P::Fifo);
#else
check(B::Vulkan,0,{P::Fifo,P::Mailbox,P::Immediate},P::Mailbox);
#endif
for(auto fps:{120u,180u,240u})check(B::Vulkan,fps,{P::Fifo,P::Mailbox,P::Immediate},P::Mailbox);
check(B::Vulkan,0,{P::Mailbox,P::Immediate},P::Mailbox);
check(B::Vulkan,120,{P::Fifo,P::Immediate},P::Immediate);
check(B::Vulkan,120,{P::Fifo},P::Fifo);
check(B::Vulkan,0,{P::Fifo},P::Fifo);
check(B::OpenGLES,0,{P::Fifo,P::Mailbox,P::Immediate},P::Immediate);
check(B::Metal,0,{P::Fifo,P::Immediate},P::Immediate);
check(B::Metal,0,{P::Fifo,P::Mailbox},P::Fifo);
check(B::OpenGLES,120,{P::Fifo,P::Mailbox},P::Mailbox);
std::cout<<cases<<" production present-mode cases passed\\n";
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-present-mode-') as directory:
    output = Path(directory)
    cpp = output / 'present-mode-cases.cpp'
    cpp.write_text(prefix + function + main)
    for name, flags in [('android', ['-D__ANDROID__']), ('other', [])]:
        executable = output / ('present-mode-' + name)
        subprocess.run(['clang++', '-std=c++20', '-Wall', '-Wextra', '-Werror',
                        *flags, str(cpp), '-o', str(executable)], check=True)
        subprocess.run([str(executable)], check=True)
