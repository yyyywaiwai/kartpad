#!/usr/bin/env python3
"""Exercise prepared Aurora cache functions; injected event loss is a hypothesis."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
source = (root / "aurora-main/lib/input.cpp").read_text()
header = (root / "aurora-main/include/aurora/input.hpp").read_text()
kpad = (root / "src/hle/input/kpad.cpp").read_text()
trigger = re.search(r"const uint32_t classicTrigger = ([^;]+);", kpad)
if trigger is None:
    raise RuntimeError("prepared KPAD classic trigger expression not found")

def function(signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]

code = r'''
#include <atomic>
#include <cassert>
#include <cstdint>
#include <map>
#include <mutex>
#include <iostream>
using Uint32 = uint32_t;
using Uint8 = uint8_t;
enum SDL_GamepadButton {
 SDL_GAMEPAD_BUTTON_SOUTH, SDL_GAMEPAD_BUTTON_EAST, SDL_GAMEPAD_BUTTON_WEST,
 SDL_GAMEPAD_BUTTON_NORTH, SDL_GAMEPAD_BUTTON_BACK, SDL_GAMEPAD_BUTTON_START,
 SDL_GAMEPAD_BUTTON_LEFT_SHOULDER, SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER,
 SDL_GAMEPAD_BUTTON_DPAD_UP, SDL_GAMEPAD_BUTTON_DPAD_DOWN,
 SDL_GAMEPAD_BUTTON_DPAD_LEFT, SDL_GAMEPAD_BUTTON_DPAD_RIGHT
};
struct FakePad {};
unsigned closed = 0, assignments = 0;
void SDL_CloseGamepad(FakePad*) { ++closed; }
bool SDL_RumbleGamepad(FakePad*, uint16_t, uint16_t, uint32_t) { return true; }
struct Logger { template<class... T> void info(T...) {} } Log;
'''
code += header.replace("#pragma once", "")
code += r'''
namespace aurora::input {
struct GameController {
 int m_playerIndex = -1;
 FakePad* m_controller = nullptr;
 bool m_hasRumble = false, m_standardRumbleEnabled = false, m_standardRumbleDirty = false;
 uint32_t m_standardButtons = 0, m_standardButtonPresses = 0;
 int16_t m_standardLeftX=0, m_standardLeftY=0, m_standardLeftTrigger=0, m_standardRightTrigger=0;
};
std::map<int, GameController> g_GameControllers;
std::mutex g_standardGamepadBridgeMutex;
std::atomic<bool> g_standardGamepadsActive{true};
void apply_port_preferences() { ++assignments; }
'''
for signature in (
    "static GameController* resolve_standard_gamepad(",
    "bool read_standard_gamepad_state(",
    "void set_standard_gamepads_active(",
    "uint32_t standard_button_mask(",
    "void update_standard_gamepad_button(",
    "void remove_controller(",
):
    code += function(signature) + "\n"
code += "\nuint32_t guest_trigger(uint32_t classicHold, uint32_t previousClassic) {\n"
code += "  const bool fixtureActive = false; const uint32_t pendingClassic = 0;\n"
code += "  return " + trigger.group(1) + ";\n}\n"
code += r'''
}
int main() {
 using namespace aurora::input;
 FakePad physical;
 auto reset = [&] {
   g_GameControllers.clear();
   auto& pad = g_GameControllers[7];
   pad.m_playerIndex = 0; pad.m_controller = &physical;
   g_standardGamepadsActive = true;
 };
 auto read = [&] {
   StandardGamepadState state;
   read_standard_gamepad_state(0, true, &state);
   return state;
 };
 auto down = [&] { update_standard_gamepad_button(7, SDL_GAMEPAD_BUTTON_SOUTH, true); };
 auto up = [&] { update_standard_gamepad_button(7, SDL_GAMEPAD_BUTTON_SOUTH, false); };
 constexpr auto A = kStandardGamepadSouth;
 reset(); down(); up();
 assert(read().buttons == A); assert(read().buttons == 0);
 std::cout << "PASS short tap retained for exactly one guest sample\n";
 reset(); down(); assert(read().buttons == A);
 set_standard_gamepads_active(false);
 assert(!read().connected && read().buttons == 0);
 set_standard_gamepads_active(true);
 assert(read().buttons == A); up(); assert(read().buttons == 0);
 std::cout << "PASS genuinely held A survives suspension; delivered release clears\n";
 reset(); down(); assert(read().buttons == A);
 set_standard_gamepads_active(false); up(); set_standard_gamepads_active(true);
 assert(read().buttons == 0);
 std::cout << "PASS release delivered while suspended prevents stale A\n";
 reset(); set_standard_gamepads_active(false); down(); up(); set_standard_gamepads_active(true);
 assert(read().buttons == A); assert(read().buttons == 0);
 std::cout << "OBSERVED suspended short tap is deferred once, not held indefinitely\n";
 reset(); down(); assert(read().buttons == A);
 set_standard_gamepads_active(false);
 // Deliberately omit up(): this models event loss; it does not prove SDL loses it.
 set_standard_gamepads_active(true);
 for (unsigned i=0; i<20; ++i) assert(read().buttons == A);
 // The actual KPAD classicHold & ~previousClassic rule cannot see a touch A edge
 // while the physical contribution remains held.
 uint32_t previous = A;
 for (const auto touch : {0u, uint32_t(A), 0u}) {
   const auto held = read().buttons | touch;
   assert(guest_trigger(held, previous) == 0); previous = held;
 }
 down(); up(); assert(read().buttons == A); assert(read().buttons == 0);
 std::cout << "HYPOTHESIS injected missing release holds A and masks touch edges; fresh down/up recovers\n";
 reset(); down(); assert(read().buttons == A);
 set_standard_gamepads_active(false); remove_controller(7); set_standard_gamepads_active(true);
 assert(!read().connected && read().buttons == 0);
 assert(closed == 1 && assignments == 1);
 up(); assert(!read().connected);
 std::cout << "PASS actual detach erases held/pending state; late release is harmless\n";
}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-android-lifecycle-") as temporary:
    cpp, binary = Path(temporary) / "probe.cpp", Path(temporary) / "probe"
    cpp.write_text(code)
    subprocess.run(["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
