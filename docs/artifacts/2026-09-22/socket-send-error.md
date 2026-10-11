# Preserve socket send errors across diagnostics

The shared IOCTLV_SO_SENDTO path saved NativeLastError immediately after sendto,
then invoked optional TCP/UDP diagnostics before calling SocketResult(ret).
SocketResult read the ambient native error again. Logging is allowed to change
errno (or the Windows last-error state), so a failed send could report an unrelated
error to the guest. The receive path already used its captured error.

All four maintained runtimes now use SocketErrorResult(hostError) when sendto
fails. Successful and partial writes still use SocketResult(ret); patched NAS
write accounting remains unchanged. No retry policy, timeout or protocol changes
are included.

The host regression compiles the actual send-result section with scripted socket
results and diagnostics that deliberately replace errno with ENOENT. The original
Android section failed. Corrected Android, iOS, macOS and tvOS sections pass under
ASan/UBSan for ECONNRESET, EAGAIN and EPIPE, plus zero, partial and complete writes
on stream and datagram sockets. The iOS receive/loopback and WFC trace privacy
tests also pass. This is a demonstrated error-propagation defect, not proof that
diagnostics caused the owner's WFC94020 session failure.

Run `python3 scripts/test-network-send-error.py`; it is also in shared-runtime CI.
Private devices were not accessed. RC1's existing binaries and source archive
remain exact historical validation controls and do not contain this correction.
A new clean candidate build and corresponding source delivery are required before
promoting the corrected code. The WFC publication hold remains in force.
