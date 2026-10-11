#!/usr/bin/env python3
"""Verify that opt-in WFC diagnostics never include protocol payload fields."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runtime", type=Path)
args = parser.parse_args()
source = (args.runtime / "src/hle/net/network_socket.cpp").read_text()
start = source.index("static void TraceWfcTcp(")
end = source.index("\nstatic uint32_t HostOrderIpv4", start)
prefix = r'''
#include <cstdlib>
#include <cstring>
#include <string>
#include <string_view>
#include <cstdint>
#include <cstdarg>
#include <cassert>
#include <cerrno>
constexpr int SOCK_STREAM=1;
struct WiiSocket { int type=SOCK_STREAM; uint16_t peerPort=29900; };
std::string output;
bool IsWouldBlockError(int e) { return e==EAGAIN; }
void NetFail(const char* fmt, ...) { char b[512]; va_list a; va_start(a,fmt);vsnprintf(b,sizeof(b),fmt,a);va_end(a);output+=b; }
'''
suffix = r'''


int main(){WiiSocket s;
const std::string payload="\\login\\authtoken\\PRIVATE_SECRET\\profileid\\123456\\final\\";
unsetenv("KARTPAD_WFC_TRACE");TraceWfcTcp("send",1,&s,payload.data(),payload.size(),0);assert(output.empty());
setenv("KARTPAD_WFC_TRACE","1",1);TraceWfcTcp("send",1,&s,payload.data(),payload.size(),0);
assert(output.find("command=\\login\\")!=std::string::npos);assert(output.find("PRIVATE_SECRET")==std::string::npos);assert(output.find("123456")==std::string::npos);
output.clear();TraceWfcTcp("recv",1,&s,nullptr,-1,EAGAIN);assert(output.empty());
TraceWfcTcp("recv",1,&s,nullptr,0,0);assert(output.find("bytes=0")!=std::string::npos);
output.clear();s.peerPort=443;TraceWfcTcp("send",1,&s,payload.data(),payload.size(),0);assert(output.empty());}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-wfc-trace-") as temporary:
    path = Path(temporary)
    (path / "test.cpp").write_text(prefix + source[start:end] + suffix)
    subprocess.run(["clang++", "-std=c++20", "-fsanitize=address,undefined", "-g",
                    str(path / "test.cpp"), "-o", str(path / "test")], check=True)
    subprocess.run([str(path / "test")], check=True)
print("PASS: WFC trace opt-in, payload exclusion, would-block filtering and EOF")
