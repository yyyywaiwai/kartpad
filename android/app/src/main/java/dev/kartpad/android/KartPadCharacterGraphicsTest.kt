package dev.kartpad.android

import android.content.Context
import android.system.Os
import android.util.AtomicFile
import java.io.File

/** Experimental character indexing comparison. Configure only before native startup. */
internal object KartPadCharacterGraphicsTest {
    enum class Mode(val stored: String, val label: String, val environment: String?) {
        NORMAL("normal", "Normal", null),
        ORIGINAL("original", "Compare: original indexing", "0"),
        COMPATIBILITY("compatibility", "Compare: compatibility indexing", "1"),
    }

    @Volatile var active = Mode.NORMAL
        private set

    private var configured = false

    private fun setting(context: Context) = AtomicFile(File(context.filesDir, "KartPad/CharacterGraphicsTest"))

    fun mode(context: Context): Mode = runCatching {
        val text = setting(context).openRead().use { input ->
            val bytes = ByteArray(32)
            val length = input.read(bytes)
            if (length < 0 || input.read() != -1) return@use ""
            String(bytes, 0, length, Charsets.UTF_8)
        }
        Mode.entries.firstOrNull { it.stored == text } ?: Mode.NORMAL
    }.getOrDefault(Mode.NORMAL)

    fun setMode(context: Context, mode: Mode): Boolean = runCatching {
        val file = setting(context)
        file.baseFile.parentFile?.mkdirs()
        val output = file.startWrite()
        try {
            output.write(mode.stored.toByteArray(Charsets.UTF_8))
            output.fd.sync()
            file.finishWrite(output)
            check(mode(context) == mode) { "Setting publication failed" }
        } catch (error: Exception) {
            file.failWrite(output)
            throw error
        }
    }.isSuccess

    @Synchronized
    fun configure(context: Context) {
        if (configured) return
        active = mode(context)
        val value = active.environment
        if (value == null) Os.unsetenv("KARTPAD_RENDERER_CONST_PNMTX")
        else Os.setenv("KARTPAD_RENDERER_CONST_PNMTX", value, true)
        configured = true
    }
}
