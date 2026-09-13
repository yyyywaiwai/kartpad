package dev.kartpad.android

import android.util.AtomicFile
import java.io.File
import java.io.IOException

/** Read fresh because the chooser and paused menu run in different processes. */
internal object KartPadPreferredGame {
    const val ASK = "ask"
    val values = arrayOf(ASK, "base", "retro_rewind")
    val labels = arrayOf("Ask Every Time", "Original Mario Kart Wii", "Retro Rewind")
    private fun file(filesDir: File) = AtomicFile(File(filesDir, "KartPad/PreferredGame"))

    fun read(filesDir: File): String = runCatching {
        file(filesDir).openRead().use { stream ->
            val bytes = ByteArray(32)
            val count = stream.read(bytes)
            if (count < 0) ASK else String(bytes, 0, count, Charsets.UTF_8)
                .takeIf { it in values } ?: ASK
        }
    }.getOrDefault(ASK)

    fun write(filesDir: File, value: String) {
        require(value in values)
        val destination = file(filesDir)
        destination.baseFile.parentFile?.mkdirs()
        val output = destination.startWrite()
        try {
            output.write(value.toByteArray(Charsets.UTF_8))
            destination.finishWrite(output)
        } catch (error: Throwable) {
            destination.failWrite(output)
            throw error
        }
        // AtomicFile may log publication failures instead of throwing them.
        if (read(filesDir) != value) throw IOException("Preferred game could not be saved")
    }
}

/** One automatic choice per fresh chooser, never when deliberately returning to it. */
internal class KartPadPreferredLaunch(var consumed: Boolean = false) {
    fun choose(preferred: String, gameReady: Boolean, retroReady: Boolean,
               explicitChoice: String?): String? {
        if (consumed) return null
        consumed = true
        if (explicitChoice != null || !gameReady) return null
        return when (preferred) {
            "base" -> preferred
            "retro_rewind" -> preferred.takeIf { retroReady }
            else -> null
        }
    }
}
