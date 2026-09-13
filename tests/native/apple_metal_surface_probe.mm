// Native SDL/Metal recovery probe. No game code, data or installed KartPad state.
#import <Foundation/Foundation.h>
#import <QuartzCore/CAMetalLayer.h>
#import <Metal/Metal.h>
#import <TargetConditionals.h>
#if TARGET_OS_OSX
#import <Cocoa/Cocoa.h>
#else
#import <UIKit/UIKit.h>
#endif
#include <SDL3/SDL.h>
#include "BackendBinding.hpp"
#include <cstdio>
#include <cstdlib>
namespace aurora::webgpu::utils {
std::shared_ptr<wgpu::ChainedStruct> SetupWindowAndGetSurfaceDescriptorCocoa(SDL_Window*);
}
static void check(bool ok, const char* message) {
  if (!ok) { fprintf(stderr, "FAIL: %s (%s)\n", message, SDL_GetError()); fflush(stderr); exit(1); }
}
static CAMetalLayer* descriptor(SDL_Window* window) {
  auto d = aurora::webgpu::utils::SetupWindowAndGetSurfaceDescriptorCocoa(window);
  check(bool(d), "descriptor exists");
  return (__bridge CAMetalLayer*)static_cast<wgpu::SurfaceSourceMetalLayer*>(d.get())->layer;
}
static void runProbe() {
  check(SDL_Init(SDL_INIT_VIDEO), "SDL video init");
  for (int cycle = 0; cycle < 3; ++cycle) {
    __weak CAMetalLayer* destroyedLayer;
    @autoreleasepool {
      auto window = SDL_CreateWindow("KartPad Metal recovery test", 640, 480, SDL_WINDOW_METAL | SDL_WINDOW_RESIZABLE);
      check(window != nullptr, "create window");
      CAMetalLayer* layer = descriptor(window);
      destroyedLayer = layer;
#if TARGET_OS_OSX
      NSWindow* native = (__bridge NSWindow*)SDL_GetPointerProperty(SDL_GetWindowProperties(window), SDL_PROP_WINDOW_COCOA_WINDOW_POINTER, nullptr);
      NSView* root = native.contentView;
      NSButton* overlay = [[NSButton alloc] initWithFrame:NSMakeRect(20,20,100,40)];
#else
      UIWindow* native = (__bridge UIWindow*)SDL_GetPointerProperty(SDL_GetWindowProperties(window), SDL_PROP_WINDOW_UIKIT_WINDOW_POINTER, nullptr);
      UIView* root = native.rootViewController.view;
      UIButton* overlay = [[UIButton alloc] initWithFrame:CGRectMake(20,20,100,40)];
#endif
      [root addSubview:overlay];
      for (int recovery = 0; recovery < 100; ++recovery) {
        @autoreleasepool {
          check(descriptor(window) == layer, "recovery preserves Metal layer");
#if TARGET_OS_OSX
          check(native.contentView == root, "recovery preserves root");
#else
          check(native.rootViewController.view == root, "recovery preserves root");
#endif
          check(overlay.superview == root && overlay.window == native, "overlay remains attached to visible window");
          SDL_PumpEvents();
        }
      }
      layer.device = MTLCreateSystemDefaultDevice();
      layer.pixelFormat = MTLPixelFormatBGRA8Unorm;
      id<CAMetalDrawable> drawable = [layer nextDrawable];
      check(drawable != nil, "drawable after repeated recovery");
      auto pass = [MTLRenderPassDescriptor renderPassDescriptor];
      pass.colorAttachments[0].texture = drawable.texture;
      pass.colorAttachments[0].loadAction = MTLLoadActionClear;
      pass.colorAttachments[0].storeAction = MTLStoreActionStore;
      pass.colorAttachments[0].clearColor = MTLClearColorMake(0.05, 0.35, 0.15, 1);
      auto queue = [layer.device newCommandQueue];
      auto buffer = [queue commandBuffer];
      auto encoder = [buffer renderCommandEncoderWithDescriptor:pass];
      [encoder endEncoding];
      [buffer presentDrawable:drawable];
      [buffer commit];
      [buffer waitUntilCompleted];
      check(buffer.status == MTLCommandBufferStatusCompleted, "Metal presentation completes");
      SDL_DestroyWindow(window);
    }
    for (int i = 0; i < 20 && destroyedLayer != nil; ++i) {
      @autoreleasepool { CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, false); }
    }
    check(destroyedLayer == nil, "window teardown releases Metal layer");
  }
  SDL_Quit();
  fprintf(stderr, "PASS: 300 descriptor recoveries; root/overlay/layer stable; 3 presentations and window teardowns\n"); fflush(stderr);
}
#define SDL_MAIN_USE_CALLBACKS 1
#include <SDL3/SDL_main.h>
SDL_AppResult SDL_AppInit(void**, int, char**) { runProbe(); return SDL_APP_SUCCESS; }
SDL_AppResult SDL_AppIterate(void*) { return SDL_APP_SUCCESS; }
SDL_AppResult SDL_AppEvent(void*, SDL_Event*) { return SDL_APP_CONTINUE; }
void SDL_AppQuit(void*, SDL_AppResult) {}
