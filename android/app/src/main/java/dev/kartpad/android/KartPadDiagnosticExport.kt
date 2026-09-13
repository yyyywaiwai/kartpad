package dev.kartpad.android

import android.content.Context
import android.net.Uri
import java.io.File
import java.io.RandomAccessFile
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** Explicit local export, available even when the game cannot finish booting. */
internal object KartPadDiagnosticExport {
    private const val MAX_FILE_BYTES = 4L * 1024 * 1024
    private const val MAX_FILES = 12

    fun write(context: Context, destination: Uri) {
        val root = File(context.filesDir, "KartPad/Logs").canonicalFile
        // Only bounded tails of runtime text logs, never game data, NAND or config.
        val files = if (root.isDirectory) root.walkTopDown().maxDepth(3)
            .filter { it.isFile && it.extension in setOf("log", "txt") }
            .filter { it.canonicalPath.startsWith(root.path + File.separator) }
            .sortedByDescending { it.lastModified() }.take(MAX_FILES).toList() else emptyList()
        val output = context.contentResolver.openOutputStream(destination, "w")
            ?: error("The chosen destination could not be opened.")
        ZipOutputStream(output.buffered()).use { zip ->
            zip.putNextEntry(ZipEntry("README.txt"))
            zip.write(buildString {
                appendLine("Private KartPad runtime diagnostics; review before sharing.")
                appendLine("Version: ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})")
                appendLine("Device: ${android.os.Build.MANUFACTURER} ${android.os.Build.MODEL}")
                appendLine("API: ${android.os.Build.VERSION.SDK_INT}")
                appendLine("Retro Rewind: ${RetroRewindRelease.VERSION}")
                appendLine("Native KartPadPerf/CPU/GPU metrics and android-health.log use elapsed_ms since boot.")
                appendLine("report-context.json describes the export time, not the source/version of every older log.")
                appendLine("Context renderer_validation is null outside the game process; renderer_validation_configured is the saved next-launch setting.")
                appendLine("Its version_match_only status does not revalidate Retro code or prove online compatibility.")
                appendLine("KartPadNetWait observes unfinished calls >=1 second; KartPadNetStall describes completed slow calls.")
                appendLine("Network wait operation codes: 0=socket scalar, 1=socket vector, 2=SSL vector. call is a process-local correlation token.")
                appendLine("Wait sampling stops in the background and has a 32-record cap; missing records do not rule out networking.")
                appendLine("Health samples run every 10 seconds while the game activity is resumed.")
                appendLine("An in-game pause menu may still render; these samples do not identify race state.")
                appendLine("Health history is bounded to 1 MiB; null means unavailable, not zero.")
                appendLine("Thermal status and headroom are OS signals, not proof of a single bottleneck.")
                appendLine("process-exits.json contains up to eight OS exit records for KartPad (Android 11+).")
                appendLine("Exit timestamps use Unix epoch milliseconds, not elapsed_ms. History may be incomplete.")
                appendLine("Exit version/profile are null for older builds; current export version is not their version.")
                appendLine("A user-requested exit can be a manual stop; missing records do not prove no crash.")
                appendLine("Memory values are last OS samples in KiB, not peak use. No system traces are exported.")
                appendLine("renderer_validation in health samples identifies opt-in game-renderer checks.")
                appendLine("Compare the same scene with validation off/on; validation can reduce performance.")
                appendLine("For renderer warnings/errors, open Logs/<test-session>/console.log and share only relevant reviewed lines.")
                appendLine("android-health.log contains settings/performance samples, not the main renderer error log.")
                appendLine("process-exits.json is intentionally outside Logs; a matching unexpected-exit entry is useful only if the app closed.")
                appendLine("If there are no renderer errors, report whether the image changed with validation off/on.")
                appendLine("Each log contains at most its last $MAX_FILE_BYTES bytes.")
                appendLine("Log files: ${files.size}")
            }.toByteArray())
            zip.closeEntry()
            zip.putNextEntry(ZipEntry("report-context.json"))
            zip.write(KartPadReportContext.snapshot(context, null).toString(2).toByteArray())
            zip.closeEntry()
            zip.putNextEntry(ZipEntry("process-exits.json"))
            zip.write(KartPadExitDiagnostics.snapshot(context).toByteArray())
            zip.closeEntry()
            val buffer = ByteArray(32 * 1024)
            for (file in files) {
                zip.putNextEntry(ZipEntry("Logs/" + file.relativeTo(root).invariantSeparatorsPath))
                RandomAccessFile(file, "r").use { input ->
                    val size = input.length()
                    input.seek(maxOf(0, size - MAX_FILE_BYTES))
                    var remaining = minOf(size, MAX_FILE_BYTES)
                    while (remaining > 0) {
                        val count = input.read(buffer, 0, minOf(buffer.size.toLong(), remaining).toInt())
                        if (count < 0) break
                        zip.write(buffer, 0, count)
                        remaining -= count
                    }
                }
                zip.closeEntry()
            }
        }
    }
}
