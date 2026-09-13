#!/usr/bin/env python3
"""Native tests of prepared VSync selector and real portable Config.toml persistence."""
from pathlib import Path
import subprocess, sys, tempfile
root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).resolve()
def function(text, name):
    start=text.index(name); end=text.index('{',start)+1; depth=1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}'); end+=1
    return text[start:end]
selector=function((source/'aurora-main/lib/webgpu/gpu.cpp').read_text(),'wgpu::PresentMode best_present_mode()')
selector_test=r'''
#include <cassert>
#include <cstddef>
#include <initializer_list>
#include <vector>
namespace wgpu {enum class PresentMode {Immediate,Mailbox,Fifo};enum class BackendType {Metal,Vulkan,Other};}
struct {bool vsync=false;} g_config;
struct {size_t presentModeCount;wgpu::PresentMode* presentModes;} g_surfaceCapabilities;
wgpu::BackendType g_backendType=wgpu::BackendType::Metal;
struct {int warnings=0;template<class... T> void warn(T...){++warnings;}template<class... T> void info(T...){}} Log;
'''+selector+r'''
wgpu::PresentMode choose(bool enabled,wgpu::BackendType backend,std::initializer_list<wgpu::PresentMode> modes){
 std::vector< wgpu::PresentMode> values(modes);g_config.vsync=enabled;g_backendType=backend;
 g_surfaceCapabilities={values.size(),values.data()};return best_present_mode();
}
int main(){using P=wgpu::PresentMode;using B=wgpu::BackendType;
 assert(choose(false,B::Metal,{P::Fifo,P::Immediate})==P::Immediate);
 assert(choose(true,B::Metal,{P::Fifo,P::Immediate})==P::Fifo);
 assert(choose(true,B::Metal,{P::Immediate})==P::Immediate);assert(Log.warnings==1);
 assert(choose(false,B::Metal,{P::Fifo})==P::Fifo);
 assert(choose(false,B::Vulkan,{P::Fifo,P::Immediate,P::Mailbox})==P::Mailbox);
 assert(choose(true,B::Vulkan,{P::Fifo,P::Immediate,P::Mailbox})==P::Mailbox);
 assert(choose(false,B::Other,{P::Immediate,P::Fifo})==P::Immediate);
}
'''
config_test=r'''
#include "runtime_config.h"
#include <cassert>
int main(int argc,char** argv){
 assert(argc==2);const std::string mode=argv[1];
 assert(RuntimeConfigFile::PortableRootDirectory().has_value());
 auto path=RuntimeConfigFile::ResolveConfigPath();
 if(mode=="write"){
  std::filesystem::create_directories(path.parent_path());
  {std::ofstream f(path);f<<"[video]\nshow_fps = false\n";}
  assert(!RuntimeConfigFile::LoadConfigFile().vsync.value_or(false));
  assert(RuntimeConfigFile::WriteSetting("video","vsync","true"));
 }else if(mode=="read"){
  auto c=RuntimeConfigFile::LoadConfigFile();assert(c.vsync.value_or(false));assert(c.showFps==false);
  assert(RuntimeConfigFile::WriteSetting("video","vsync","false"));
 }else if(mode=="off"){
  assert(RuntimeConfigFile::LoadConfigFile().vsync==false);
  assert(RuntimeConfigFile::WriteSetting("video","vsync","\"invalid\""));
  assert(!RuntimeConfigFile::LoadConfigFile().vsync.value_or(false));
  std::filesystem::remove(path);std::filesystem::create_directory(path);
  assert(!RuntimeConfigFile::WriteSetting("video","vsync","true"));
 }
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-vsync-') as temp:
    d=Path(temp);(d/'portable.txt').touch()
    for name,code in [('selector',selector_test),('config',config_test)]:
        f=d/(name+'.cpp');f.write_text(code)
        subprocess.run(['clang++','-std=c++20','-Wall','-Wextra','-Werror','-I'+str(source/'include'),'-isystem',str(source/'third_party/toml11'),str(f),'-o',str(d/name)],check=True)
    subprocess.run([str(d/'selector')],check=True)
    for mode in ('write','read','off'): subprocess.run([str(d/'config'),mode],check=True)
ui=(root/'apple/macos/KartPadMacSettings.inc.mm').read_text()
restart=ui.split('if([key isEqual:@"video.vsync"]) {',1)[1].split('\n  }',1)[0]
assert '[self refreshSettings];return;' in restart and 'KartPadRequestSettingsReload' not in restart
assert 'c.vsync.value_or(false)' in ui
assert 'auroraConfig.vsync = RuntimeConfigFile::Get().vsync.value_or(false)' in (source/'src/main.cpp').read_text()
for path in (root/'scripts').glob('prepare-*-runtime.sh'):
    if path.name!='prepare-g7-game-runtime.sh': assert 'macos-vsync-startup.patch' not in path.read_text()
print('PASS: real selector capability matrix; native config persistence across processes, malformed/default values, unrelated key preservation, save failure; restart-only UI contract and macOS preparation isolation')
