#include "kartpad/network/private_wfc.h"
#include <iostream>

int main() {
    using namespace KartPad::Network;
    unsigned failures = 0;
    auto check = [&](bool value, const char *message) {
        if (!value) { std::cerr << message << '\n'; ++failures; }
    };
    for (const char *host : {"127.0.0.1", "192.168.1.10", "wfc.example.org", "wfc-host.local"})
        check(ValidPrivateWfcHost(host), "valid private address rejected");
    for (const char *host : {"", "http://localhost", "localhost:80", "host/path", "host name",
                            "-host", "host-", "a..b", ".host", "host.", "user@host", "host\n"})
        check(!ValidPrivateWfcHost(host), "invalid private address accepted");
    unsetenv(kPrivateWfcHostEnvironment);
    check(RoutePrivateWfcHost("naswii.nintendowifi.net") == "naswii.nintendowifi.net",
          "default server unexpectedly redirected");
    setenv(kPrivateWfcHostEnvironment, "192.168.1.10", 1);
    for (const char *host : {"naswii.nintendowifi.net", "mariokartwii.ms19.gs.nintendowifi.net",
                            "nas.play.rwfc.net", "NAS.PLAY.RWFC.NET."}) {
        check(RoutePrivateWfcHost(host) == "192.168.1.10", "Wii service not routed");
        check(PrivateWfcRoutesHost(host), "private Wii service not classified for legacy transport");
    }
    for (const char *host : {"update.rwfc.net", "cdn.update.rwfc.net", "example.com",
                            "play.rwfc.net.example.org", "evilnintendowifi.net", "192.168.1.11"})
        check(RoutePrivateWfcHost(host) == host, "unrelated DNS or peer address redirected");
    setenv(kPrivateWfcHostEnvironment, "https://invalid/path", 1);
    check(!PrivateWfcRoutesHost("naswii.nintendowifi.net"), "invalid persisted route enabled");
    unsetenv(kPrivateWfcHostEnvironment);
    return failures ? 1 : 0;
}
