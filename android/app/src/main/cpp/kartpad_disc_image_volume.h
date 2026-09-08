#pragma once

#include <array>
#include <memory>
#include <string>
#include <utility>

#include "Common/DirectIOFile.h"
#include "DiscIO/Blob.h"
#include "DiscIO/FileBlob.h"
#include "DiscIO/Volume.h"
#include "DiscIO/WbfsBlob.h"

// A picker grants one image, not access to filename-derived siblings. In
// particular, WbfsFileReader must never treat /proc/self/fd/123 as a basename
// and open descriptors 121, 122, ... as split WBFS files.
inline std::unique_ptr<DiscIO::Volume> KartPadOpenDiscDescriptor(int fd) {
  if (fd < 0) return nullptr;
  // SAF grants the descriptor, not permission to reopen its underlying path.
  // Duplicate it without changing its offset or taking ownership from Java.
  File::DirectIOFile file = File::DirectIOFile::DuplicateFileDescriptor(fd);
  std::array<unsigned char, 4> magic{};
  if (!file.IsOpen() || !file.Read(magic.data(), magic.size())) return nullptr;
  file.Seek(0, File::SeekOrigin::Begin);
  std::unique_ptr<DiscIO::BlobReader> reader;
  if (magic == std::array<unsigned char, 4>{'W', 'B', 'F', 'S'}) {
    reader = DiscIO::WbfsFileReader::Create(std::move(file), "");
  } else {
    reader = DiscIO::PlainFileReader::Create(std::move(file));
  }
  return reader ? DiscIO::CreateVolume(std::move(reader)) : nullptr;
}
