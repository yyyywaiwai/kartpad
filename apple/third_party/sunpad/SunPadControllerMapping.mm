#import "SunPadControllerMapping.h"

#include <initializer_list>

static NSString *const SunPadControllerMappingDefaultsKey =
    @"SunPadControllerButtonMappingV2";

static uint8_t const SunPadRunAndSprayPressure = 128;

static NSArray<NSString *> *SunPadMappingKeys(void) {
    return @[@"A", @"B", @"X", @"Y", @"Z", @"R", @"L", @"Up", @"Down", @"Left", @"Right"];
}

static NSArray<NSNumber *> *SunPadMappingValues(SunPadControllerButtonMapping mapping) {
    return @[@(mapping.gameA), @(mapping.gameB), @(mapping.gameX),
             @(mapping.gameY), @(mapping.gameZ), @(mapping.gameR), @(mapping.gameL),
             @(mapping.gameUp), @(mapping.gameDown), @(mapping.gameLeft), @(mapping.gameRight)];
}

static SunPadPhysicalControllerButton *SunPadMappingSlot(
    SunPadControllerButtonMapping *mapping, uint16_t gameButton) {
    switch (gameButton) {
    case SunPadButtonA: return &mapping->gameA;
    case SunPadButtonB: return &mapping->gameB;
    case SunPadButtonX: return &mapping->gameX;
    case SunPadButtonY: return &mapping->gameY;
    case SunPadButtonZ: return &mapping->gameZ;
    case SunPadButtonR: return &mapping->gameR;
    case SunPadButtonL: return &mapping->gameL;
    case SunPadButtonDpadUp: return &mapping->gameUp;
    case SunPadButtonDpadDown: return &mapping->gameDown;
    case SunPadButtonDpadLeft: return &mapping->gameLeft;
    case SunPadButtonDpadRight: return &mapping->gameRight;
    default: return nullptr;
    }
}

SunPadControllerButtonMapping SunPadDefaultControllerButtonMapping(void) {
    return (SunPadControllerButtonMapping){
        .gameA = SunPadPhysicalControllerButtonA,
        .gameB = SunPadPhysicalControllerButtonB,
        .gameX = SunPadPhysicalControllerButtonX,
        .gameY = SunPadPhysicalControllerButtonY,
        .gameZ = SunPadPhysicalControllerButtonLeftShoulder,
        .gameR = (SunPadPhysicalControllerButton)(SunPadPhysicalControllerButtonRightShoulder | SunPadPhysicalControllerButtonRightTrigger),
        .gameL = SunPadPhysicalControllerButtonLeftTrigger,
        .gameUp = SunPadPhysicalControllerButtonDpadUp,
        .gameDown = SunPadPhysicalControllerButtonDpadDown,
        .gameLeft = SunPadPhysicalControllerButtonDpadLeft,
        .gameRight = SunPadPhysicalControllerButtonDpadRight,
    };
}

BOOL SunPadControllerButtonMappingIsValid(SunPadControllerButtonMapping mapping) {
    for (NSNumber *number in SunPadMappingValues(mapping)) {
        const uint16_t value = number.unsignedShortValue;
        if (value == 0 || (value & ~0x0fffu) != 0) return NO;
    }
    return YES;
}

uint16_t SunPadApplyControllerButtonMapping(
    SunPadControllerButtonMapping mapping,
    SunPadPhysicalControllerButton pressedButtons) {
    if (!SunPadControllerButtonMappingIsValid(mapping))
        mapping = SunPadDefaultControllerButtonMapping();
    uint16_t gameButtons = 0;
    if (pressedButtons & mapping.gameA) gameButtons |= SunPadButtonA;
    if (pressedButtons & mapping.gameB) gameButtons |= SunPadButtonB;
    if (pressedButtons & mapping.gameX) gameButtons |= SunPadButtonX;
    if (pressedButtons & mapping.gameY) gameButtons |= SunPadButtonY;
    if (pressedButtons & mapping.gameZ) gameButtons |= SunPadButtonZ;
    if (pressedButtons & mapping.gameR) gameButtons |= SunPadButtonR;
    if (pressedButtons & mapping.gameL) gameButtons |= SunPadButtonL;
    if (pressedButtons & mapping.gameUp) gameButtons |= SunPadButtonDpadUp;
    if (pressedButtons & mapping.gameDown) gameButtons |= SunPadButtonDpadDown;
    if (pressedButtons & mapping.gameLeft) gameButtons |= SunPadButtonDpadLeft;
    if (pressedButtons & mapping.gameRight) gameButtons |= SunPadButtonDpadRight;
    return gameButtons;
}

