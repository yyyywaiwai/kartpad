#!/usr/bin/env python3
"""Compile exact SDL button delivery functions with host focus/device stand-ins."""
from pathlib import Path
import subprocess
import sys
import tempfile

def function(path, signature):
    source = Path(path).read_text()
    start = source.index(signature)
    opening = source.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]

code = r'''
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
using Uint64 = uint64_t;
using Uint8 = uint8_t;
struct SDL_Joystick {
 bool swap_face_buttons=false;
 unsigned nbuttons=4;
 bool buttons[4]{};
 Uint64 update_complete=0;
 int instance_id=7;
};
struct SDL_Event {
 int type=0;
 struct { Uint64 timestamp=0; } common;
 struct { int which=0; Uint8 button=0; bool down=false; } jbutton;
};
constexpr int SDL_EVENT_JOYSTICK_BUTTON_DOWN=1, SDL_EVENT_JOYSTICK_BUTTON_UP=2;
constexpr int SDL_GLOBAL_KEYBOARD_ID=0;
std::vector<SDL_Event> events;
bool unfocused=false;
void SDL_AssertJoysticksLocked() {}
void SDL_LockJoysticks() {}
void SDL_UnlockJoysticks() {}
bool SDL_PrivateJoystickShouldIgnoreEvent() { return unfocused; }
bool SDL_EventEnabled(int) { return true; }
void SDL_PushEvent(SDL_Event* event) { events.push_back(*event); }
#define SDL_assert assert
struct SDL_joylist_item { SDL_Joystick* joystick=nullptr; } item;
SDL_joylist_item* JoystickByDeviceId(int id) { return id==7 ? &item : nullptr; }
Uint64 SDL_GetTicksNS() { return 1; }
// The mapping and registry are deliberately controlled; focus delivery is under test.
int keycode_to_SDL(int code) { return code==96 ? 0 : -1; }
int button_to_scancode(int button) { return button; }
unsigned keyboardEvents=0;
void SDL_SendKeyboardKey(Uint64, int, int, int, bool) { ++keyboardEvents; }
'''
code += function(sys.argv[1], "void SDL_SendJoystickButton(") + "\n"
code += function(sys.argv[2], "bool Android_OnPadDown(") + "\n"
code += function(sys.argv[2], "bool Android_OnPadUp(") + "\n"
code += r'''
int main() {
 SDL_Joystick pad;
 item.joystick=&pad;
 assert(Android_OnPadDown(7,96));
 assert(pad.buttons[0] && events.size()==1);
 unfocused=true;
 assert(Android_OnPadUp(7,96));
 assert(!pad.buttons[0] && events.size()==2 && !events.back().jbutton.down);
 std::cout << "PASS SDL native button-up remains delivered without focus\n";
 assert(Android_OnPadDown(7,96));
 assert(!pad.buttons[0] && events.size()==2);
 assert(Android_OnPadUp(7,96));
 assert(events.size()==2);
 std::cout << "PASS background down is ignored; duplicate neutral release adds no event\n";
 unfocused=false;
 assert(Android_OnPadDown(7,96));
 assert(Android_OnPadUp(7,96));
 assert(events.size()==4 && !pad.buttons[0]);
 std::cout << "PASS foreground down/up remains symmetric\n";
 item.joystick=nullptr;
 assert(Android_OnPadDown(7,96)); assert(Android_OnPadUp(7,96));
 assert(keyboardEvents==2 && events.size()==4);
 std::cout << "PASS unopened Android pad uses symmetric keyboard fallback\n";
}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-sdl-button-focus-") as temporary:
    cpp, binary = Path(temporary)/"probe.cpp", Path(temporary)/"probe"
    cpp.write_text(code)
    subprocess.run(["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
