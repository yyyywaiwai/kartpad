#pragma once

#include "kartpad/mii/seed_mii_database.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace kartpad::mii {

inline constexpr std::size_t kMaximumMiiSlots = 100;
inline constexpr std::size_t kMiiNameByteSize = 20;
inline constexpr std::size_t kCreateIdByteSize = 8;

struct MiiRecord {
    std::size_t slot = 0;
    std::string name;
    std::string creatorName;
    uint32_t createId = 0;
    uint8_t favoriteColor = 0;
};

struct DatabaseResult {
    bool ok = false;
    std::string message;

    explicit operator bool() const { return ok; }
};

inline uint16_t ReadBigEndian16(std::span<const uint8_t> bytes,
                                std::size_t offset) {
    return static_cast<uint16_t>((static_cast<uint16_t>(bytes[offset]) << 8) |
                                 bytes[offset + 1]);
}

inline uint32_t ReadBigEndian32(std::span<const uint8_t> bytes,
                                std::size_t offset) {
    return (static_cast<uint32_t>(bytes[offset]) << 24) |
           (static_cast<uint32_t>(bytes[offset + 1]) << 16) |
           (static_cast<uint32_t>(bytes[offset + 2]) << 8) |
           static_cast<uint32_t>(bytes[offset + 3]);
}

inline void AppendUtf8(std::string& output, uint32_t codePoint) {
    if (codePoint <= 0x7Fu) {
        output.push_back(static_cast<char>(codePoint));
    } else if (codePoint <= 0x7FFu) {
        output.push_back(static_cast<char>(0xC0u | (codePoint >> 6)));
        output.push_back(static_cast<char>(0x80u | (codePoint & 0x3Fu)));
    } else if (codePoint <= 0xFFFFu) {
        output.push_back(static_cast<char>(0xE0u | (codePoint >> 12)));
        output.push_back(static_cast<char>(0x80u | ((codePoint >> 6) & 0x3Fu)));
        output.push_back(static_cast<char>(0x80u | (codePoint & 0x3Fu)));
    } else {
        output.push_back(static_cast<char>(0xF0u | (codePoint >> 18)));
        output.push_back(static_cast<char>(0x80u | ((codePoint >> 12) & 0x3Fu)));
        output.push_back(static_cast<char>(0x80u | ((codePoint >> 6) & 0x3Fu)));
        output.push_back(static_cast<char>(0x80u | (codePoint & 0x3Fu)));
    }
}

inline std::string ReadMiiName(std::span<const uint8_t> block,
                               std::size_t offset) {
    std::string result;
    for (std::size_t index = 0; index < 10; ++index) {
        const uint16_t first = ReadBigEndian16(block, offset + index * 2);
        if (first == 0) {
            break;
        }
        uint32_t codePoint = first;
        if (first >= 0xD800u && first <= 0xDBFFu && index + 1 < 10) {
            const uint16_t second =
                ReadBigEndian16(block, offset + (index + 1) * 2);
            if (second >= 0xDC00u && second <= 0xDFFFu) {
                codePoint = 0x10000u +
                    ((static_cast<uint32_t>(first) - 0xD800u) << 10) +
                    (static_cast<uint32_t>(second) - 0xDC00u);
                ++index;
            }
        }
        if (codePoint < 0x20u || (codePoint >= 0xD800u && codePoint <= 0xDFFFu)) {
            continue;
        }
        AppendUtf8(result, codePoint);
    }
    return result;
}

inline bool IsEmptyMii(std::span<const uint8_t> block) {
    return std::all_of(block.begin(), block.end(),
                       [](uint8_t byte) { return byte == 0; });
}

inline DatabaseResult ValidateMii(std::span<const uint8_t> block) {
    if (block.size() != kMiiBlockSize) {
        return {false, "A Mii file must contain exactly 74 bytes."};
    }
    const bool allZero = IsEmptyMii(block);
    const bool allFF = std::all_of(block.begin(), block.end(),
                                   [](uint8_t byte) { return byte == 0xFF; });
    if (allZero || allFF) {
        return {false, "The selected Mii file is empty."};
    }
    const uint16_t header = ReadBigEndian16(block, 0);
    // RFLiCharData's high header bit is padding0, not an invalid flag.
    // Raw database exporters preserve it; validate the actual fields below.
    const uint8_t month = static_cast<uint8_t>((header >> 10) & 0x0Fu);
    const uint8_t day = static_cast<uint8_t>((header >> 5) & 0x1Fu);
    const uint8_t color = static_cast<uint8_t>((header >> 1) & 0x0Fu);
    if (month > 12 || day > 31 || color > 11) {
        return {false, "The selected file contains invalid Mii metadata."};
    }
    if (ReadMiiName(block, 0x02).empty()) {
        return {false, "The selected Mii has no readable name."};
    }
    if (ReadBigEndian32(block, 0x18) == 0) {
        return {false, "The selected Mii has no creation ID."};
    }
    if (block[0x16] > 127 || block[0x17] > 127) {
        return {false, "The selected Mii has an invalid height or weight."};
    }
    return {true, {}};
}

inline DatabaseResult ValidateDatabase(std::span<const uint8_t> database) {
    if (database.size() < kDatabaseCrcOffset + 2) {
        return {false, "The Mii database is truncated."};
    }
    if (database[0] != 'R' || database[1] != 'N' || database[2] != 'O' ||
        database[3] != 'D') {
        return {false, "The Mii database header is invalid."};
    }
    const uint16_t stored = ReadBigEndian16(database, kDatabaseCrcOffset);
    const uint16_t calculated = Crc16Ccitt(database.first(kDatabaseCrcOffset));
    if (stored != calculated) {
        return {false, "The Mii database checksum is invalid."};
    }
    return {true, {}};
}

