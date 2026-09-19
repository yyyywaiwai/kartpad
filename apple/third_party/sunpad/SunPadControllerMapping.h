#pragma once

#import <Foundation/Foundation.h>

#include "SunPadInputState.h"

NS_ASSUME_NONNULL_BEGIN

typedef NS_OPTIONS(uint16_t, SunPadPhysicalControllerButton) {
    SunPadPhysicalControllerButtonA = 1 << 0,
    SunPadPhysicalControllerButtonB = 1 << 1,
    SunPadPhysicalControllerButtonX = 1 << 2,
    SunPadPhysicalControllerButtonY = 1 << 3,
    SunPadPhysicalControllerButtonLeftShoulder = 1 << 4,
    SunPadPhysicalControllerButtonRightShoulder = 1 << 5,
    SunPadPhysicalControllerButtonDpadUp = 1 << 6,
    SunPadPhysicalControllerButtonDpadDown = 1 << 7,
    SunPadPhysicalControllerButtonDpadLeft = 1 << 8,
    SunPadPhysicalControllerButtonDpadRight = 1 << 9,
    SunPadPhysicalControllerButtonLeftTrigger = 1 << 10,
    SunPadPhysicalControllerButtonRightTrigger = 1 << 11,
};

typedef struct {
    SunPadPhysicalControllerButton gameA;
    SunPadPhysicalControllerButton gameB;
    SunPadPhysicalControllerButton gameX;
    SunPadPhysicalControllerButton gameY;
    SunPadPhysicalControllerButton gameZ;
    SunPadPhysicalControllerButton gameR;
    SunPadPhysicalControllerButton gameL;
    SunPadPhysicalControllerButton gameUp, gameDown, gameLeft, gameRight;
} SunPadControllerButtonMapping;

FOUNDATION_EXPORT SunPadControllerButtonMapping SunPadDefaultControllerButtonMapping(void);
FOUNDATION_EXPORT BOOL SunPadControllerButtonMappingIsValid(
    SunPadControllerButtonMapping mapping);
FOUNDATION_EXPORT uint16_t SunPadApplyControllerButtonMapping(
    SunPadControllerButtonMapping mapping,
    SunPadPhysicalControllerButton pressedButtons);
FOUNDATION_EXPORT SunPadControllerButtonMapping SunPadControllerButtonMappingByAssigning(
    SunPadControllerButtonMapping mapping,
    SunPadPhysicalControllerButton physicalButton,
    uint16_t gameButton);
FOUNDATION_EXPORT SunPadControllerButtonMapping SunPadControllerButtonMappingBySharing(
    SunPadControllerButtonMapping mapping, SunPadPhysicalControllerButton physicalButton,
    uint16_t gameButton);
FOUNDATION_EXPORT NSString *SunPadPhysicalControllerButtonName(
    SunPadPhysicalControllerButton button);
FOUNDATION_EXPORT uint8_t SunPadControllerRightTriggerPressure(
    uint8_t triggerPressure, BOOL rightShoulderPressed);

/* App-local action mapping. Sticks and Menu remain direct. */
@interface SunPadControllerMappingStore : NSObject

+ (SunPadControllerButtonMapping)mapping;
+ (void)setMapping:(SunPadControllerButtonMapping)mapping;
+ (void)reset;

@end

NS_ASSUME_NONNULL_END
