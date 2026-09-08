#!/usr/bin/env python3
"""Compile actual prepared Android connection/read functions with a synthetic pad store."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
source = (root / "aurora-main/lib/input.cpp").read_text()
kpad = (root / "src/hle/input/kpad.cpp").read_text()
def function(text, signature):
    start = text.index(signature)
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]

code = r'''
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <map>
#include <mutex>
#undef __APPLE__
#define __ANDROID__ 1
std::array<std::atomic<bool>, 4> g_keyboardConnected{};
namespace kartpad::android { bool IsTouchInputConnected() { return true; } }
namespace aurora::input {
struct GameController {
  int m_playerIndex = -1;
  void* m_controller = nullptr;
  uint32_t m_standardButtons = 0, m_standardButtonPresses = 0;
  int16_t m_standardLeftX=0, m_standardLeftY=0, m_standardLeftTrigger=0, m_standardRightTrigger=0;
};
struct StandardGamepadState {
  bool connected=false; uint32_t buttons=0;
  int16_t leftX=0,leftY=0,leftTrigger=0,rightTrigger=0;
};
std::map<int, GameController> g_GameControllers;
std::mutex g_standardGamepadBridgeMutex;
std::atomic<bool> g_standardGamepadsActive{true};
'''
for signature in ("static GameController* resolve_standard_gamepad(",
                  "bool standard_gamepad_connected(", "bool read_standard_gamepad_state("):
    code += function(source, signature) + "\n"
code += "}\n" + function(kpad, 'extern "C" bool KPAD_IsKeyboardChannelConnected')
code += r'''
int main() {
  using namespace aurora::input;
  for (unsigned player=0; player<4; ++player) {
    auto& pad = g_GameControllers[player];
    pad.m_playerIndex=player;
    pad.m_controller=&pad;
    pad.m_standardButtonPresses=1; // Press/release already occurred between guest polls.
    for (int i=0;i<20;++i) assert(KPAD_IsKeyboardChannelConnected(player));
    StandardGamepadState state;
    assert(read_standard_gamepad_state(player, player==0, &state) && state.buttons==1);
    assert(read_standard_gamepad_state(player, player==0, &state) && state.buttons==0);
  }
  g_GameControllers.erase(2);
  assert(!KPAD_IsKeyboardChannelConnected(2));
  assert(KPAD_IsKeyboardChannelConnected(1) && KPAD_IsKeyboardChannelConnected(3));
  assert(!KPAD_IsKeyboardChannelConnected(4));
  assert(!KPAD_IsKeyboardChannelConnected(UINT32_MAX));
  g_standardGamepadsActive=false;
  assert(!standard_gamepad_connected(1,false));
}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-android-probe-") as temporary:
    cpp, binary = Path(temporary) / "probe.cpp", Path(temporary) / "probe"
    cpp.write_text(code)
    subprocess.run(["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print("Android controller probe passed: 4 slots, 20 probes preserve each short edge, disconnect isolation, invalid channels, suspension")
