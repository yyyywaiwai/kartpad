package dev.kartpad.android

import java.io.File

/** Single-worker, bounded numeric telemetry; never reads game data or system logs. */
internal class KartPadHealthJournal(private val file: File, private val limit: Long = 1024 * 1024) {
    fun append(line: String) {
        val bytes = (line + "\n").toByteArray(Charsets.UTF_8)
        require(bytes.size <= limit)
        file.parentFile?.mkdirs()
        // Start a new bounded window when full. Readers may safely reach EOF
        // during an explicit export; the file is never renamed underneath them.
        if (file.length() + bytes.size > limit) file.writeBytes(bytes)
        else file.appendBytes(bytes)
    }
}
