#!/usr/bin/env python3
"""Compile the prepared runtime's actual WPAD detection functions in isolation.

Run after prepare-ios-game-runtime.sh (or the tvOS preparation). This catches
an integration regression that a pure host-input test cannot see.
"""
import pathlib
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
kpad = (root / "src/hle/input/kpad.cpp").read_text()
wpad = (root / "src/hle/input/wpad.cpp").read_text()

def function(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]

code = r'''
#include <array>
#include <atomic>
#include <cassert>
#include <cstdint>
#undef TARGET_OS_IOS
#define TARGET_OS_IOS 1
#undef TARGET_OS_TV
#define TARGET_OS_TV 0
std::array<std::atomic<bool>, 4> g_keyboardConnected{};
std::array<bool, 4> physical{};
bool KartPadMobileIsControllerConnected(unsigned chan) { return physical.at(chan); }
namespace WpadContract {
constexpr unsigned kChannelCount = 4, kExtensionClassic = 2;
constexpr int kErrorBadChannel = -1, kErrorNoController = -2;
}
constexpr int kStatusOk = 0;
namespace Memory { unsigned type = 0; void Write32(unsigned, unsigned value) { type = value; } }
'''
code += function(kpad, 'extern "C" bool KPAD_IsKeyboardChannelConnected')
code += function(wpad, 'extern "C" int32_t WPADProbe_HLE')
code += r'''
int main() {
    assert(WPADProbe_HLE(0, 1) == 0);
    for (unsigned chan = 1; chan < 4; ++chan) {
        assert(WPADProbe_HLE(chan, 1) == WpadContract::kErrorNoController);
        physical[chan] = true;
        for (unsigned probe = 0; probe < 8; ++probe) {
            assert(WPADProbe_HLE(chan, 1) == 0);
            assert(Memory::type == WpadContract::kExtensionClassic);
        }
        physical[chan] = false;
        assert(WPADProbe_HLE(chan, 1) == WpadContract::kErrorNoController);
        g_keyboardConnected[chan] = true;
        assert(WPADProbe_HLE(chan, 1) == 0);
    }
    assert(WPADProbe_HLE(4, 1) == WpadContract::kErrorBadChannel);
    assert(WPADProbe_HLE(UINT32_MAX, 1) == WpadContract::kErrorBadChannel);
}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-wpad-probe-") as temporary:
    source = pathlib.Path(temporary) / "probe.cpp"
    binary = pathlib.Path(temporary) / "probe"
    for mobile, tv in ((1, 0), (0, 1)):
        source.write_text(code.replace("#define TARGET_OS_IOS 1", f"#define TARGET_OS_IOS {mobile}")
                         .replace("#define TARGET_OS_TV 0", f"#define TARGET_OS_TV {tv}"))
        subprocess.run(["xcrun", "clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror",
                        str(source), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
print("Prepared runtime WPAD physical controller registration passed")