inline void UpdateDatabaseCrc(std::span<uint8_t> database) {
    const uint16_t crc = Crc16Ccitt(
        std::span<const uint8_t>(database.data(), kDatabaseCrcOffset));
    WriteBigEndian16(database, kDatabaseCrcOffset, crc);
}

inline std::vector<MiiRecord> ListMiis(std::span<const uint8_t> database) {
    std::vector<MiiRecord> records;
    if (!ValidateDatabase(database)) {
        return records;
    }
    for (std::size_t slot = 0; slot < kMaximumMiiSlots; ++slot) {
        const std::size_t offset = kMiiBlockOffset + slot * kMiiBlockSize;
        if (offset + kMiiBlockSize > database.size()) {
            break;
        }
        const auto block = database.subspan(offset, kMiiBlockSize);
        if (IsEmptyMii(block) || !ValidateMii(block)) {
            continue;
        }
        const uint16_t header = ReadBigEndian16(block, 0);
        records.push_back({slot, ReadMiiName(block, 0x02),
                           ReadMiiName(block, 0x36),
                           ReadBigEndian32(block, 0x18),
                           static_cast<uint8_t>((header >> 1) & 0x0Fu)});
    }
    return records;
}

inline DatabaseResult ImportMii(std::span<uint8_t> database,
                                std::span<const uint8_t> mii) {
    if (const auto validation = ValidateDatabase(database); !validation) {
        return validation;
    }
    if (const auto validation = ValidateMii(mii); !validation) {
        return validation;
    }

    const uint32_t createId = ReadBigEndian32(mii, 0x18);
    std::size_t emptyOffset = database.size();
    for (std::size_t slot = 0; slot < kMaximumMiiSlots; ++slot) {
        const std::size_t offset = kMiiBlockOffset + slot * kMiiBlockSize;
        if (offset + kMiiBlockSize > database.size()) {
            break;
        }
        const auto block = database.subspan(offset, kMiiBlockSize);
        if (IsEmptyMii(block)) {
            if (emptyOffset == database.size()) {
                emptyOffset = offset;
            }
        } else if (ReadBigEndian32(block, 0x18) == createId) {
            return {false, "That Mii is already in the database."};
        }
    }
    if (emptyOffset == database.size()) {
        return {false, "The Mii database has no empty slots."};
    }
    std::copy(mii.begin(), mii.end(), database.begin() + emptyOffset);
    UpdateDatabaseCrc(database);
    return {true, {}};
}

inline DatabaseResult ValidateUtf16BigEndianName(
        std::span<const uint8_t> utf16BigEndianName) {
    if (utf16BigEndianName.empty() ||
        utf16BigEndianName.size() > kMiiNameByteSize ||
        (utf16BigEndianName.size() % 2) != 0) {
        return {false, "A player name must contain 1 to 10 characters."};
    }
    for (std::size_t offset = 0; offset < utf16BigEndianName.size(); offset += 2) {
        const uint16_t unit = ReadBigEndian16(utf16BigEndianName, offset);
        if (unit == 0 || unit < 0x20u ||
            (unit >= 0xDC00u && unit <= 0xDFFFu)) {
            return {false, "The player name contains an unsupported character."};
        }
        if (unit >= 0xD800u && unit <= 0xDBFFu) {
            if (offset + 3 >= utf16BigEndianName.size()) {
                return {false,
                        "The player name contains an unsupported character."};
            }
            const uint16_t low = ReadBigEndian16(utf16BigEndianName, offset + 2);
            if (low < 0xDC00u || low > 0xDFFFu) {
                return {false,
                        "The player name contains an unsupported character."};
            }
            offset += 2;
        }
    }
    return {true, {}};
}

inline DatabaseResult RenameMii(std::span<uint8_t> database,
                                std::size_t slot,
                                std::span<const uint8_t> utf16BigEndianName) {
    if (const auto validation = ValidateDatabase(database); !validation) {
        return validation;
    }
    if (slot >= kMaximumMiiSlots) {
        return {false, "The selected Mii slot is invalid."};
    }
    if (const auto validation =
            ValidateUtf16BigEndianName(utf16BigEndianName); !validation) {
        return validation;
    }

    const std::size_t recordOffset = kMiiBlockOffset + slot * kMiiBlockSize;
    if (recordOffset + kMiiBlockSize > database.size() ||
        IsEmptyMii(database.subspan(recordOffset, kMiiBlockSize))) {
        return {false, "The selected Mii no longer exists."};
    }
    auto name = database.subspan(recordOffset + 0x02, kMiiNameByteSize);
    std::fill(name.begin(), name.end(), 0);
    std::copy(utf16BigEndianName.begin(), utf16BigEndianName.end(), name.begin());
    UpdateDatabaseCrc(database);
    return {true, {}};
}

inline DatabaseResult RemoveMii(std::span<uint8_t> database,
                                std::size_t slot) {
    if (const auto validation = ValidateDatabase(database); !validation) {
        return validation;
    }
    const auto records = ListMiis(database);
    if (records.size() <= 1) {
        return {false, "KartPad keeps at least one Mii available for the game."};
    }
    if (slot >= kMaximumMiiSlots) {
        return {false, "The selected Mii slot is invalid."};
    }
    const std::size_t offset = kMiiBlockOffset + slot * kMiiBlockSize;
    if (offset + kMiiBlockSize > database.size() ||
        IsEmptyMii(database.subspan(offset, kMiiBlockSize))) {
        return {false, "The selected Mii no longer exists."};
    }
    std::fill(database.begin() + offset,
              database.begin() + offset + kMiiBlockSize, 0);
    UpdateDatabaseCrc(database);
    return {true, {}};
}

} // namespace kartpad::mii
