# Receive retry regression coverage

The released receive policy is unchanged: logically blocking TCP may wait up to 5 seconds; explicit or socket-level nonblocking receives do not wait. This change adds regression coverage, not an online performance fix.

Run `python3 scripts/test-network-receive-semantics.py <prepared-runtime>` against a runtime prepared by the Android build scripts. The harness extracts the real `IOCTLV_SO_RECVFROM` retry/result block and compiles it with the repository wait-policy header. Scripted IO tests cover partial data, delayed replies, timeout, EOF before/after retry, refreshed retry errors, fatal errors, both nonblocking controls, source-address output, and UDP. A real TCP loopback test delivers a response after 800 ms.

Validation on 2026-09-13 passed against the retained Android code-80 prepared source (`615225b`). The receive patch and policy header are unchanged between that revision and this branch base (`975ed07`). Two isolated negative controls failed as expected: removing retry error refresh failed the ECONNRESET assertion; reducing the blocking window to 500 ms rejected the delayed response.

The harness substitutes host IO and result mapping for deterministic checks. It does not validate Wii errno translation, Android scheduling, public WFC servers, gameplay pacing, or reconnect behavior. An 800 ms loopback response is a regression gate for the receive window, not an online acceptance test.
