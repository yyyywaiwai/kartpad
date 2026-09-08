#include <filesystem>
#include <iostream>
#include <memory>
#include <optional>
#include <string>

#include "DiscIO/DiscExtractor.h"
#include "DiscIO/Filesystem.h"
#include "DiscIO/Volume.h"

#if defined(__ANDROID__)
#include <fcntl.h>
#include <unistd.h>
#include "../android/app/src/main/cpp/kartpad_disc_image_volume.h"
#endif

#if defined(KARTPAD_FMT_ALLOC_SHIM)
// The feasibility oracle is linked against the reference build's fmt v12 ABI.
// Its system fmt archive is macOS-only, so provide the one allocation shim that
// Dolphin's logging object needs instead of linking a host-platform object.
namespace fmt::v12::detail
{
void* allocate(std::size_t size)
{
  return ::operator new(size);
}
}  // namespace fmt::v12::detail
#endif

int main(int argc, char** argv)
{
#if defined(__ANDROID__)
  if (argc == 4 && std::string(argv[1]) == "--fd")
  {
    // Reserve sibling descriptor numbers to reproduce the old WBFS basename
    // bug deterministically. The original picker descriptor stays readable.
    const int source = open(argv[2], O_RDONLY);
    if (source < 0) return 65;
    for (int fd = 120; fd <= 129; ++fd)
      if (dup2(source, fd) != fd) return 65;
    auto legacy = DiscIO::CreateVolume("/proc/self/fd/123");
    auto volume = KartPadOpenDiscDescriptor(123);
    unsigned char magic[4]{};
    const bool source_readable = pread(source, magic, sizeof(magic), 0) == sizeof(magic);
    const auto* filesystem = volume ? volume->GetFileSystem(volume->GetGamePartition()) : nullptr;
    const bool valid = volume && volume->GetGameID(volume->GetGamePartition()) == "RMCP01" &&
                       filesystem && filesystem->IsValid();
    std::cout << "descriptor-import=" << (valid ? "passed" : "failed")
              << " source-readable=" << source_readable
              << " legacy-open=" << bool(legacy) << '\n';
    if (!valid || !source_readable) return 66;
    std::filesystem::create_directories(argv[3]);
    return DiscIO::ExportSystemData(*volume, volume->GetGamePartition(), argv[3]) ? 0 : 68;
  }
#endif
  if (argc != 3)
  {
    std::cerr << "usage: ios-discio-probe IMAGE DESTINATION\n";
    return 64;
  }

  std::unique_ptr<DiscIO::Volume> volume = DiscIO::CreateVolume(argv[1]);
  if (!volume)
  {
    std::cerr << "open failed\n";
    return 65;
  }

  const DiscIO::Partition partition = volume->GetGamePartition();
  const DiscIO::FileSystem* filesystem = volume->GetFileSystem(partition);
  if (!filesystem || !filesystem->IsValid())
  {
    std::cerr << "filesystem failed\n";
    return 66;
  }

  const std::string game_id = volume->GetGameID(partition);
  const std::optional<u16> revision = volume->GetRevision(partition);
  std::cout << "game=" << game_id << " revision="
            << (revision ? std::to_string(*revision) : "missing")
            << " children=" << filesystem->GetRoot().GetTotalChildren() << '\n';
  if (game_id != "RMCP01" || revision != std::optional<u16>{0})
  {
    std::cerr << "unsupported disc\n";
    return 67;
  }

  std::error_code error;
  std::filesystem::create_directories(argv[2], error);
  if (error || !DiscIO::ExportSystemData(*volume, partition, argv[2]))
  {
    std::cerr << "system export failed\n";
    return 68;
  }

  std::cout << "system export passed\n";
  return 0;
}
