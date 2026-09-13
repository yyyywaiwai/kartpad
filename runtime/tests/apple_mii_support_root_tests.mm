#import "KartPadMiiManager.h"
#include "kartpad/mii/mii_database.h"
#include "runtime_config.h"
#include <cassert>
#include <cstdlib>
#include <filesystem>

// The test runner renames Foundation's home lookup at compile time. Even the
// pre-fix manager can only access this synthetic home, never the account's data.
NSString *KartPadTestHomeDirectory(void) {
  const char *home = std::getenv("HOME");
  assert(home != nullptr && home[0] == '/');
  return [NSString stringWithUTF8String:home];
}

static void Write(NSString *path, NSData *data) {
  assert([NSFileManager.defaultManager createDirectoryAtPath:path.stringByDeletingLastPathComponent
      withIntermediateDirectories:YES attributes:nil error:nil]);
  assert([data writeToFile:path options:NSDataWritingAtomic error:nil]);
}

int main(int argc, const char **argv) {
  @autoreleasepool {
    assert(argc == 3);
    NSString *root = [NSString stringWithUTF8String:argv[1]];
    NSString *other = [NSString stringWithUTF8String:argv[2]];
    assert(RuntimeConfigFile::ApplicationDataDirectory() == std::filesystem::path(argv[1]));
    const auto seed = kartpad::mii::CreateSeedDatabase({0x02, 0x17, 0xab, 0x10, 0x20, 0x30});
    NSData *valid = [NSData dataWithBytes:seed.data() length:seed.size()];
    NSData *sentinel = [@"unrelated installation pending data" dataUsingEncoding:NSUTF8StringEncoding];
    NSString *pending = [root stringByAppendingPathComponent:@"PendingRFL_DB.dat"];
    NSString *database = [root stringByAppendingPathComponent:@"NAND/shared2/menu/FaceLib/RFL_DB.dat"];
    NSString *otherPending = [other stringByAppendingPathComponent:@"PendingRFL_DB.dat"];
    Write(pending, valid);
    Write(database, valid);
    Write(otherPending, sentinel);
    assert(KartPadHasPendingMiiChanges());
    NSError *error = nil;
    assert(KartPadApplyPendingMiiDatabase(&error));
    assert(!KartPadHasPendingMiiChanges());
    assert(![NSFileManager.defaultManager fileExistsAtPath:pending]);
    assert([valid isEqual:[NSData dataWithContentsOfFile:database]]);
    assert([[NSFileManager.defaultManager contentsOfDirectoryAtPath:
        [root stringByAppendingPathComponent:@"MiiBackups"] error:nil] count] == 1);
    assert([sentinel isEqual:[NSData dataWithContentsOfFile:otherPending]]);
    assert(![NSFileManager.defaultManager fileExistsAtPath:
        [other stringByAppendingPathComponent:@"MiiBackups"]]);
    puts("Mii pending apply and backup confined to runtime support root; unrelated pending data preserved");
  }
}
