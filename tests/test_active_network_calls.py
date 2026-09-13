"""Active-wait diagnosis: fixed clock boundaries, capacity, reuse, and a blocked receive."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ActiveNetworkCallsTest(unittest.TestCase):
    def test_active_waits_are_observable_before_receive_returns(self):
        compiler = shutil.which("clang++") or shutil.which("g++")
        self.assertIsNotNone(compiler, "C++ compiler is required")
        source = r'''
#include <kartpad/diagnostics/active_calls.h>
#include <cassert>
#include <atomic>
#include <thread>
#include <sys/socket.h>
#include <unistd.h>
using namespace kartpad::diagnostics;
int main() {
  ActiveCalls tracker;
  auto id = tracker.begin(NetworkOperation::SocketVector, 12, 100);
  assert(tracker.sample(99).count == 0);
  assert(tracker.sample(1'000'000'099).count == 0);
  auto first = tracker.sample(1'000'000'100);
  assert(first.count == 1 && first.overdue[0].command == 12 && first.remaining == 31);
  assert(tracker.sample(9'000'000'000).count == 0);
  tracker.end(id);
  auto replacement = tracker.begin(NetworkOperation::SslVector, 3, 0);
  tracker.end(id); // An old token must not erase a reused slot.
  assert(tracker.sample(2'000'000'000).count == 1);
  tracker.end(replacement);
  for (int i = 0; i < 40; ++i) {
    auto next = tracker.begin(NetworkOperation::SocketScalar, 0, 0);
    auto result = tracker.sample(2'000'000'000);
    assert(result.count == (i < 30 ? 1u : 0u));
    tracker.end(next);
  }
  ActiveCalls full;
  uint64_t tokens[8];
  for (auto& token : tokens) token = full.begin(NetworkOperation::SocketScalar, 1, 0);
  assert(full.begin(NetworkOperation::SocketScalar, 1, 0) == 0);
  auto snapshot = full.sample(2'000'000'000);
  assert(snapshot.count == 8 && snapshot.untracked == 1);
  for (auto token : tokens) full.end(token);
  assert(full.sample(4'000'000'000).count == 0);

  // Local socket only: remote peer withholds data until observation has occurred.
  ActiveCalls blocked;
  int sockets[2]; assert(socketpair(AF_UNIX, SOCK_STREAM, 0, sockets) == 0);
  std::atomic<bool> entered{false}, completed{false};
  std::thread receiver([&] {
    auto token = blocked.begin(NetworkOperation::SocketVector, 12, 0);
    entered.store(true);
    char byte{}; assert(recv(sockets[0], &byte, 1, 0) == 1 && byte == 'x');
    blocked.end(token);
    completed.store(true);
  });
  while (!entered.load()) std::this_thread::yield();
  assert(!completed.load());
  auto waiting = blocked.sample(2'000'000'000);
  assert(waiting.count == 1 && !completed.load());
  assert(send(sockets[1], "x", 1, 0) == 1);
  receiver.join();
  assert(completed.load() && blocked.sample(3'000'000'000).count == 0);
  close(sockets[0]); close(sockets[1]);
}
'''
        with tempfile.TemporaryDirectory() as temp:
            cpp = pathlib.Path(temp) / "test.cpp"
            exe = pathlib.Path(temp) / "test"
            cpp.write_text(source)
            subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                            "-pthread", "-fsanitize=address,undefined", "-I",
                            str(ROOT / "runtime/include"), str(cpp), "-o", str(exe)], check=True)
            subprocess.run([str(exe)], check=True, timeout=15)


if __name__ == "__main__":
    unittest.main()
