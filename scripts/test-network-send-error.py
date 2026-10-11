#!/usr/bin/env python3
"""Check actual send-result handling when diagnostics overwrite native errno."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
for platform in ('android','ios','macos','tvos'):
    source=(root/'vendor/runtimes'/platform/'runtime/src/hle/net/network_socket.cpp').read_text()
    section=source[source.index('case IOCTLV_SO_SENDTO:'):source.index('case IOCTLV_SO_RECVFROM:')]
    start=section.index('        const int ret = sendto(')
    end=section.index('        if (patchedWrite &&',start)
    block=section[start:end]
    prefix=r'''
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cinttypes>
#include <sys/socket.h>
#include <netinet/in.h>
int outcome=-1, nativeError=ECONNRESET;
int NativeLastError() { return errno; }
int SocketResult(int r) { return r>=0?r:-errno; }
int SocketErrorResult(int e) { return -e; }
int FakeSend(int,const char*,int,int,sockaddr*,socklen_t) { errno=nativeError; return outcome; }
void TraceWfcTcp(const char*,unsigned,void*,const char*,int,int) { errno=ENOENT; }
bool LocalWfcTraceEnabled() { return true; }
bool ShouldTracePacket(uint64_t) { return true; }
void LocalWfcTrace(const char*,...) { errno=ENOENT; }
uint32_t HostOrderIpv4(sockaddr_in) { return 0; }
struct Socket { int native=0, type=SOCK_STREAM; uint64_t localTestUdpSendCalls=0; } socketState;
int Run(int type) {
 auto* s=&socketState; s->type=type;
 const unsigned fd=0,sendSize=4,flags=0;
 const uint8_t sendData[4]={}; sockaddr_in dest{};
 sockaddr* destPtr=nullptr; socklen_t destLen=0;
#define sendto FakeSend
'''
    suffix=r'''
#undef sendto
 return result;
}
int main() {
 for(int type : {SOCK_STREAM,SOCK_DGRAM}) {
  for(int e : {ECONNRESET,EAGAIN,EPIPE}) {
   outcome=-1; nativeError=e; assert(Run(type)==-e);
  }
  outcome=0; assert(Run(type)==0);
  outcome=2; assert(Run(type)==2);
  outcome=4; assert(Run(type)==4);
 }
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp); (path/'test.cpp').write_text('#include <initializer_list>\n'+prefix+block+suffix)
        subprocess.run(['clang++','-std=c++20','-fsanitize=address,undefined',str(path/'test.cpp'),'-o',str(path/'test')],check=True)
        result=subprocess.run([str(path/'test')],capture_output=True,text=True)
        print(platform, 'PASS' if result.returncode==0 else 'FAIL: captured socket error replaced by diagnostic errno',flush=True)
        if result.returncode: raise SystemExit(1)
