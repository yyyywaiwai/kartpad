#pragma once

#include <charconv>
#include <cstdint>
#include <cstdlib>
#include <optional>
#include <string>
#include <string_view>

namespace KartPad::Network {

inline constexpr char kLocalWfcHostEnvironment[] = "KARTPAD_WFC_TEST_HOST";
inline constexpr char kLocalWfcHttpPortEnvironment[] = "KARTPAD_WFC_TEST_HTTP_PORT";
inline constexpr char kLocalWfcTraceEnvironment[] = "KARTPAD_WFC_TEST_TRACE";

inline std::optional<uint16_t> ParseLocalWfcPort(const char* text) {
    if (!text || *text == '\0') {
        return std::nullopt;
    }
    unsigned value = 0;
    const char* const end = text + std::char_traits<char>::length(text);
    const auto parsed = std::from_chars(text, end, value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end || value == 0 || value > 65535) {
        return std::nullopt;
    }
    return static_cast<uint16_t>(value);
}

inline bool LocalWfcRouteEnabled(bool retroRewindActive) {
    const char* const host = std::getenv(kLocalWfcHostEnvironment);
    return retroRewindActive && host && *host != '\0';
}

// Keep diagnostics independent from destination routing.  The explicit value
// check avoids enabling packet metadata logging for an accidentally inherited
// or malformed environment value.
inline bool LocalWfcTraceRequested() {
    const char* const value = std::getenv(kLocalWfcTraceEnvironment);
    if (!value) {
        return false;
    }
    const std::string_view text(value);
    return text == "1" || text == "true" || text == "on";
}

inline bool LocalWfcTraceEnabled(bool retroRewindActive) {
    return retroRewindActive &&
        (LocalWfcRouteEnabled(retroRewindActive) || LocalWfcTraceRequested());
}

inline std::string RouteLocalWfcHost(bool retroRewindActive, std::string_view requestedHost) {
    if (!LocalWfcRouteEnabled(retroRewindActive)) {
        return std::string(requestedHost);
    }
    return std::string(std::getenv(kLocalWfcHostEnvironment));
}

inline uint16_t RouteLocalWfcPort(bool retroRewindActive, uint16_t requestedPort) {
    if (!LocalWfcRouteEnabled(retroRewindActive) ||
        (requestedPort != 80 && requestedPort != 443)) {
        return requestedPort;
    }
    const auto overridePort = ParseLocalWfcPort(std::getenv(kLocalWfcHttpPortEnvironment));
    return overridePort.value_or(requestedPort);
}

}  // namespace KartPad::Network
