#pragma once

#import <Foundation/Foundation.h>
#include "kartpad/network/private_wfc.h"

// Shared Apple preference. The runtime reads a launch-time copy so an active
// online session can never be redirected by editing the settings dialog.
static inline NSString *KartPadPrivateServerHost() {
  return [NSUserDefaults.standardUserDefaults stringForKey:@"KartPadPrivateWfcHost"] ?: @"";
}

static inline void KartPadApplyPrivateServerAtLaunch() {
  if (std::getenv(KartPad::Network::kPrivateWfcHostEnvironment)) return;
  NSString *host = KartPadPrivateServerHost();
  if (KartPad::Network::ValidPrivateWfcHost(host.UTF8String)) {
    setenv(KartPad::Network::kPrivateWfcHostEnvironment, host.UTF8String, 1);
  }
}
