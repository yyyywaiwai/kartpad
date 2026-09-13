// Exercises the actual native settings implementation without game startup,
// Mii-manager code, user-defaults access, device input, or renderer creation.
#import <AppKit/AppKit.h>
#include "runtime_config.h"
#include <cassert>
static int reloadCalls=0;
static void KartPadRequestSettingsReload(){++reloadCalls;}
static void KartPadRequestControllerCompatibility(){}
static bool KPFullscreenAcrossNotch(){return false;}
@interface TestControllers : NSObject <NSWindowDelegate>
@property(nonatomic,strong) NSView *content;
@end
@implementation TestControllers
- (void)cancelCapture{}
- (void)windowWillClose:(NSNotification *)note{(void)note;}
- (void)prepareInPanel:(NSPanel *)panel{(void)panel;self.content=[NSView new];}
- (void)activateInput{}
@end
static TestControllers *KPControllers(){static TestControllers *c=[TestControllers new];return c;}
@interface KartPadMacShellController : NSObject <NSTabViewDelegate>
@property(nonatomic,strong) NSPanel *settingsPanel;
@property(nonatomic,strong) NSTabView *settingsTabs;
@property(nonatomic,strong) NSMutableDictionary<NSString *,NSControl *> *settingControls;
@property(nonatomic,strong) NSMutableDictionary<NSString *,NSArray *> *settingChoices;
@property(nonatomic,strong) NSMutableDictionary<NSString *,NSTextField *> *settingValues;
@property(nonatomic,strong) NSTextField *settingsStatus;
@end
@implementation KartPadMacShellController
- (NSTextField *)label:(NSString *)text{return [NSTextField labelWithString:text];}
#include "KartPadMacSettings.inc.mm"
@end
static void select(KartPadMacShellController *c,NSString *key,NSInteger index){
 NSPopUpButton *p=(NSPopUpButton *)c.settingControls[key];[p selectItemAtIndex:index];
 [p sendAction:p.action to:p.target];
}
int main(int argc,char **argv){@autoreleasepool {
 assert(argc==3);
 const auto expected=std::filesystem::canonical(argv[1]);
 assert(RuntimeConfigFile::PortableRootDirectory()==expected);
 assert(RuntimeConfigFile::ApplicationDataDirectory()==expected/"UserData");
 [NSApplication sharedApplication];[NSApp setActivationPolicy:NSApplicationActivationPolicyAccessory];
 KartPadMacShellController *c=[KartPadMacShellController new];[c showSettings:nil];
 NSButton *vsync=(NSButton *)c.settingControls[@"video.vsync"];
 if(std::string(argv[2])=="reopen"){
  assert(vsync.state==NSControlStateValueOn);
  [vsync performClick:nil];assert(RuntimeConfigFile::LoadConfigFile().vsync==false);
  assert(reloadCalls==0);[c.settingsPanel close];puts("PASS: native checkbox persisted across process restart");return 0;
 }
 assert(vsync.state==NSControlStateValueOff);
 [vsync performClick:nil];assert(RuntimeConfigFile::LoadConfigFile().vsync==true);
 assert(reloadCalls==0);assert([c.settingsStatus.stringValue containsString:@"Quit and reopen"]);
 [c.settingsPanel close];[c showSettings:nil];assert(vsync.state==NSControlStateValueOn);
 select(c,@"video.display_mode",1);assert(RuntimeConfigFile::LoadConfigFile().displayMode=="borderless");
 select(c,@"video.frame_interpolation_fps",1);assert(RuntimeConfigFile::LoadConfigFile().frameInterpolationFps==120);
 NSSlider *volume=(NSSlider *)c.settingControls[@"audio.volume"];volume.doubleValue=35;[volume sendAction:volume.action to:volume.target];
 assert(std::abs(RuntimeConfigFile::LoadConfigFile().audioVolume.value_or(0)-0.35f)<0.001f);assert(reloadCalls==3);
 auto configPath=RuntimeConfigFile::ResolveConfigPath();
 const auto permissions=std::filesystem::status(configPath).permissions();
 std::filesystem::permissions(configPath,std::filesystem::perms::owner_read);
 [vsync performClick:nil];assert([c.settingsStatus.stringValue containsString:@"Could not save"]);assert(reloadCalls==3);
 std::filesystem::permissions(configPath,permissions);[c refreshSettings];
 [vsync performClick:nil];[vsync performClick:nil];assert(reloadCalls==3);
 [c.settingsPanel setContentSize:NSMakeSize(820,570)];[c.settingsTabs selectTabViewItemAtIndex:1];[c.settingsTabs selectTabViewItemAtIndex:0];
 NSScrollView *scroll=(NSScrollView *)c.settingsTabs.selectedTabViewItem.view;
 assert(std::abs(NSMaxY(scroll.contentView.bounds)-NSHeight(scroll.documentView.frame))<1);
 [vsync scrollRectToVisible:vsync.bounds];
 [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.2]];
 [c.settingsPanel displayIfNeeded];
 assert(NSContainsRect(scroll.documentVisibleRect,vsync.frame));
 assert(NSMinY(vsync.frame)>=0 && NSMaxY(vsync.frame)<=NSHeight(scroll.documentView.frame));
 for(NSView *view in scroll.documentView.subviews){if(view==vsync)continue;assert(!NSIntersectsRect(view.frame,vsync.frame));}
 if(std::getenv("KARTPAD_SETTINGS_UI_CAPTURE")) {
  NSTask *capture=[NSTask new];capture.executableURL=[NSURL fileURLWithPath:@"/usr/sbin/screencapture"];
  capture.arguments=@[@"-x",@"-l",[@(c.settingsPanel.windowNumber) stringValue],
      [NSString stringWithUTF8String:(expected/"settings-vsync.png").c_str()]];
  NSError *error=nil;assert([capture launchAndReturnError:&error]);[capture waitUntilExit];assert(capture.terminationStatus==0);
 }
 [c.settingsPanel close];puts("PASS: actual native checkbox action/save/error/reopen, adjacent controls, small-window scroll and row layout");
}}
