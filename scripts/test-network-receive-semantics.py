#!/usr/bin/env python3
"""Exercise the actual prepared receive/retry block with scripted and loopback IO."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runtime", type=Path)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
source = (args.runtime / "src/hle/net/network_socket.cpp").read_text()
case = source[source.index("case IOCTLV_SO_RECVFROM:"):]
start = case.index("        int ret = 0;")
end = case.index("        if (s->type == SOCK_DGRAM && LocalWfcTraceEnabled())", start)
block = case[start:end]
assert "StreamReceiveWaitMilliseconds" in block
assert "nativeErr = ret < 0 ? NativeLastError() : 0;" in block

prefix = r'''
#include <kartpad/network/blocking_stream_wait.h>
#include <arpa/inet.h>
#include <cassert>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <poll.h>
#include <fcntl.h>
#include <thread>
#include <unistd.h>
#include <vector>
struct Outcome { int count, error; };
std::vector<Outcome> outcomes;
int calls, waits, waitedMs, lastError, addressWrites, readyAfter;
bool realIO = false;
struct WiiSocket { int native = -1; int type = SOCK_STREAM; bool nonblocking = false; };
struct Output { unsigned address, size; };
int NativeLastError() { return realIO ? errno : lastError; }
bool IsWouldBlockError(int e) { return e == EAGAIN || e == EWOULDBLOCK; }
int SocketResult(int count) { return count; }
int SocketErrorResult(int e) { return -e; } // Check selected error, not Wii errno mapping.
void WriteWiiSockAddr(unsigned, const sockaddr_in& from, unsigned) {
  ++addressWrites;
  assert(from.sin_port == htons(1234));
}
int Receive(int fd, void* data, int size, int flags, sockaddr* from, socklen_t* len) {
  ++calls;
  if (realIO) return ::recvfrom(fd, data, size, flags, from, len);
  assert(size > 0 && !outcomes.empty());
  auto result = outcomes.front(); outcomes.erase(outcomes.begin());
  lastError = result.error;
  if (from) reinterpret_cast<sockaddr_in*>(from)->sin_port = htons(1234);
  return result.count;
}
bool WaitForReadable(int fd, int ms) {
  ++waits; waitedMs = ms;
  if (!realIO) return ms > 0 && readyAfter >= 0 && readyAfter <= ms;
  pollfd p{fd, POLLIN, 0};
  return ::poll(&p, 1, ms) > 0;
}
void Reset(std::initializer_list<Outcome> o, int delay = 0) {
  outcomes = o; calls = waits = addressWrites = 0; waitedMs = -1;
  readyAfter = delay; lastError = 0;
}
int Run(WiiSocket* s, bool forceNonBlock = false, bool withAddress = false) {
  char storage[128]{}; char* data = storage; unsigned flags = 0;
  std::vector<Output> out{{0, sizeof(storage)}, {1, 8}};
  sockaddr_in from{}; socklen_t fromLen = sizeof(from);
  sockaddr* fromPtr = withAddress ? reinterpret_cast<sockaddr*>(&from) : nullptr;
#define recvfrom Receive
'''
suffix = r'''
#undef recvfrom
  return result;
}
int main() {
  WiiSocket socket;
  Reset({{7, 0}}); assert(Run(&socket) == 7 && calls == 1 && waits == 0);
  Reset({{1, 0}}); assert(Run(&socket) == 1 && calls == 1 && waits == 0);
  Reset({{-1, EAGAIN}, {4, 0}}, 800);
  assert(Run(&socket) == 4 && calls == 2 && waitedMs >= 800);
  Reset({{-1, EAGAIN}, {4, 0}}, 4900); assert(Run(&socket) == 4);
  Reset({{-1, EAGAIN}}, 5100); assert(Run(&socket) == -EAGAIN && calls == 1);
  Reset({{0, 0}}); assert(Run(&socket) == 0 && waits == 0);
  Reset({{-1, EAGAIN}, {0, 0}}); assert(Run(&socket) == 0 && calls == 2);
  Reset({{-1, EAGAIN}, {-1, ECONNRESET}});
  assert(Run(&socket) == -ECONNRESET && calls == 2);
  Reset({{-1, ECONNRESET}}); assert(Run(&socket) == -ECONNRESET && waits == 0);
  for (bool forced : {false, true}) for (bool nonblocking : {false, true}) {
    if (!forced && !nonblocking) continue;
    socket.nonblocking = nonblocking;
    Reset({{-1, EAGAIN}}, 800);
    assert(Run(&socket, forced) == -EAGAIN && waitedMs == 0 && calls == 1);
  }
  socket.nonblocking = false;
  Reset({{-1, EAGAIN}}, 800);
  assert(Run(&socket, false, true) == -EAGAIN && waits == 0);
  Reset({{5, 0}}); assert(Run(&socket, false, true) == 5 && addressWrites == 1);
  socket.type = SOCK_DGRAM;
  Reset({{-1, EAGAIN}}); assert(Run(&socket) == -EAGAIN && waits == 0);
  Reset({{2, 0}}); assert(Run(&socket, false, true) == 2 && addressWrites == 1);

  // Real TCP loopback response beyond the old proposed 500 ms Android window.
  int listener = ::socket(AF_INET, SOCK_STREAM, 0); assert(listener >= 0);
  sockaddr_in address{}; address.sin_family = AF_INET;
  address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
  assert(::bind(listener, reinterpret_cast<sockaddr*>(&address), sizeof(address)) == 0);
  socklen_t addressLen = sizeof(address);
  assert(::getsockname(listener, reinterpret_cast<sockaddr*>(&address), &addressLen) == 0);
  assert(::listen(listener, 1) == 0);
  int client = ::socket(AF_INET, SOCK_STREAM, 0); assert(client >= 0);
  assert(::connect(client, reinterpret_cast<sockaddr*>(&address), sizeof(address)) == 0);
  int server = ::accept(listener, nullptr, nullptr); assert(server >= 0);
  socket = WiiSocket{client, SOCK_STREAM, false};
  // Host sockets are nonblocking even when the Wii socket is logically blocking.
  assert(::fcntl(client, F_SETFL, O_NONBLOCK) == 0);
  Reset({}); realIO = true;
  std::thread writer([server] {
    std::this_thread::sleep_for(std::chrono::milliseconds(800));
    assert(::send(server, "test", 4, 0) == 4);
  });
  assert(Run(&socket) == 4 && calls == 2);
  writer.join(); ::close(server); ::close(client); ::close(listener);
}
'''
with tempfile.TemporaryDirectory(prefix="kartpad-recv-semantics-") as temp:
    path = Path(temp)
    cpp = path / "receive.cpp"
    cpp.write_text(prefix + block + suffix)
    binary = path / "receive"
    subprocess.run(["clang++", "-std=c++20", "-Wall", "-Wextra", "-Werror", "-pthread",
                    "-I", str(repo / "runtime/include"), str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print("PASS: prepared receive retry/errors/nonblocking/UDP and delayed loopback response")
