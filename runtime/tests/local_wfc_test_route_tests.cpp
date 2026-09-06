#include "kartpad/network/local_wfc_test_route.h"

#include <cstdlib>
#include <iostream>
#include <optional>
#include <string>

namespace {

class EnvironmentGuard {
public:
    explicit EnvironmentGuard(const char* name) : name_(name) {
        if (const char* value = std::getenv(name)) {
            original_ = value;
        }
    }

    ~EnvironmentGuard() {
        if (original_) {
            setenv(name_.c_str(), original_->c_str(), 1);
        } else {
            unsetenv(name_.c_str());
        }
    }

private:
    std::string name_;
    std::optional<std::string> original_;
};

bool Check(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
    }
    return condition;
}

}  // namespace

int main() {
    using namespace KartPad::Network;
    EnvironmentGuard hostGuard(kLocalWfcHostEnvironment);
    EnvironmentGuard portGuard(kLocalWfcHttpPortEnvironment);
    EnvironmentGuard traceGuard(kLocalWfcTraceEnvironment);
    unsetenv(kLocalWfcHostEnvironment);
    unsetenv(kLocalWfcHttpPortEnvironment);
    unsetenv(kLocalWfcTraceEnvironment);

    bool ok = true;
    ok &= Check(RouteLocalWfcHost(true, "nas.example.net") == "nas.example.net",
                "host is unchanged without an explicit test route");
    ok &= Check(RouteLocalWfcPort(true, 443) == 443,
                "port is unchanged without an explicit test route");
    ok &= Check(!LocalWfcTraceEnabled(true),
                "trace is disabled by default");

    setenv(kLocalWfcHostEnvironment, "127.0.0.1", 1);
    setenv(kLocalWfcHttpPortEnvironment, "18080", 1);
    ok &= Check(RouteLocalWfcHost(false, "nas.example.net") == "nas.example.net",
                "vanilla product ignores local RWFC routing");
    ok &= Check(RouteLocalWfcHost(true, "nas.example.net") == "127.0.0.1",
                "Retro Rewind product routes DNS to the explicit local host");
    ok &= Check(RouteLocalWfcPort(true, 80) == 18080,
                "local HTTP route maps port 80");
    ok &= Check(RouteLocalWfcPort(true, 443) == 18080,
                "local plaintext-WFC route maps logical port 443");
    ok &= Check(RouteLocalWfcPort(true, 29900) == 29900,
                "GameSpy ports remain unchanged");
    ok &= Check(LocalWfcTraceEnabled(true),
                "the legacy host route still enables trace diagnostics");

    // The trace-only switch must not affect resolver or port routing.
    unsetenv(kLocalWfcHostEnvironment);
    unsetenv(kLocalWfcHttpPortEnvironment);
    setenv(kLocalWfcTraceEnvironment, "1", 1);
    ok &= Check(LocalWfcTraceEnabled(true),
                "trace-only switch enables diagnostics for Retro Rewind");
    ok &= Check(!LocalWfcTraceEnabled(false),
                "vanilla product ignores trace-only switch");
    ok &= Check(RouteLocalWfcHost(true, "nas.example.net") == "nas.example.net",
                "trace-only switch leaves host destination unchanged");
    ok &= Check(RouteLocalWfcPort(true, 443) == 443,
                "trace-only switch leaves HTTP port unchanged");

    setenv(kLocalWfcTraceEnvironment, "true", 1);
    ok &= Check(LocalWfcTraceEnabled(true), "literal true enables trace");
    setenv(kLocalWfcTraceEnvironment, "on", 1);
    ok &= Check(LocalWfcTraceEnabled(true), "literal on enables trace");
    setenv(kLocalWfcTraceEnvironment, "true-ish", 1);
    ok &= Check(!LocalWfcTraceEnabled(true), "malformed true value is rejected");
    setenv(kLocalWfcTraceEnvironment, "0", 1);
    ok &= Check(!LocalWfcTraceEnabled(true), "zero disables trace");

    setenv(kLocalWfcHostEnvironment, "127.0.0.1", 1);
    setenv(kLocalWfcHttpPortEnvironment, "0", 1);
    ok &= Check(RouteLocalWfcPort(true, 80) == 80, "zero port is rejected");
    setenv(kLocalWfcHttpPortEnvironment, "65536", 1);
    ok &= Check(RouteLocalWfcPort(true, 80) == 80, "oversized port is rejected");
    setenv(kLocalWfcHttpPortEnvironment, "18080x", 1);
    ok &= Check(RouteLocalWfcPort(true, 80) == 80, "partial port parse is rejected");

    return ok ? 0 : 1;
}
