#include "../../apple/mobile/KartPadClassicInput.h"
#include "../../apple/mobile/KartPadPhysicalControllers.h"
#include "../../apple/third_party/sunpad/SunPadControllerSlots.h"

#import <GameController/GameController.h>

// Exercise reconciliation with Apple's mutable snapshot controllers, without
// substituting the production slot, latch, mapping, or connection code.
@interface KartPadPhysicalControllers (Fixture)
- (void)reconcileControllerList:(NSArray<GCController *> *)controllers;
- (void)publishController:(GCController *)controller gamepad:(GCExtendedGamepad *)gamepad;
@end

#include <cstdlib>
#include <iostream>
#include <stdexcept>

namespace {

void Require(const bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

void TestExactSunPadSlotReconciliation() {
  constexpr uintptr_t first = 0x1001;
  constexpr uintptr_t second = 0x2001;
  constexpr uintptr_t returned = 0x1002;
  SunPadControllerSlots slots;
  auto result = slots.Reconcile({first, second});
  Require(result.assigned.size() == 2, "two controllers were not assigned");
  Require(slots.SlotFor(first) == 0 && slots.SlotFor(second) == 1,
          "initial player slots changed");
  result = slots.Reconcile({second});
  Require(result.removed.size() == 1 && result.removed[0].slot == 0,
          "disconnected player one was not removed");
  result = slots.Reconcile({second, returned});
  Require(slots.SlotFor(returned) == 0 && slots.SlotFor(second) == 1,
          "stable slots were not preserved after reconnect");
}

void TestRegistrationAndReconnect() {
  KartPadPhysicalControllers *bridge = [KartPadPhysicalControllers new];
  NSMutableArray<GCController *> *pads = [NSMutableArray array];
  for (unsigned player = 0; player < 4; ++player) {
    [pads addObject:[GCController controllerWithExtendedGamepad]];
  }
  [bridge reconcileControllerList:pads];
  Require([bridge connectedControllerCount] == 4, "four pads not detected");
  for (unsigned player = 1; player < 4; ++player) {
    GCController *pad = pads[player];
    [pad.extendedGamepad.buttonA setValue:1];
    [bridge publishController:pad gamepad:pad.extendedGamepad];
    [pad.extendedGamepad.buttonA setValue:0];
    [bridge publishController:pad gamepad:pad.extendedGamepad];
    for (unsigned probe = 0; probe < 8; ++probe) {
      Require([bridge isPlayerConnected:player], "WPAD connection query lost physical pad");
    }
    SunPadInputState state{};
    Require([bridge consumePlayer:player state:&state], "registered pad cannot read");
    Require((state.buttons & SunPadButtonA) != 0, "connection probe consumed registration A");
    [bridge consumePlayer:player state:&state];
    Require(state.buttons == 0, "released registration button remained held");
  }
  GCController *removed = pads[1];
  [bridge reconcileControllerList:@[pads[0], pads[2], pads[3]]];
  Require(![bridge isPlayerConnected:1], "disconnected player still present");
  Require([bridge isPlayerConnected:2] && [bridge isPlayerConnected:3],
          "disconnect shifted other player slots");
  [bridge reconcileControllerList:@[pads[3], removed, pads[0], pads[2]]];
  Require([bridge isPlayerConnected:1], "reconnected player missing");
  Require(![bridge isPlayerConnected:4] && ![bridge isPlayerConnected:NSUIntegerMax],
          "invalid player accepted");
  [bridge reconcileControllerList:@[]];
}

void TestControllerSampleMapping() {
  KartPadPhysicalControllerSample sample;
  sample.faceButtons = static_cast<SunPadPhysicalControllerButton>(
      SunPadPhysicalControllerButtonA | SunPadPhysicalControllerButtonB |
      SunPadPhysicalControllerButtonX | SunPadPhysicalControllerButtonY |
      SunPadPhysicalControllerButtonLeftShoulder);
  sample.menu = true;
  sample.dpadUp = true;
  sample.dpadRight = true;
  sample.rightShoulder = true;
  sample.leftX = -1.4f;
  sample.leftY = 0.5f;
  sample.rightX = 0.25f;
  sample.rightY = -0.75f;
  sample.leftTrigger = 0.5f;
  sample.rightTrigger = 0.25f;

  const SunPadInputState state = KartPadAdaptPhysicalControllerSample(
      sample, SunPadDefaultControllerButtonMapping());
  const uint16_t expectedButtons =
      SunPadButtonA | SunPadButtonB | SunPadButtonX | SunPadButtonY |
      SunPadButtonZ | SunPadButtonStart | SunPadButtonDpadUp |
      SunPadButtonDpadRight | SunPadButtonL | SunPadButtonR;
  Require(state.connected == 1, "controller connection was lost");
  Require(state.buttons == expectedButtons, "SunPad physical mapping changed");
  Require(state.stickX == -127 && state.stickY == 64,
          "left stick normalization changed");
  Require(state.cStickX == 32 && state.cStickY == -95,
          "right stick normalization changed");
  Require(state.triggerL == 128 && state.triggerR == 128,
          "trigger pressure mapping changed");

  const KartPadClassicInputState classic =
      kartpad::mobile::AdaptSunPadInput(state);
  Require(classic.connected, "Classic controller connection was lost");
  Require((classic.buttons & kartpad::mobile::kClassicButtonA) != 0,
          "physical A did not reach Classic A");
  Require((classic.buttons & kartpad::mobile::kClassicButtonR) != 0,
          "physical trigger did not reach Classic R");
  Require((classic.buttons & kartpad::mobile::kClassicButtonPlus) != 0,
          "physical Menu did not reach Classic Plus");
}

}  // namespace

int main() {
  @autoreleasepool {
    try {
      TestExactSunPadSlotReconciliation();
      TestControllerSampleMapping();
      TestRegistrationAndReconnect();
      std::cout << "KartPad mobile physical-controller bridge passed\n";
      return EXIT_SUCCESS;
    } catch (const std::exception& error) {
      std::cerr << "KartPad mobile physical-controller bridge failed: "
                << error.what() << '\n';
      return EXIT_FAILURE;
    }
  }
}
