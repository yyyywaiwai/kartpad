package dev.kartpad.android

import java.io.InputStream

/** Returns at most limit+1 bytes so callers can reject an oversized input. */
internal fun InputStream.readBytesBounded(limit: Int): ByteArray {
    require(limit in 0 until Int.MAX_VALUE)
    val buffer = ByteArray(limit + 1)
    var count = 0
    while (count < buffer.size) {
        val read = read(buffer, count, buffer.size - count)
        if (read < 0) break
        check(read > 0) { "Input stopped making progress." }
        count += read
    }
    return buffer.copyOf(count)
}