SunPadControllerButtonMapping SunPadControllerButtonMappingByAssigning(
    SunPadControllerButtonMapping mapping,
    SunPadPhysicalControllerButton physicalButton,
    uint16_t gameButton) {
    if (!SunPadControllerButtonMappingIsValid(mapping))
        mapping = SunPadDefaultControllerButtonMapping();
    SunPadPhysicalControllerButton *destination = SunPadMappingSlot(&mapping, gameButton);
    if (destination == nullptr)
        return mapping;
    SunPadPhysicalControllerButton previous = *destination;
    if (previous == physicalButton)
        return mapping;
    for (uint16_t candidate : {SunPadButtonA, SunPadButtonB, SunPadButtonX,
                               SunPadButtonY, SunPadButtonZ, SunPadButtonR, SunPadButtonL,
                               SunPadButtonDpadUp, SunPadButtonDpadDown, SunPadButtonDpadLeft, SunPadButtonDpadRight}) {
        SunPadPhysicalControllerButton *slot = SunPadMappingSlot(&mapping, candidate);
        if (slot != nullptr && slot != destination && (*slot & physicalButton) != 0) {
            *slot = (SunPadPhysicalControllerButton)((*slot & ~physicalButton) | previous);
            break;
        }
    }
    *destination = physicalButton;
    return mapping;
}

SunPadControllerButtonMapping SunPadControllerButtonMappingBySharing(
    SunPadControllerButtonMapping mapping, SunPadPhysicalControllerButton physicalButton,
    uint16_t gameButton) {
    if (!SunPadControllerButtonMappingIsValid(mapping)) mapping = SunPadDefaultControllerButtonMapping();
    auto *slot = SunPadMappingSlot(&mapping, gameButton);
    if (slot != nullptr && physicalButton != 0 && !(physicalButton & ~0x0fff)) *slot = physicalButton;
    return mapping;
}

NSString *SunPadPhysicalControllerButtonName(SunPadPhysicalControllerButton button) {
    NSArray<NSString *> *names = @[@"A", @"B", @"X", @"Y", @"Left Shoulder", @"Right Shoulder",
        @"D-pad Up", @"D-pad Down", @"D-pad Left", @"D-pad Right", @"Left Trigger", @"Right Trigger"];
    NSMutableArray<NSString *> *selected = [NSMutableArray array];
    for (NSUInteger i = 0; i < names.count; ++i) if (button & (1u << i)) [selected addObject:names[i]];
    return selected.count ? [selected componentsJoinedByString:@" / "] : @"Unknown";
}

uint8_t SunPadControllerRightTriggerPressure(
    uint8_t triggerPressure, BOOL rightShoulderPressed) {
    return rightShoulderPressed
        ? MAX(triggerPressure, SunPadRunAndSprayPressure)
        : triggerPressure;
}

@implementation SunPadControllerMappingStore

+ (SunPadControllerButtonMapping)mapping {
    NSDictionary *saved = [[NSUserDefaults standardUserDefaults]
        dictionaryForKey:SunPadControllerMappingDefaultsKey];
    BOOL legacy = saved == nil;
    if (legacy) saved = [[NSUserDefaults standardUserDefaults] dictionaryForKey:@"SunPadControllerButtonMappingV1"];
    if (saved == nil) return SunPadDefaultControllerButtonMapping();
    SunPadControllerButtonMapping mapping = SunPadDefaultControllerButtonMapping();
    NSArray<NSString *> *keys = SunPadMappingKeys();
    const uint16_t buttons[] = {SunPadButtonA, SunPadButtonB, SunPadButtonX, SunPadButtonY, SunPadButtonZ,
        SunPadButtonR, SunPadButtonL, SunPadButtonDpadUp, SunPadButtonDpadDown, SunPadButtonDpadLeft, SunPadButtonDpadRight};
    for (NSUInteger i = 0; i < (legacy ? 5u : keys.count); ++i) {
        id value = saved[keys[i]];
        if (![value isKindOfClass:NSNumber.class] || [value unsignedIntegerValue] > 0xfff)
            return SunPadDefaultControllerButtonMapping();
        *SunPadMappingSlot(&mapping, buttons[i]) = (SunPadPhysicalControllerButton)[value unsignedShortValue];
    }
    return SunPadControllerButtonMappingIsValid(mapping)
        ? mapping : SunPadDefaultControllerButtonMapping();
}

+ (void)setMapping:(SunPadControllerButtonMapping)mapping {
    if (!SunPadControllerButtonMappingIsValid(mapping))
        mapping = SunPadDefaultControllerButtonMapping();
    NSArray<NSString *> *keys = SunPadMappingKeys();
    NSArray<NSNumber *> *values = SunPadMappingValues(mapping);
    NSMutableDictionary *saved = [NSMutableDictionary dictionaryWithCapacity:keys.count];
    for (NSUInteger index = 0; index < keys.count; ++index)
        saved[keys[index]] = values[index];
    [[NSUserDefaults standardUserDefaults] setObject:saved
                                              forKey:SunPadControllerMappingDefaultsKey];
}

+ (void)reset {
    [self setMapping:SunPadDefaultControllerButtonMapping()];
}

@end
