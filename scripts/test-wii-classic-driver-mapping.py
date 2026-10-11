#!/usr/bin/env python3
"""Check the built SDL Wii driver's Classic button reports against actual KPAD mapping.

Synthetic packets only; does not establish Bluetooth latency or physical acceptance.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('runtime', type=Path)
parser.add_argument('sdl', type=Path)
args = parser.parse_args()
runtime = (args.runtime / 'src/wii_remote_input.cpp').read_text()
driver = (args.sdl / 'src/joystick/hidapi/SDL_hidapi_wii.c').read_text()

def block(source, signature):
    start = source.index(signature)
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

constants = runtime[runtime.index('constexpr uint32_t kClUp'):]
constants = constants[:constants.index(';') + 1]
classic = block(runtime, '    if (kind == Kind::RemoteWithClassic) {')
code = r'''
#include <SDL3/SDL_gamepad.h>
#include "wii_remote_input.h"
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
using namespace WiiRemoteInput;
std::array<bool, 64> buttons{};
std::array<Sint16, SDL_GAMEPAD_AXIS_COUNT> axes{};
bool SDL_GetJoystickButton(SDL_Joystick*, int index) { return buttons.at(index); }
Sint16 SDL_GetGamepadAxis(SDL_Gamepad*, SDL_GamepadAxis axis) { return axes.at(axis); }
'''
code += constants + '\n' + block(runtime, 'int16_t ClassicStickRaw(') + '\n'
code += block(driver, 'static const Uint8 GAMEPAD_BUTTON_DEFS[3][8] = {') + ';\n'
code += '''KpadSample samplePacket(unsigned pressed) {
 buttons.fill(false); axes.fill(0);
 // On the wire extension buttons are active-low, high byte first.
 const unsigned char packet[2] = {static_cast<unsigned char>(~(pressed >> 8)),
                                  static_cast<unsigned char>(~pressed)};
 for (int byte=0; byte<2; ++byte) for (int bit=0; bit<8; ++bit) {
   const auto button=GAMEPAD_BUTTON_DEFS[byte][bit];
   if (button!=0xff) buttons[button]=!(packet[byte] & (1<<bit));
 }
 SDL_Gamepad* gamepad=nullptr; SDL_Joystick* joystick=nullptr;
 KpadSample sample{}; const auto kind=Kind::RemoteWithClassic;
'''
code += classic + '\nreturn sample; }\n'
code += r'''
int main() {
 // Independent Wii Classic protocol bits for every button posted by this SDL table.
 constexpr unsigned mask=0xfe7b; // excludes reserved bits and analog-axis ZL/ZR
 for (unsigned input=0; input<=0xffff; ++input) {
   const auto sample=samplePacket(input);
   assert(sample.hasClassic);
   assert(sample.clHold==(input & mask));
   assert(sample.hold==0); // extension buttons must not become remote core buttons
 }
 assert(samplePacket(0x0001).clHold==0x0001); // up
 assert(samplePacket(0x4000).clHold==0x4000); // down
 assert(samplePacket(0x0002).clHold==0x0002); // left
 assert(samplePacket(0x8000).clHold==0x8000); // right
 assert(samplePacket(0x8001).clHold==0x8001); // diagonal
 assert(samplePacket(0).clHold==0); // release
}
'''
with tempfile.TemporaryDirectory(prefix='kartpad-classic-') as temp:
    path = Path(temp)
    (path / 'test.cpp').write_text(code)
    subprocess.run(['clang++', '-std=c++20', '-fsanitize=address,undefined', '-g',
                    '-I' + str(args.runtime.resolve() / 'include'),
                    '-I' + str(args.sdl.resolve() / 'include'),
                    str(path / 'test.cpp'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
print('PASS: 65,536 synthetic Classic packets; SDL raw button table to KPAD, D-pad and release')
