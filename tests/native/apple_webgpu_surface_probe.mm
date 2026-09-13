// Automated Dawn/Metal surface recreation. No game, saves, or debugger attachment.
#import <Foundation/Foundation.h>
#import <QuartzCore/CAMetalLayer.h>
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
#include <string_view>

namespace aurora::webgpu::utils {
std::shared_ptr<wgpu::ChainedStruct> SetupWindowAndGetSurfaceDescriptorCocoa(SDL_Window*);
}
namespace {
SDL_Window* window;
wgpu::Instance instance;
wgpu::Adapter adapter;
wgpu::Device device;
wgpu::Queue queue;
wgpu::Surface surface;
wgpu::SurfaceConfiguration config;
CAMetalLayer* originalLayer;
#if TARGET_OS_OSX
NSWindow* nativeWindow;
NSView* originalRoot;
NSButton* overlay;
#else
UIWindow* nativeWindow;
UIView* originalRoot;
UIButton* overlay;
#endif
unsigned frames = 0, recreations = 0;

void check(bool ok, const char* message) {
  if (!ok) {
    fprintf(stderr, "FAIL: %s; frame=%u recreations=%u SDL=%s\n",
            message, frames, recreations, SDL_GetError());
    fflush(stderr);
    exit(1);
  }
}

void drain() {
  bool completed = false;
  auto future = queue.OnSubmittedWorkDone(wgpu::CallbackMode::WaitAnyOnly,
      [&completed](wgpu::QueueWorkDoneStatus status, wgpu::StringView) {
        completed = status == wgpu::QueueWorkDoneStatus::Success;
      });
  check(instance.WaitAny(future, 5000000000) == wgpu::WaitStatus::Success && completed,
        "submitted GPU work completes");
}

void checkViews() {
#if TARGET_OS_OSX
  check(nativeWindow.contentView == originalRoot, "native root survives surface recreation");
#else
  check(nativeWindow.rootViewController.view == originalRoot, "native root survives surface recreation");
#endif
  check(overlay.superview == originalRoot && overlay.window == nativeWindow,
        "native overlay remains in the window");
}

void createSurface() {
  // Match Aurora's descriptor -> release old surface -> create new surface order.
  auto chain = aurora::webgpu::utils::SetupWindowAndGetSurfaceDescriptorCocoa(window);
  check(bool(chain), "Metal surface descriptor exists");
  auto layer = (__bridge CAMetalLayer*)static_cast<wgpu::SurfaceSourceMetalLayer*>(chain.get())->layer;
  if (originalLayer) {
    check(layer == originalLayer, "Metal layer survives real WebGPU surface recreation");
    checkViews();
  } else {
    originalLayer = layer;
  }
  if (surface) {
    surface.Unconfigure();
    surface = {};
    drain();
  }
  wgpu::SurfaceDescriptor descriptor{.nextInChain = chain.get(), .label = "Recovery probe"};
  surface = instance.CreateSurface(&descriptor);
  check(bool(surface), "Dawn creates surface");
}

void initialize() {
  check(SDL_Init(SDL_INIT_VIDEO), "SDL video initializes");
  window = SDL_CreateWindow("KartPad graphics recovery check", 640, 480,
                             SDL_WINDOW_METAL | SDL_WINDOW_RESIZABLE);
  check(window != nullptr, "SDL window exists");
  const auto feature = wgpu::InstanceFeatureName::TimedWaitAny;
  const wgpu::InstanceDescriptor descriptor{.requiredFeatureCount = 1, .requiredFeatures = &feature};
  instance = wgpu::CreateInstance(&descriptor);
  check(bool(instance), "Dawn instance exists");
  createSurface();
#if TARGET_OS_OSX
  nativeWindow = (__bridge NSWindow*)SDL_GetPointerProperty(SDL_GetWindowProperties(window),
      SDL_PROP_WINDOW_COCOA_WINDOW_POINTER, nullptr);
  originalRoot = nativeWindow.contentView;
  overlay = [[NSButton alloc] initWithFrame:NSMakeRect(20, 20, 320, 50)];
  overlay.title = @"Automatic graphics recovery check";
#else
  nativeWindow = (__bridge UIWindow*)SDL_GetPointerProperty(SDL_GetWindowProperties(window),
      SDL_PROP_WINDOW_UIKIT_WINDOW_POINTER, nullptr);
  originalRoot = nativeWindow.rootViewController.view;
  overlay = [[UIButton alloc] initWithFrame:CGRectMake(20, 20, 320, 50)];
  [overlay setTitle:@"Automatic graphics recovery check" forState:UIControlStateNormal];
#endif
  [originalRoot addSubview:overlay];
  const wgpu::RequestAdapterOptions options{.backendType = wgpu::BackendType::Metal,
                                           .compatibleSurface = surface};
  auto future = instance.RequestAdapter(&options, wgpu::CallbackMode::WaitAnyOnly,
      [](wgpu::RequestAdapterStatus status, wgpu::Adapter result, wgpu::StringView) {
        if (status == wgpu::RequestAdapterStatus::Success) adapter = std::move(result);
      });
  check(instance.WaitAny(future, 5000000000) == wgpu::WaitStatus::Success && adapter,
        "Metal adapter request succeeds");
  wgpu::DeviceDescriptor deviceDescriptor{};
  deviceDescriptor.SetUncapturedErrorCallback(
      [](const wgpu::Device&, wgpu::ErrorType, wgpu::StringView message) {
        const std::string_view text{message};
        fprintf(stderr, "Dawn error: %.*s\n", int(text.size()), text.data());
        check(false, "no uncaptured Dawn error");
      });
  future = adapter.RequestDevice(&deviceDescriptor, wgpu::CallbackMode::WaitAnyOnly,
      [](wgpu::RequestDeviceStatus status, wgpu::Device result, wgpu::StringView) {
        if (status == wgpu::RequestDeviceStatus::Success) device = std::move(result);
      });
  check(instance.WaitAny(future, 5000000000) == wgpu::WaitStatus::Success && device,
        "Metal device request succeeds");
  queue = device.GetQueue();
  wgpu::SurfaceCapabilities caps;
  check(surface.GetCapabilities(adapter, &caps) == wgpu::Status::Success && caps.formatCount,
        "surface capabilities available");
  int width = 0, height = 0;
  check(SDL_GetWindowSizeInPixels(window, &width, &height) && width > 0 && height > 0,
        "native pixel dimensions available");
  config.device = device;
  config.format = caps.formats[0];
  config.usage = wgpu::TextureUsage::RenderAttachment;
  config.width = width;
  config.height = height;
  config.presentMode = wgpu::PresentMode::Fifo;
  config.alphaMode = caps.alphaModes[0];
  surface.Configure(&config);
}

void frame() {
  // A bounded automatic trigger replaces debugger-driven fault injection here.
  // Each cycle has visible frames before and after a real surface replacement.
  if (frames != 0 && frames % 30 == 0) {
    drain();
    createSurface();
    surface.Configure(&config);
    ++recreations;
  }
  wgpu::SurfaceTexture acquired;
  surface.GetCurrentTexture(&acquired);
  check(acquired.status == wgpu::SurfaceGetCurrentTextureStatus::SuccessOptimal ||
        acquired.status == wgpu::SurfaceGetCurrentTextureStatus::SuccessSuboptimal,
        "surface texture acquired after recovery");
  check(bool(acquired.texture), "acquired surface texture exists");
  wgpu::RenderPassColorAttachment color{};
  color.view = acquired.texture.CreateView();
  color.loadOp = wgpu::LoadOp::Clear;
  color.storeOp = wgpu::StoreOp::Store;
  color.clearValue = {0.05, 0.15 + 0.15 * recreations, 0.3, 1.0};
  const wgpu::RenderPassDescriptor passDescriptor{.colorAttachmentCount = 1, .colorAttachments = &color};
  auto encoder = device.CreateCommandEncoder();
  auto pass = encoder.BeginRenderPass(&passDescriptor);
  pass.End();
  auto command = encoder.Finish();
  queue.Submit(1, &command);
  check(surface.Present() == wgpu::Status::Success, "Dawn presents frame");
  checkViews();
  ++frames;
  SDL_Delay(16);
}

void finish() {
  drain();
  check(recreations == 3 && frames == 120, "all recovery cycles completed");
  surface.Unconfigure();
  surface = {};
  config.device = {};
  queue = {};
  device = {};
  adapter = {};
  instance = {};
  overlay = nil;
  originalRoot = nil;
  nativeWindow = nil;
  originalLayer = nil;
  SDL_DestroyWindow(window);
  SDL_Quit();
  fprintf(stderr, "PASS: 3 real Dawn surface recreations; 120 acquired/submitted/presented frames; root, overlay and Metal layer preserved\n");
  fflush(stderr);
}
} // namespace
#define SDL_MAIN_USE_CALLBACKS 1
#include <SDL3/SDL_main.h>
SDL_AppResult SDL_AppInit(void**, int, char**) { initialize(); return SDL_APP_CONTINUE; }
SDL_AppResult SDL_AppIterate(void*) {
  frame();
  if (frames < 120) return SDL_APP_CONTINUE;
  finish();
  return SDL_APP_SUCCESS;
}
SDL_AppResult SDL_AppEvent(void*, SDL_Event* event) {
  return event->type == SDL_EVENT_QUIT ? SDL_APP_FAILURE : SDL_APP_CONTINUE;
}
void SDL_AppQuit(void*, SDL_AppResult) {}
